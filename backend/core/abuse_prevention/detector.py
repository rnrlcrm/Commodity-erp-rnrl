"""
Abuse Detection System

Main abuse detector that coordinates pattern matching, bot detection,
and suspicious behavior tracking.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from fastapi import Request

from backend.core.abuse_prevention.patterns import PatternMatcher
from backend.core.abuse_prevention.ip_reputation import IPReputationChecker

logger = logging.getLogger(__name__)


class AbuseType(str, Enum):
    """Types of abuse events"""
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    PATH_TRAVERSAL = "path_traversal"
    COMMAND_INJECTION = "command_injection"
    LDAP_INJECTION = "ldap_injection"
    XXE = "xxe"
    BOT_DETECTED = "bot_detected"
    BLOCKED_IP = "blocked_ip"
    CREDENTIAL_STUFFING = "credential_stuffing"
    EXCESSIVE_FAILED_LOGINS = "excessive_failed_logins"
    SUSPICIOUS_BEHAVIOR = "suspicious_behavior"


@dataclass
class AbuseEvent:
    """
    Abuse event detected.
    
    Attributes:
        abuse_type: Type of abuse
        severity: Low, medium, high
        ip_address: Source IP
        user_id: User ID if authenticated
        endpoint: Endpoint accessed
        details: Additional details
        timestamp: When detected
        should_block: Whether to block immediately
    """
    abuse_type: AbuseType
    severity: str  # low, medium, high
    ip_address: str
    user_id: Optional[str] = None
    endpoint: Optional[str] = None
    details: Optional[str] = None
    timestamp: float = 0
    should_block: bool = False
    
    def __post_init__(self):
        if self.timestamp == 0:
            self.timestamp = time.time()


class AbuseDetector:
    """
    Main abuse detection system.
    
    Coordinates:
    - Pattern matching (SQL injection, XSS, etc.)
    - Bot detection
    - IP reputation checking
    - Failed login tracking
    - Suspicious behavior detection
    
    Usage:
        detector = AbuseDetector(redis_client)
        event = await detector.check_request(request)
        if event and event.should_block:
            raise HTTPException(403, "Forbidden")
    """
    
    def __init__(self, redis_client=None):
        """
        Initialize abuse detector.
        
        Args:
            redis_client: Redis client for state tracking
        """
        self.redis = redis_client
        self.pattern_matcher = PatternMatcher()
        self.ip_checker = IPReputationChecker(redis_client)
    
    async def check_request(self, request: Request) -> Optional[AbuseEvent]:
        """
        Check request for abuse patterns.
        
        Checks:
        1. IP blocklist
        2. Bot user agent
        3. Malicious patterns in query params
        4. Malicious patterns in request body
        
        Args:
            request: FastAPI request object
            
        Returns:
            AbuseEvent if abuse detected, None otherwise
        """
        ip_address = self._get_client_ip(request)
        user = getattr(request.state, "user", None)
        user_id = str(user.id) if user else None
        endpoint = request.url.path
        
        # Check if IP is blocked
        is_blocked, block_reason = await self.ip_checker.is_blocked(ip_address)
        if is_blocked:
            return AbuseEvent(
                abuse_type=AbuseType.BLOCKED_IP,
                severity="high",
                ip_address=ip_address,
                user_id=user_id,
                endpoint=endpoint,
                details=f"IP blocked: {block_reason}",
                should_block=True,
            )
        
        # Check for bot user agent
        user_agent = request.headers.get("user-agent", "")
        is_bot, bot_type = self.ip_checker.is_bot(user_agent)
        if is_bot:
            # Log but don't block (some legitimate bots exist)
            event = AbuseEvent(
                abuse_type=AbuseType.BOT_DETECTED,
                severity="low",
                ip_address=ip_address,
                user_id=user_id,
                endpoint=endpoint,
                details=f"Bot detected: {bot_type}",
                should_block=False,  # Don't auto-block bots
            )
            await self._log_abuse_event(event)
        
        # Check query parameters for malicious patterns
        query_string = str(request.url.query)
        if query_string:
            patterns = self.pattern_matcher.scan_all(query_string)
            if patterns:
                event = AbuseEvent(
                    abuse_type=self._classify_pattern(patterns[0]),
                    severity="high",
                    ip_address=ip_address,
                    user_id=user_id,
                    endpoint=endpoint,
                    details=f"Malicious pattern in query: {patterns[0]}",
                    should_block=True,
                )
                await self._log_abuse_event(event)
                await self.ip_checker.increment_abuse_count(ip_address)
                return event
        
        # Check request body for malicious patterns (if applicable)
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # Note: Reading body here requires careful handling
                # In production, integrate with request validation
                # For now, we'll skip body checking to avoid consuming the stream
                pass
            except Exception:
                pass
        
        return None
    
    async def track_failed_login(
        self,
        identifier: str,  # email or mobile
        ip_address: str,
    ) -> Optional[AbuseEvent]:
        """
        Track failed login attempts.
        
        Detects:
        - Credential stuffing (many attempts on same account)
        - Brute force (many attempts from same IP)
        
        Args:
            identifier: Email or mobile number
            ip_address: Source IP
            
        Returns:
            AbuseEvent if threshold exceeded
        """
        if not self.redis:
            return None
        
        # Track per-account failures (credential stuffing)
        account_key = f"failed_login:account:{identifier}"
        pipe = self.redis.pipeline()
        pipe.incr(account_key)
        pipe.expire(account_key, 3600)  # 1 hour window
        results = await pipe.execute()
        account_failures = results[0]
        
        # Track per-IP failures (brute force)
        ip_key = f"failed_login:ip:{ip_address}"
        pipe = self.redis.pipeline()
        pipe.incr(ip_key)
        pipe.expire(ip_key, 3600)  # 1 hour window
        results = await pipe.execute()
        ip_failures = results[0]
        
        # Check thresholds
        if account_failures >= 5:  # 5 failed attempts on same account
            event = AbuseEvent(
                abuse_type=AbuseType.CREDENTIAL_STUFFING,
                severity="high",
                ip_address=ip_address,
                user_id=None,
                endpoint="/auth/login",
                details=f"Credential stuffing: {account_failures} failures on {identifier}",
                should_block=True,
            )
            await self._log_abuse_event(event)
            await self.ip_checker.increment_abuse_count(ip_address)
            return event
        
        if ip_failures >= 20:  # 20 failed attempts from same IP
            event = AbuseEvent(
                abuse_type=AbuseType.EXCESSIVE_FAILED_LOGINS,
                severity="high",
                ip_address=ip_address,
                user_id=None,
                endpoint="/auth/login",
                details=f"Brute force: {ip_failures} failures from IP",
                should_block=True,
            )
            await self._log_abuse_event(event)
            await self.ip_checker.block_ip(
                ip_address,
                f"Auto-blocked: {ip_failures} failed logins",
                ttl_seconds=3600,  # Block for 1 hour
            )
            return event
        
        return None
    
    async def reset_failed_login_count(self, identifier: str) -> None:
        """
        Reset failed login count after successful login.
        
        Args:
            identifier: Email or mobile number
        """
        if not self.redis:
            return
        
        account_key = f"failed_login:account:{identifier}"
        await self.redis.delete(account_key)
    
    def _classify_pattern(self, pattern_description: str) -> AbuseType:
        """Classify detected pattern into AbuseType"""
        if "SQL injection" in pattern_description:
            return AbuseType.SQL_INJECTION
        elif "XSS" in pattern_description:
            return AbuseType.XSS
        elif "Path traversal" in pattern_description:
            return AbuseType.PATH_TRAVERSAL
        elif "Command injection" in pattern_description:
            return AbuseType.COMMAND_INJECTION
        elif "LDAP" in pattern_description:
            return AbuseType.LDAP_INJECTION
        elif "XXE" in pattern_description:
            return AbuseType.XXE
        else:
            return AbuseType.SUSPICIOUS_BEHAVIOR
    
    async def _log_abuse_event(self, event: AbuseEvent) -> None:
        """
        Log abuse event to Redis and system logger.
        
        Stores in Redis for analytics/reporting.
        """
        logger.warning(
            f"Abuse detected: {event.abuse_type} from {event.ip_address} "
            f"({event.severity} severity) - {event.details}"
        )
        
        if not self.redis:
            return
        
        # Store event in Redis (for reporting)
        event_key = f"abuse_event:{int(event.timestamp)}:{event.ip_address}"
        event_data = {
            "type": event.abuse_type,
            "severity": event.severity,
            "ip": event.ip_address,
            "user_id": event.user_id or "",
            "endpoint": event.endpoint or "",
            "details": event.details or "",
        }
        
        await self.redis.hset(event_key, mapping=event_data)
        await self.redis.expire(event_key, 2592000)  # Keep for 30 days
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        if request.client:
            return request.client.host
        
        return "unknown"
