"""
Real-time Currency Conversion Service

Provides real-time forex rates with caching for multi-currency reporting.
Supports all major currencies used in global cotton trade.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional
from decimal import Decimal
import httpx
from pydantic import BaseModel


class ExchangeRate(BaseModel):
    """Exchange rate data"""
    base_currency: str
    target_currency: str
    rate: Decimal
    timestamp: datetime
    source: str = "exchangerate-api.com"


class CurrencyConversionService:
    """
    Real-time currency conversion with caching.
    
    Features:
    - Real-time FX rates from exchangerate-api.com
    - In-memory caching (1-hour TTL)
    - Support for 30+ currencies
    - Batch conversion for reporting
    - Fallback to static rates if API fails
    """
    
    # Free API key - replace with paid tier for production
    API_KEY = "demo"  # TODO: Get from environment variable
    API_URL = "https://v6.exchangerate-api.com/v6/{api_key}/latest/{base}"
    
    # Supported currencies (major trading currencies)
    SUPPORTED_CURRENCIES = [
        "USD", "EUR", "GBP", "INR", "CNY", "JPY", "AUD", "CAD",
        "CHF", "HKD", "SGD", "NZD", "KRW", "MXN", "BRL", "ZAR",
        "RUB", "TRY", "THB", "IDR", "MYR", "PHP", "VND", "EGP",
        "PKR", "BDT", "LKR", "AED", "SAR", "QAR", "KWD"
    ]
    
    # Cache: {base_currency: {target: rate, timestamp: ...}}
    _rate_cache: Dict[str, Dict] = {}
    
    # Cache TTL (1 hour)
    CACHE_TTL_SECONDS = 3600
    
    # Fallback static rates (as of 2024 - for offline mode)
    STATIC_RATES = {
        "USD": {
            "EUR": Decimal("0.92"),
            "GBP": Decimal("0.79"),
            "INR": Decimal("83.12"),
            "CNY": Decimal("7.24"),
            "JPY": Decimal("149.50"),
            "AUD": Decimal("1.52"),
            "BDT": Decimal("109.50"),
            "PKR": Decimal("278.00"),
            "AED": Decimal("3.67"),
        }
    }
    
    async def get_rate(
        self,
        base_currency: str,
        target_currency: str,
        use_cache: bool = True
    ) -> ExchangeRate:
        """
        Get exchange rate from base to target currency.
        
        Args:
            base_currency: Base currency code (e.g., USD)
            target_currency: Target currency code (e.g., INR)
            use_cache: Whether to use cached rates
        
        Returns:
            ExchangeRate object with current rate
        
        Raises:
            ValueError: If currency not supported
        """
        base = base_currency.upper()
        target = target_currency.upper()
        
        # Same currency - rate is 1.0
        if base == target:
            return ExchangeRate(
                base_currency=base,
                target_currency=target,
                rate=Decimal("1.0"),
                timestamp=datetime.utcnow(),
                source="identity"
            )
        
        # Validate currencies
        if base not in self.SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported base currency: {base}")
        if target not in self.SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported target currency: {target}")
        
        # Check cache
        if use_cache:
            cached_rate = self._get_cached_rate(base, target)
            if cached_rate:
                return cached_rate
        
        # Fetch from API
        try:
            rate = await self._fetch_rate_from_api(base, target)
            self._cache_rate(base, target, rate)
            return rate
        except Exception as e:
            # Fallback to static rates
            print(f"API fetch failed: {e}. Using static rates.")
            return self._get_static_rate(base, target)
    
    async def convert(
        self,
        amount: Decimal,
        from_currency: str,
        to_currency: str
    ) -> Decimal:
        """
        Convert amount from one currency to another.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency
            to_currency: Target currency
        
        Returns:
            Converted amount
        """
        rate = await self.get_rate(from_currency, to_currency)
        return amount * rate.rate
    
    async def convert_batch(
        self,
        amounts: Dict[str, Decimal],
        target_currency: str
    ) -> Dict[str, Decimal]:
        """
        Convert multiple amounts to target currency.
        
        Args:
            amounts: {currency: amount} dictionary
            target_currency: Currency to convert to
        
        Returns:
            {currency: converted_amount} dictionary
        """
        results = {}
        
        # Convert each amount
        tasks = []
        for currency, amount in amounts.items():
            tasks.append(self.convert(amount, currency, target_currency))
        
        converted_amounts = await asyncio.gather(*tasks)
        
        for i, (currency, _) in enumerate(amounts.items()):
            results[currency] = converted_amounts[i]
        
        return results
    
    def get_multi_currency_summary(
        self,
        amounts: Dict[str, Decimal],
        converted_amounts: Dict[str, Decimal],
        target_currency: str
    ) -> Dict:
        """
        Generate multi-currency summary for reporting.
        
        Args:
            amounts: Original amounts by currency
            converted_amounts: Converted amounts
            target_currency: Target currency
        
        Returns:
            Summary with total and breakdown
        """
        total = sum(converted_amounts.values())
        
        breakdown = []
        for currency, original_amount in amounts.items():
            converted = converted_amounts[currency]
            breakdown.append({
                "currency": currency,
                "original_amount": float(original_amount),
                "converted_amount": float(converted),
                "percentage": float((converted / total * 100) if total > 0 else 0)
            })
        
        return {
            "total_amount": float(total),
            "target_currency": target_currency,
            "breakdown": breakdown,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _get_cached_rate(self, base: str, target: str) -> Optional[ExchangeRate]:
        """Get rate from cache if fresh"""
        if base not in self._rate_cache:
            return None
        
        cache_entry = self._rate_cache[base].get(target)
        if not cache_entry:
            return None
        
        # Check if cache is still valid
        age = (datetime.utcnow() - cache_entry["timestamp"]).total_seconds()
        if age > self.CACHE_TTL_SECONDS:
            return None
        
        return ExchangeRate(
            base_currency=base,
            target_currency=target,
            rate=cache_entry["rate"],
            timestamp=cache_entry["timestamp"],
            source="cache"
        )
    
    def _cache_rate(self, base: str, target: str, rate: ExchangeRate):
        """Cache exchange rate"""
        if base not in self._rate_cache:
            self._rate_cache[base] = {}
        
        self._rate_cache[base][target] = {
            "rate": rate.rate,
            "timestamp": rate.timestamp
        }
    
    async def _fetch_rate_from_api(self, base: str, target: str) -> ExchangeRate:
        """
        Fetch rate from exchangerate-api.com
        
        Note: Free tier has 1500 requests/month limit.
        For production, upgrade to paid tier or use Redis caching.
        """
        url = self.API_URL.format(api_key=self.API_KEY, base=base)
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("result") != "success":
                raise Exception(f"API error: {data.get('error-type')}")
            
            rates = data.get("conversion_rates", {})
            if target not in rates:
                raise ValueError(f"Rate not found for {target}")
            
            return ExchangeRate(
                base_currency=base,
                target_currency=target,
                rate=Decimal(str(rates[target])),
                timestamp=datetime.utcnow(),
                source="exchangerate-api.com"
            )
    
    def _get_static_rate(self, base: str, target: str) -> ExchangeRate:
        """Fallback to static rates"""
        if base in self.STATIC_RATES and target in self.STATIC_RATES[base]:
            rate = self.STATIC_RATES[base][target]
        elif base == "INR" and target == "USD":
            # Inverse rate
            rate = Decimal("1") / self.STATIC_RATES["USD"]["INR"]
        else:
            # Cross rate via USD
            try:
                base_to_usd = Decimal("1") / self.STATIC_RATES["USD"][base]
                usd_to_target = self.STATIC_RATES["USD"][target]
                rate = base_to_usd * usd_to_target
            except KeyError:
                # Default fallback
                rate = Decimal("1.0")
        
        return ExchangeRate(
            base_currency=base,
            target_currency=target,
            rate=rate,
            timestamp=datetime.utcnow(),
            source="static_fallback"
        )
    
    def clear_cache(self):
        """Clear all cached rates"""
        self._rate_cache.clear()
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        total_entries = sum(len(rates) for rates in self._rate_cache.values())
        currencies_cached = len(self._rate_cache)
        
        return {
            "total_entries": total_entries,
            "currencies_cached": currencies_cached,
            "cache_ttl_seconds": self.CACHE_TTL_SECONDS,
            "supported_currencies": len(self.SUPPORTED_CURRENCIES)
        }
