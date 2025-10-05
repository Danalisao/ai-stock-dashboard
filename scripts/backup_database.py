#!/usr/bin/env python3
"""
💾 Database Backup Script
Automated database backup and cleanup
Run via cron: 0 2 * * * (2 AM daily)
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import shutil
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.utils import load_config, setup_logging


class DatabaseBackup:
    """Database backup manager"""
    
    def __init__(self):
        """Initialize backup manager"""
        self.config = load_config()
        setup_logging(self.config.get('logging', {}))
        self.logger = logging.getLogger(__name__)
        
        # Paths
        db_config = self.config.get('database', {})
        self.db_path = Path(db_config.get('path', './data/stock_data.db'))
        self.backup_path = Path(db_config.get('backup_path', './data/backups'))
        
        # Settings
        self.max_backups = db_config.get('max_backups', 30)
        
        # Create backup directory
        self.backup_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("Database Backup Manager initialized")
    
    def run(self):
        """Run complete backup process"""
        self.logger.info("=" * 60)
        self.logger.info("💾 Starting Database Backup")
        self.logger.info(f"Timestamp: {datetime.now()}")
        self.logger.info("=" * 60)
        
        try:
            # Check if database exists
            if not self.db_path.exists():
                self.logger.warning(f"❌ Database not found: {self.db_path}")
                return
            
            # Create backup
            backup_file = self._create_backup()
            
            if backup_file:
                self.logger.info(f"✅ Backup created: {backup_file.name}")
                
                # Verify backup
                if self._verify_backup(backup_file):
                    self.logger.info("✅ Backup verified successfully")
                else:
                    self.logger.error("❌ Backup verification failed!")
                    return
                
                # Cleanup old backups
                self._cleanup_old_backups()
                
                # Display summary
                self._display_summary()
                
                self.logger.info("=" * 60)
                self.logger.info("✅ Backup Completed Successfully")
                self.logger.info("=" * 60)
            else:
                self.logger.error("❌ Backup creation failed")
            
        except Exception as e:
            self.logger.critical(f"💥 Backup failed: {e}", exc_info=True)
    
    def _create_backup(self):
        """Create database backup"""
        try:
            # Generate backup filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = self.backup_path / f"stock_data_backup_{timestamp}.db"
            
            # Copy database file
            self.logger.info(f"📋 Copying database...")
            shutil.copy2(self.db_path, backup_file)
            
            # Get file size
            size_mb = backup_file.stat().st_size / (1024 * 1024)
            self.logger.info(f"📦 Backup size: {size_mb:.2f} MB")
            
            return backup_file
            
        except Exception as e:
            self.logger.error(f"Backup creation error: {e}", exc_info=True)
            return None
    
    def _verify_backup(self, backup_file: Path):
        """Verify backup integrity"""
        try:
            # Check file exists and has size
            if not backup_file.exists():
                return False
            
            if backup_file.stat().st_size == 0:
                self.logger.error("Backup file is empty!")
                return False
            
            # Compare sizes (should be similar)
            original_size = self.db_path.stat().st_size
            backup_size = backup_file.stat().st_size
            
            size_diff_pct = abs(original_size - backup_size) / original_size * 100
            
            if size_diff_pct > 10:  # More than 10% difference
                self.logger.warning(f"⚠️ Size difference: {size_diff_pct:.1f}%")
            
            # Try to open with sqlite3 (basic integrity check)
            import sqlite3
            conn = sqlite3.connect(str(backup_file))
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            conn.close()
            
            if result[0] != 'ok':
                self.logger.error(f"Integrity check failed: {result[0]}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Verification error: {e}", exc_info=True)
            return False
    
    def _cleanup_old_backups(self):
        """Remove old backups"""
        try:
            self.logger.info(f"🧹 Cleaning up old backups (keeping {self.max_backups})...")
            
            # Get all backup files
            backup_files = sorted(
                self.backup_path.glob('stock_data_backup_*.db'),
                key=lambda p: p.stat().st_mtime,
                reverse=True  # Newest first
            )
            
            # Remove old backups
            removed_count = 0
            for backup_file in backup_files[self.max_backups:]:
                try:
                    backup_file.unlink()
                    removed_count += 1
                    self.logger.info(f"  🗑️ Removed: {backup_file.name}")
                except Exception as e:
                    self.logger.error(f"  ❌ Could not remove {backup_file.name}: {e}")
            
            if removed_count > 0:
                self.logger.info(f"🗑️ Removed {removed_count} old backups")
            else:
                self.logger.info("✅ No cleanup needed")
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}", exc_info=True)
    
    def _display_summary(self):
        """Display backup summary"""
        try:
            self.logger.info("\n📊 Backup Summary")
            self.logger.info("-" * 60)
            
            # Count backups
            backup_files = list(self.backup_path.glob('stock_data_backup_*.db'))
            total_backups = len(backup_files)
            
            # Calculate total size
            total_size = sum(f.stat().st_size for f in backup_files)
            total_size_mb = total_size / (1024 * 1024)
            
            # Oldest and newest
            if backup_files:
                oldest = min(backup_files, key=lambda p: p.stat().st_mtime)
                newest = max(backup_files, key=lambda p: p.stat().st_mtime)
                
                oldest_date = datetime.fromtimestamp(oldest.stat().st_mtime)
                newest_date = datetime.fromtimestamp(newest.stat().st_mtime)
                
                self.logger.info(f"  Total Backups: {total_backups}")
                self.logger.info(f"  Total Size: {total_size_mb:.2f} MB")
                self.logger.info(f"  Oldest: {oldest_date.strftime('%Y-%m-%d %H:%M')}")
                self.logger.info(f"  Newest: {newest_date.strftime('%Y-%m-%d %H:%M')}")
            else:
                self.logger.info("  No backups found")
            
            self.logger.info("-" * 60)
            
        except Exception as e:
            self.logger.error(f"Summary error: {e}")


def main():
    """Main entry point"""
    backup = DatabaseBackup()
    backup.run()


if __name__ == '__main__':
    main()
