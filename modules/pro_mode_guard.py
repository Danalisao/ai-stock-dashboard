"""
🛡️ Professional Mode Guard
Enforce production-grade safeguards for the trading dashboard.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd


@dataclass
class ValidationResult:
    """Container describing the outcome of a validation step."""

    passed: bool
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "issues": list(dict.fromkeys(self.issues)),  # preserve order, avoid duplicates
            "warnings": list(dict.fromkeys(self.warnings)),
        }

    @classmethod
    def success(cls) -> "ValidationResult":
        return cls(True, [], [])


class ProModeGuard:
    """Centralised professional-mode enforcement for trading operations."""

    def __init__(self, config: Dict[str, Any], db_manager):
        self.config = config
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)

        mode_cfg = config.get("professional_mode", {})
        
        # FORCE professional mode - cannot be disabled
        if not mode_cfg.get("enabled", True) or not mode_cfg.get("force_professional_mode", True):
            raise RuntimeError("This is a professional trading system. Professional mode cannot be disabled.")
            
        self.require_alerts = mode_cfg.get("require_alerts", True)
        self.min_watchlist_size = mode_cfg.get("min_watchlist_size", 25)
        self.max_data_staleness_minutes = mode_cfg.get("max_data_staleness_minutes", 240)
        self.weekend_extension_minutes = mode_cfg.get("weekend_extension_minutes", 2880)
        self.permit_debug_logging = mode_cfg.get("permit_debug_logging", False)

    # ------------------------------------------------------------------
    # High-level readiness
    # ------------------------------------------------------------------
    def ensure_production_ready(self, enforce: bool = True) -> ValidationResult:
        """Run configuration checks and optionally raise on failure."""
        readiness = self._run_readiness_checks()

        for warning in readiness.warnings:
            self.logger.warning("Professional readiness warning: %s", warning)

        if enforce and not readiness.passed:
            combined = "; ".join(readiness.issues)
            raise RuntimeError(f"Professional readiness checks failed: {combined}")

        return readiness

    def _run_readiness_checks(self) -> ValidationResult:
        issues: List[str] = []
        warnings: List[str] = []

        dev_cfg = self.config.get("development", {})
        if dev_cfg.get("mock_data", False):
            issues.append("CRITICAL: Mock data is strictly forbidden in professional trading systems.")
        if dev_cfg.get("test_mode", False):
            issues.append("CRITICAL: Test mode must be disabled for live trading operations.")
        if dev_cfg.get("debug_mode", False):
            issues.append("CRITICAL: Debug mode exposes sensitive trading data and must be disabled.")
            
        # Verify this is configured as production system
        if not dev_cfg.get("production_only", False):
            issues.append("CRITICAL: System must be explicitly configured for production use only.")

        logging_cfg = self.config.get("logging", {})
        log_level = logging_cfg.get("level", "INFO").upper()
        if log_level == "DEBUG" and not self.permit_debug_logging:
            warnings.append("Logging level is DEBUG. Reduce verbosity for production compliance unless required.")

        if self.require_alerts:
            alerts_enabled = self.config.get("alerts", {}).get("enabled", False)
            if not alerts_enabled:
                issues.append("CRITICAL: Professional monitoring requires mandatory alert system activation.")
                
        # Enhanced watchlist requirements
        watchlist_cfg = self.config.get("watchlist", {})
        if isinstance(watchlist_cfg, dict):
            watchlist_symbols = watchlist_cfg.get("stocks", [])
        elif isinstance(watchlist_cfg, list):
            watchlist_symbols = watchlist_cfg
        else:
            watchlist_symbols = []

        if len(watchlist_symbols) < self.min_watchlist_size:
            issues.append(
                f"CRITICAL: Professional trading requires minimum {self.min_watchlist_size} instruments in watchlist "
                f"(current: {len(watchlist_symbols)}). Insufficient diversification compromises signal reliability."
            )

        database_cfg = self.config.get("database", {})
        if not database_cfg or not database_cfg.get("path"):
            issues.append("Database path is undefined; persistent storage is required in professional mode.")

        trading_cfg = self.config.get("trading", {})
        entry_score = trading_cfg.get("entry_score_min", 0)
        if entry_score < 80:
            issues.append(
                f"CRITICAL: Professional trading requires minimum entry score of 80 "
                f"(current: {entry_score}). Low thresholds compromise signal quality."
            )
            
        min_rr = trading_cfg.get("min_risk_reward", 0)
        if min_rr < 2.0:
            issues.append(
                f"CRITICAL: Professional risk management requires minimum 2:1 risk/reward ratio "
                f"(current: {min_rr}). This ensures positive expectancy."
            )

        return ValidationResult(passed=not issues, issues=issues, warnings=warnings)

    # ------------------------------------------------------------------
    # Market data
    # ------------------------------------------------------------------
    def validate_market_data(self, symbol: str, data: Optional[pd.DataFrame]) -> ValidationResult:
        """Ensure market data is live, clean, and suitable for pro analytics."""
        issues: List[str] = []
        warnings: List[str] = []

        if data is None or data.empty:
            return ValidationResult(False, [f"No market data returned for {symbol}."], [])

        index = getattr(data, "index", None)
        if not isinstance(index, pd.DatetimeIndex):
            issues.append(f"Market data for {symbol} lacks a DatetimeIndex; unable to validate recency.")
            return ValidationResult(False, issues, warnings)

        last_ts = pd.Timestamp(index[-1]).tz_localize(None)
        now_utc = pd.Timestamp.utcnow().tz_localize(None)
        staleness = now_utc - last_ts

        allowed_minutes = self.max_data_staleness_minutes
        if now_utc.weekday() >= 5:  # weekend extension
            allowed_minutes += self.weekend_extension_minutes

        if staleness > timedelta(minutes=allowed_minutes):
            issues.append(
                f"CRITICAL: Market data for {symbol} is unacceptably stale ({staleness} old). "
                f"Professional trading requires data fresher than {allowed_minutes} minutes. "
                "Stale data compromises signal accuracy and trade execution."
            )

        if index.has_duplicates:
            issues.append(f"CRITICAL: Market data for {symbol} contains duplicate timestamps. Data integrity violation.")

        close_series = data.get("Close")
        if close_series is None:
            issues.append(f"CRITICAL: Close prices missing for {symbol}. Cannot execute professional analysis.")
        else:
            if close_series.isna().any():
                issues.append(f"CRITICAL: Close prices contain missing values for {symbol}. Data quality failure.")
            if (close_series <= 0).any():
                issues.append(f"CRITICAL: Close prices contain invalid values for {symbol}. Data corruption detected.")

        volume_series = data.get("Volume")
        if volume_series is not None and (volume_series < 0).any():
            issues.append(f"CRITICAL: Negative volume values detected for {symbol}. Data source integrity compromised.")

        return ValidationResult(passed=not issues, issues=issues, warnings=warnings)

    # ------------------------------------------------------------------
    # Portfolio risk
    # ------------------------------------------------------------------
    def validate_portfolio_limits(
        self,
        portfolio_tracker,
        current_prices: Dict[str, float],
    ) -> ValidationResult:
        """Validate portfolio exposure, diversification, and drawdown limits."""
        try:
            risk_report = portfolio_tracker.check_risk_limits(current_prices)
        except Exception as exc:  # pragma: no cover - defensive
            message = f"Portfolio risk checks failed: {exc}"
            self.logger.error(message)
            return ValidationResult(False, [message], [])

        if not risk_report:
            return ValidationResult.success()

        warnings = risk_report.get("warnings", [])
        issues: List[str] = []

        if not risk_report.get("all_checks_passed", True):
            # In professional mode, all risk warnings become critical issues
            critical_issues = []
            for warning in warnings:
                if "position too large" in warning.lower() or "over-invested" in warning.lower():
                    critical_issues.append(f"CRITICAL RISK VIOLATION: {warning}")
                elif "too many positions" in warning.lower():
                    critical_issues.append(f"CRITICAL DIVERSIFICATION FAILURE: {warning}")
                elif "unrealized losses" in warning.lower():
                    critical_issues.append(f"CRITICAL DRAWDOWN ALERT: {warning}")
                else:
                    critical_issues.append(f"RISK MANAGEMENT ALERT: {warning}")
            issues.extend(critical_issues)
            warnings = []

        return ValidationResult(passed=not issues, issues=issues, warnings=warnings)