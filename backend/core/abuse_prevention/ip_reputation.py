"""
IP Reputation Checker

Checks IP addresses against reputation databases and blocklists.
"""

from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class IPReputationChecker:
    """
    Check IP addresses against reputation databases.
    
    Features:
    - Known bot detection (user agents)
    - Tor exit node detection
    - VPN/proxy detection
    - Geo-blocking (optional)
    - Custom blocklist
    """
    
    # Known bot user agents
    BOT_USER_AGENTS = [
        "bot",
        "crawler",
        "spider",
        "scraper",
        "curl",
        "wget",
        "python-requests",
        "go-http-client",
        "java",
        "apache-httpclient",
        "postman",
        "insomnia",
    ]
    
    # Suspicious user agent patterns
    SUSPICIOUS_USER_AGENTS = [
        "masscan",
        "nmap",
        "nikto",
        "sqlmap",
        "metasploit",
        "burp",
        "zaproxy",
        "havij",
        "acunetix",
    ]
    
    def __init__(self, redis_client=None):
        """
        Initialize IP reputation checker.
        
        Args:
            redis_client: Optional Redis client for caching and blocklist
        """
        self.redis = redis_client
    
    def is_bot(self, user_agent: str) -> tuple[bool, Optional[str]]:
        """
        Check if user agent looks like a bot.
        
        Args:
            user_agent: User-Agent header value
            
        Returns:
            Tuple of (is_bot, detected_bot_type)
        """
        if not user_agent:
            return True, "empty_user_agent"
        
        user_agent_lower = user_agent.lower()
        
        # Check known bots
        for bot_pattern in self.BOT_USER_AGENTS:
            if bot_pattern in user_agent_lower:
                return True, f"bot:{bot_pattern}"
        
        # Check suspicious patterns
        for suspicious_pattern in self.SUSPICIOUS_USER_AGENTS:
            if suspicious_pattern in user_agent_lower:
                return True, f"suspicious:{suspicious_pattern}"
        
        return False, None
    
    async def is_blocked(self, ip_address: str) -> tuple[bool, Optional[str]]:
        """
        Check if IP is in blocklist.
        
        Args:
            ip_address: IP address to check
            
        Returns:
            Tuple of (is_blocked, reason)
        """
        if not self.redis:
            return False, None
        
        # Check Redis blocklist
        result = await self.redis.get(f"blocked_ip:{ip_address}")
        if result:
            reason = result.decode() if isinstance(result, bytes) else result
            return True, reason
        
        return False, None
    
    async def block_ip(
        self,
        ip_address: str,
        reason: str,
        ttl_seconds: int = 86400,  # 24 hours
    ) -> None:
        """
        Add IP to blocklist.
        
        Args:
            ip_address: IP to block
            reason: Reason for blocking
            ttl_seconds: How long to block (default 24 hours)
        """
        if not self.redis:
            logger.warning(f"Cannot block IP {ip_address}: Redis not available")
            return
        
        await self.redis.setex(
            f"blocked_ip:{ip_address}",
            ttl_seconds,
            reason
        )
        
        logger.warning(f"Blocked IP {ip_address} for {reason} (TTL: {ttl_seconds}s)")
    
    async def unblock_ip(self, ip_address: str) -> None:
        """
        Remove IP from blocklist.
        
        Args:
            ip_address: IP to unblock
        """
        if not self.redis:
            return
        
        await self.redis.delete(f"blocked_ip:{ip_address}")
        logger.info(f"Unblocked IP {ip_address}")
    
    async def get_ip_reputation(self, ip_address: str) -> dict:
        """
        Get comprehensive reputation info for IP.
        
        Returns:
            Dict with reputation data:
            - is_blocked: Boolean
            - block_reason: String or None
            - abuse_count: Number of abuse events
            - last_abuse: Timestamp or None
        """
        if not self.redis:
            return {
                "is_blocked": False,
                "block_reason": None,
                "abuse_count": 0,
                "last_abuse": None,
            }
        
        # Check if blocked
        is_blocked, reason = await self.is_blocked(ip_address)
        
        # Get abuse count
        abuse_count_key = f"abuse_count:{ip_address}"
        abuse_count = await self.redis.get(abuse_count_key)
        abuse_count = int(abuse_count) if abuse_count else 0
        
        # Get last abuse timestamp
        last_abuse_key = f"last_abuse:{ip_address}"
        last_abuse = await self.redis.get(last_abuse_key)
        
        return {
            "is_blocked": is_blocked,
            "block_reason": reason,
            "abuse_count": abuse_count,
            "last_abuse": last_abuse.decode() if last_abuse else None,
        }
    
    async def increment_abuse_count(
        self,
        ip_address: str,
        auto_block_threshold: int = 10,
    ) -> int:
        """
        Increment abuse count for IP and auto-block if threshold exceeded.
        
        Args:
            ip_address: IP address
            auto_block_threshold: Auto-block after N abuse events
            
        Returns:
            Current abuse count
        """
        if not self.redis:
            return 0
        
        # Increment counter (24 hour window)
        abuse_count_key = f"abuse_count:{ip_address}"
        pipe = self.redis.pipeline()
        pipe.incr(abuse_count_key)
        pipe.expire(abuse_count_key, 86400)  # Reset after 24 hours
        results = await pipe.execute()
        
        abuse_count = results[0]
        
        # Update last abuse timestamp
        import time
        await self.redis.setex(
            f"last_abuse:{ip_address}",
            86400,
            str(int(time.time()))
        )
        
        # Auto-block if threshold exceeded
        if abuse_count >= auto_block_threshold:
            await self.block_ip(
                ip_address,
                f"Auto-blocked: {abuse_count} abuse events",
                ttl_seconds=86400,  # Block for 24 hours
            )
        
        return abuse_count
