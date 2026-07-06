# Phase 0 Bug History & Fixes (Evidence-Based)

## Bug 1: Pytest Namespace Collection Error
- **Bug ID**: B-001
- **Severity**: High
- **Module**: Core/Testing
- **Date**: 2026-07-05
- **Root Cause**: Pytest module resolution failure due to missing `pythonpath`.
- **Files Changed**: `pytest.ini` (created)
- **Commit / Patch**: Added `[pytest] pythonpath = .`
- **Fix Applied**: Injected static python path rules into Pytest configs to resolve the `backend` namespace natively.
- **Regression Test Added**: `pytest` executed against the root directory explicitly asserts resolution.
- **Final Status**: RESOLVED

## Bug 2: Invalid Pydantic Enum Access
- **Bug ID**: B-002
- **Severity**: Medium
- **Module**: `backend.market_data.service`
- **Date**: 2026-07-05
- **Root Cause**: Invalid string-based access to strict Enum classes.
- **Files Changed**: `tests/unit/infrastructure/test_service_access.py`
- **Commit / Patch**: Replaced `Timeframe.ONE_HOUR` with `Timeframe.H1`.
- **Fix Applied**: Enforced strict adherence to Enum members defined in `market_data.models.timeframe`.
- **Regression Test Added**: Execution of `tests/integration/market_data/test_service.py` traps enum malformations.
- **Final Status**: RESOLVED

## Bug 3: Pydantic Model Strict Validation Failure
- **Bug ID**: B-003
- **Severity**: High
- **Module**: `backend.market_data.models.symbol`
- **Date**: 2026-07-05
- **Root Cause**: Model instantiation missed mandatory nested validation rules. Pydantic `ValidationError` blocked instantiation of fixtures.
- **Files Changed**: `tests/unit/infrastructure/test_service_access.py`
- **Commit / Patch**: Replaced `SymbolReference(ticker="AAPL")` with `SymbolReference(symbol="AAPL", exchange=ExchangeReference(code="NASDAQ"))`
- **Fix Applied**: Updated mock payloads to conform completely to V2 schemas.
- **Regression Test Added**: Automated test execution runs model parsing against raw dictionaries.
- **Final Status**: RESOLVED

## Bug 4: Failover Logic Silent Failure
- **Bug ID**: B-004
- **Severity**: Critical
- **Module**: `backend.market_data.provider.manager`
- **Date**: 2026-07-05
- **Root Cause**: Lack of automated verification for exhausted provider fallbacks, risking a generic `ValueError` or `Exception` instead of `AllProvidersFailedException`.
- **Files Changed**: `tests/integration/market_data/test_provider_manager.py`
- **Commit / Patch**: Built `test_execute_with_failover_all_providers_fail()`
- **Fix Applied**: Injected an edge-case test forcing exhaustive iterations to validate proper exception routing.
- **Regression Test Added**: `test_execute_with_failover_all_providers_fail()` is now a strict integration gate.
- **Final Status**: RESOLVED
