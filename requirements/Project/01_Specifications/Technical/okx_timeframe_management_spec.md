# OKX Timeframe Management Technical Specification

## Overview

This document provides the complete technical specification for OKX timeframe management components that enhance the existing Nautilus Trader OKX adapter. These components enable support for custom timeframes, rate limiting, bar aggregation, and rolling data management.

## Table of Contents

1. [OKXTimeframeManager](#1-okxtimeframemanager)
2. [OKXRateLimiter](#2-okxratelimiter)
3. [OKXBarAggregator](#3-okxbaraggregator)
4. [OKXRollingDataManager](#4-okxrollingdatamanager)
5. [Integration Notes](#5-integration-notes)
6. [Performance Considerations](#6-performance-considerations)
7. [Testing Specifications](#7-testing-specifications)

## 1. OKXTimeframeManager

### Purpose
The `OKXTimeframeManager` serves as a bridge between Nautilus `BarType` objects and OKX API timeframe strings. It handles the mapping between different timeframe representations and determines which timeframes require custom aggregation.

### Key Features
- Maps Nautilus BarType to OKX timeframe strings
- Determines which timeframes require custom aggregation
- Provides caching for performance optimization
- Supports all OKX native timeframes and custom aggregations

### Implementation Location
**File**: `nautilus_trader/adapters/okx/enhanced/timeframe_manager.py`

### Class Definition
```python
from typing import Dict, Optional, Tuple
from nautilus_trader.model.data import BarSpecification, BarType
from nautilus_trader.model.enums import BarAggregation, PriceType

class OKXTimeframeManager:
    """
    Manages the mapping between Nautilus BarType objects and OKX API timeframe strings.

    This class provides conversion functions in both directions and determines which
    timeframes require custom aggregation.
    """

    # OKX supported timeframes in seconds
    SUPPORTED_TIMEFRAMES = {
        "1s": 1, "1m": 60, "3m": 180, "5m": 300, "15m": 900,
        "30m": 1800, "1H": 3600, "2H": 7200, "4H": 14400,
        "6H": 21600, "12H": 43200, "1D": 86400, "1W": 604800
    }

    # Mapping from Nautilus aggregation to OKX timeframe prefix
    AGGREGATION_TO_PREFIX = {
        BarAggregation.SECOND: "s",
        BarAggregation.MINUTE: "m",
        BarAggregation.HOUR: "H",
        BarAggregation.DAY: "D",
        BarAggregation.WEEK: "W",
        BarAggregation.MONTH: "M",
    }

    def __init__(self) -> None:
        """Initialize the OKXTimeframeManager."""
        self._bar_type_to_okx_cache: Dict[BarType, str] = {}
        self._requires_aggregation_cache: Dict[BarType, bool] = {}

    def bar_type_to_okx_timeframe(self, bar_type: BarType) -> str:
        """Convert a Nautilus BarType to an OKX API timeframe string."""
        # Implementation details provided in source document

    def okx_timeframe_to_bar_spec(self, timeframe: str, price_type: PriceType = PriceType.LAST) -> BarSpecification:
        """Convert an OKX API timeframe string to a Nautilus BarSpecification."""
        # Implementation details provided in source document

    def requires_custom_aggregation(self, bar_type: BarType) -> bool:
        """Determine if a bar type requires custom aggregation."""
        # Implementation details provided in source document

    def get_aggregation_source(self, bar_type: BarType) -> Tuple[BarType, bool]:
        """Get the source bar type for aggregation and whether aggregation is needed."""
        # Implementation details provided in source document
```

### Validation Requirements
- [ ] Test with standard timeframes (1m, 5m, 1H, 1D)
- [ ] Test with custom timeframes (3s, 5s, 15s, 30s)
- [ ] Verify caching functionality reduces computation time by >90%
- [ ] Test error handling for invalid timeframes

### Acceptance Criteria
- All OKX supported timeframes map correctly
- Custom timeframes return appropriate base timeframe for aggregation
- Caching reduces computation time by >90% for repeated calls
- Invalid timeframes raise appropriate exceptions

## 2. OKXRateLimiter

### Purpose
The `OKXRateLimiter` enforces OKX's API rate limits to prevent request throttling and account suspension. OKX imposes a limit of 20 requests per 2 seconds for market data endpoints.

### Key Features
- Async locking mechanism for concurrent requests
- Exponential backoff for rate limit errors
- Per-endpoint tracking and statistics
- Sliding window algorithm for accurate rate limiting

### Implementation Location
**File**: `nautilus_trader/adapters/okx/enhanced/rate_limiter.py`

### Class Definition
```python
import asyncio
import logging
import time
from typing import Dict, Optional
from datetime import datetime, timedelta

class OKXRateLimiter:
    """
    Enforces OKX API rate limits for market data requests.

    OKX imposes a limit of 20 requests per 2 seconds for market data endpoints.
    This class provides an async locking mechanism to handle concurrent requests
    and implements exponential backoff for rate limit errors.
    """

    def __init__(
        self,
        requests_per_window: int = 20,
        window_seconds: int = 2,
        max_retries: int = 5,
        base_backoff: float = 0.5,
    ) -> None:
        """Initialize the OKXRateLimiter."""
        # Implementation details provided in source document

    async def acquire(self, endpoint: str = "default") -> None:
        """Acquire permission to make an API request, waiting if necessary."""
        # Implementation details provided in source document

    async def execute_with_retry(self, func, *args, endpoint: str = "default", **kwargs):
        """Execute a function with rate limiting and automatic retry on failure."""
        # Implementation details provided in source document

    def get_usage_stats(self) -> Dict[str, Dict[str, int]]:
        """Get current rate limit usage statistics."""
        # Implementation details provided in source document
```

### Validation Requirements
- [ ] Test rate limiting with burst requests
- [ ] Verify exponential backoff behavior
- [ ] Test concurrent request handling
- [ ] Validate per-endpoint tracking

### Acceptance Criteria
- Rate limiter prevents exceeding 20 requests per 2 seconds
- Exponential backoff increases delay appropriately
- Concurrent requests are properly queued
- Usage statistics are accurate

## 3. OKXBarAggregator

### Purpose
The `OKXBarAggregator` aggregates 1-second bars into custom timeframes (3s, 5s, 15s, 30s) that are not natively supported by the OKX API.

### Key Features
- OHLCV aggregation logic for custom timeframes
- Support for partial bar updates
- Timeframe boundary alignment
- Memory-efficient operation

### Implementation Location
**File**: `nautilus_trader/adapters/okx/enhanced/bar_aggregator.py`

### Class Definition
```python
from typing import Dict, List, Any, Optional
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.objects import Price, Quantity

class OKXBarAggregator:
    """Aggregates 1-second bars into custom timeframes."""

    def __init__(self, target_timeframe: str):
        """Initialize the bar aggregator for a specific timeframe."""
        # Implementation details provided in source document

    def add_tick_data(self, timestamp: int, price: float, volume: float) -> Bar | None:
        """Add tick data and return completed bar if ready."""
        # Implementation details provided in source document

    def aggregate_bars(self, source_bars: List[Bar]) -> List[Bar]:
        """Aggregate source bars into target timeframe."""
        # Implementation details provided in source document
```

### Validation Requirements
- [ ] Test aggregation accuracy with known data sets
- [ ] Verify OHLCV calculations are correct
- [ ] Test partial bar handling
- [ ] Validate timeframe boundary alignment

### Acceptance Criteria
- Aggregated bars maintain OHLCV accuracy within 0.01%
- Timeframe boundaries align correctly
- Partial bars are handled without data loss
- Memory usage remains constant during operation

## 4. OKXRollingDataManager

### Purpose
The `OKXRollingDataManager` manages a rolling window of 7,600 bars for any timeframe, providing continuous data availability for trading strategies.

### Key Features
- Maintains exactly 7,600 bars at all times
- Handles historical data initialization
- Real-time bar updates
- Error recovery mechanisms
- Integration with persistence layer

### Implementation Location
**File**: `nautilus_trader/adapters/okx/enhanced/rolling_data_manager.py`

### Class Definition
```python
from typing import Dict, List, Optional
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.adapters.okx.http.client import OKXHttpClient

class OKXRollingDataManager:
    """Manages rolling window of 7,600 bars for any timeframe."""

    def __init__(
        self,
        symbol: str,
        timeframe: str,
        window_size: int = 7600,
        okx_client: OKXHttpClient,
        rate_limiter: OKXRateLimiter,
        bar_aggregator: OKXBarAggregator | None = None,
    ):
        """Initialize the rolling data manager."""
        # Implementation details provided in source document

    async def initialize(self) -> None:
        """Initialize rolling data with historical bars."""
        # Implementation details provided in source document

    async def update_with_new_bar(self, bar: Bar) -> None:
        """Add new bar to rolling window."""
        # Implementation details provided in source document

    def get_bars(self, count: int | None = None) -> List[Bar]:
        """Get bars from rolling window."""
        # Implementation details provided in source document
```

### Validation Requirements
- [ ] Test initialization with historical data
- [ ] Verify rolling window maintains exactly 7,600 bars
- [ ] Test real-time bar updates
- [ ] Validate data persistence and recovery

### Acceptance Criteria
- Rolling window maintains exactly 7,600 bars at all times
- Historical data initialization completes within 30 seconds
- Real-time updates have <100ms latency
- Data recovery works after system restart

## 5. Integration Notes

### Integration with Existing OKX Adapter
The enhanced components integrate with the existing Nautilus Trader OKX adapter as follows:

1. **OKXDataClient Enhancement**: Modified to use the rolling data manager for bar subscriptions and requests
2. **Factory Updates**: Enhanced to create and inject the new components
3. **Configuration Extensions**: New configuration options for enhanced features

### Backward Compatibility
All enhancements maintain backward compatibility with existing OKX adapter functionality. Enhanced features can be enabled/disabled via configuration.

## 6. Performance Considerations

### Memory Usage
- Rolling data manager maintains fixed memory footprint
- Caching optimizes repeated operations
- Cleanup procedures prevent memory leaks

### CPU Usage
- Aggregation only performed when necessary
- Efficient algorithms for timeframe conversion
- Async operations prevent blocking

### Network Usage
- Rate limiting minimizes API calls
- Batched requests where possible
- Intelligent caching reduces redundant requests

## 7. Testing Specifications

### Unit Testing Requirements
- [ ] Test all public methods with valid inputs
- [ ] Test error handling with invalid inputs
- [ ] Test edge cases and boundary conditions
- [ ] Verify performance benchmarks

### Integration Testing Requirements
- [ ] Test integration with existing OKX adapter
- [ ] Test real-time data flow
- [ ] Test error recovery scenarios
- [ ] Validate configuration options

### Performance Testing Requirements
- [ ] Memory usage under sustained load
- [ ] CPU usage during aggregation
- [ ] Network efficiency with rate limiting
- [ ] Latency measurements for real-time updates

This specification provides the foundation for implementing Phase 1 and Phase 2 of the master implementation plan.
