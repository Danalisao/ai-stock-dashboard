"""
🤖 Automated ML Model Training Script
Train ML prediction models for entire watchlist

Usage:
    python scripts/train_ml_models.py
    python scripts/train_ml_models.py --symbols AAPL MSFT GOOGL
    python scripts/train_ml_models.py --horizon 60
"""

import sys
import os
import argparse
import logging
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import yfinance as yf
import pandas as pd
from modules.utils import load_config, setup_logging
from modules.ml_predictor import MLPredictor


def setup_argparse():
    """Setup command line arguments"""
    parser = argparse.ArgumentParser(
        description='Train ML models for stock price prediction'
    )
    parser.add_argument(
        '--symbols',
        nargs='+',
        help='Specific symbols to train (default: use watchlist)',
        default=None
    )
    parser.add_argument(
        '--horizon',
        type=int,
        help='Forecast horizon in days (default: 30)',
        default=30
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force retrain even if models are recent'
    )
    parser.add_argument(
        '--backtest',
        action='store_true',
        help='Run accuracy backtest after training'
    )
    return parser.parse_args()


def get_watchlist(config):
    """Get watchlist from config"""
    watchlist_config = config.get('watchlist', {})
    if isinstance(watchlist_config, dict):
        return watchlist_config.get('stocks', [])
    elif isinstance(watchlist_config, list):
        return watchlist_config
    return []


def train_symbol(ml_predictor, symbol, args, logger):
    """Train models for a single symbol"""
    logger.info(f"\n{'='*60}")
    logger.info(f"Processing: {symbol}")
    logger.info(f"{'='*60}")
    
    try:
        # Check if retraining needed
        if not args.force:
            ml_predictor._load_models(symbol)
            if ml_predictor.is_trained and not ml_predictor.needs_retraining():
                logger.info(f"✅ {symbol} - Models are up to date (trained {ml_predictor.last_training_date.strftime('%Y-%m-%d')})")
                return {'status': 'skipped', 'reason': 'up_to_date'}
        
        # Fetch data
        logger.info(f"📡 Fetching data for {symbol}...")
        lookback_days = ml_predictor.lookback_days + 100
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=f"{lookback_days}d")
        
        if data.empty:
            logger.error(f"❌ {symbol} - No data available")
            return {'status': 'failed', 'error': 'no_data'}
        
        logger.info(f"✅ Retrieved {len(data)} days of data")
        
        # Set forecast horizon
        ml_predictor.forecast_days = args.horizon
        
        # Train models
        logger.info(f"🎯 Training models (forecast: {args.horizon} days)...")
        results = ml_predictor.train_models(data, symbol)
        
        if results['status'] == 'success':
            logger.info(f"✅ {symbol} - Training completed!")
            logger.info(f"   - Training samples: {results['training_samples']}")
            logger.info(f"   - Features: {results['features_count']}")
            logger.info(f"   - Ensemble R²: {results['ensemble_r2']:.4f}")
            
            # Model metrics
            for model_name, metrics in results['individual_metrics'].items():
                logger.info(f"   - {model_name}: R²={metrics['r2']:.4f}, RMSE={metrics['rmse']:.4f}")
            
            # Run backtest if requested
            if args.backtest:
                logger.info(f"📊 Running accuracy backtest for {symbol}...")
                backtest_results = ml_predictor.backtest_predictions(data, symbol)
                
                if backtest_results['status'] == 'success':
                    logger.info(f"✅ Backtest completed:")
                    logger.info(f"   - Direction accuracy: {backtest_results['direction_accuracy_pct']:.1f}%")
                    logger.info(f"   - Mean absolute error: {backtest_results['mean_absolute_error_pct']:.2f}%")
                    logger.info(f"   - CI coverage: {backtest_results['confidence_interval_coverage_pct']:.1f}%")
                else:
                    logger.warning(f"⚠️ Backtest failed: {backtest_results.get('error')}")
            
            return results
        else:
            logger.error(f"❌ {symbol} - Training failed: {results.get('error')}")
            return results
    
    except Exception as e:
        logger.error(f"❌ {symbol} - Exception: {e}")
        return {'status': 'failed', 'error': str(e)}


def main():
    """Main training function"""
    # Parse arguments
    args = setup_argparse()
    
    # Load configuration
    config = load_config()
    setup_logging(config.get('logging', {}))
    logger = logging.getLogger(__name__)
    
    # Banner
    logger.info("\n" + "="*70)
    logger.info("🤖 ML MODEL TRAINING SCRIPT")
    logger.info("="*70)
    logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Forecast horizon: {args.horizon} days")
    logger.info(f"Force retrain: {args.force}")
    logger.info(f"Run backtest: {args.backtest}")
    
    # Initialize ML predictor
    ml_predictor = MLPredictor(config)
    
    # Get symbols to train
    if args.symbols:
        symbols = args.symbols
        logger.info(f"Symbols: {', '.join(symbols)} (user specified)")
    else:
        symbols = get_watchlist(config)
        logger.info(f"Symbols: Using watchlist ({len(symbols)} stocks)")
    
    if not symbols:
        logger.error("❌ No symbols to train")
        return
    
    # Train each symbol
    results = {}
    success_count = 0
    failed_count = 0
    skipped_count = 0
    
    for i, symbol in enumerate(symbols, 1):
        logger.info(f"\n[{i}/{len(symbols)}] Training {symbol}...")
        
        result = train_symbol(ml_predictor, symbol, args, logger)
        results[symbol] = result
        
        if result['status'] == 'success':
            success_count += 1
        elif result['status'] == 'skipped':
            skipped_count += 1
        else:
            failed_count += 1
    
    # Summary
    logger.info("\n" + "="*70)
    logger.info("📊 TRAINING SUMMARY")
    logger.info("="*70)
    logger.info(f"Total symbols: {len(symbols)}")
    logger.info(f"✅ Successful: {success_count}")
    logger.info(f"⏭️  Skipped: {skipped_count}")
    logger.info(f"❌ Failed: {failed_count}")
    
    if failed_count > 0:
        logger.info("\n❌ Failed symbols:")
        for symbol, result in results.items():
            if result['status'] == 'failed':
                logger.info(f"   - {symbol}: {result.get('error', 'unknown error')}")
    
    logger.info(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*70 + "\n")
    
    # Create summary report
    summary_file = f"logs/ml_training_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(summary_file, 'w') as f:
        f.write("ML MODEL TRAINING SUMMARY\n")
        f.write("="*60 + "\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Forecast Horizon: {args.horizon} days\n")
        f.write(f"Force Retrain: {args.force}\n")
        f.write(f"Backtest: {args.backtest}\n\n")
        f.write(f"Total Symbols: {len(symbols)}\n")
        f.write(f"Successful: {success_count}\n")
        f.write(f"Skipped: {skipped_count}\n")
        f.write(f"Failed: {failed_count}\n\n")
        
        f.write("DETAILED RESULTS:\n")
        f.write("-"*60 + "\n")
        for symbol, result in results.items():
            f.write(f"\n{symbol}: {result['status'].upper()}\n")
            if result['status'] == 'success':
                f.write(f"  Training samples: {result['training_samples']}\n")
                f.write(f"  Features: {result['features_count']}\n")
                f.write(f"  Ensemble R²: {result['ensemble_r2']:.4f}\n")
            elif result['status'] == 'failed':
                f.write(f"  Error: {result.get('error', 'unknown')}\n")
    
    logger.info(f"📄 Summary saved to: {summary_file}")


if __name__ == '__main__':
    main()
