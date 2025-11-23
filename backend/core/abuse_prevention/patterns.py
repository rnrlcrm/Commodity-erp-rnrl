"""
Malicious Pattern Detection

Detects common attack patterns in request data.
"""

from __future__ import annotations

import re
from typing import Optional


class MaliciousPatterns:
    """
    Collection of regex patterns for detecting common attacks.
    
    Patterns cover:
    - SQL injection
    - XSS (Cross-Site Scripting)
    - Path traversal
    - Command injection
    - LDAP injection
    - XXE (XML External Entity)
    """
    
    # SQL Injection patterns
    SQL_INJECTION = [
        re.compile(r"(\bUNION\b.*\bSELECT\b)", re.IGNORECASE),
        re.compile(r"(\bSELECT\b.*\bFROM\b.*\bWHERE\b)", re.IGNORECASE),
        re.compile(r"(\bINSERT\b.*\bINTO\b.*\bVALUES\b)", re.IGNORECASE),
        re.compile(r"(\bDELETE\b.*\bFROM\b.*\bWHERE\b)", re.IGNORECASE),
        re.compile(r"(\bDROP\b.*\bTABLE\b)", re.IGNORECASE),
        re.compile(r"(\bEXEC\b|\bEXECUTE\b).*\(", re.IGNORECASE),
        re.compile(r"('|\")(\s)*(OR|AND)(\s)*('|\")?(=|!=|<>)", re.IGNORECASE),
        re.compile(r"('|\")(\s)*;(\s)*(DROP|DELETE|UPDATE)", re.IGNORECASE),
        re.compile(r"--(\s)*$", re.IGNORECASE),  # SQL comments
        re.compile(r"/\*.*\*/", re.IGNORECASE),  # SQL comments
    ]
    
    # XSS patterns
    XSS = [
        re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL),
        re.compile(r"javascript:", re.IGNORECASE),
        re.compile(r"on\w+\s*=", re.IGNORECASE),  # event handlers
        re.compile(r"<iframe", re.IGNORECASE),
        re.compile(r"<embed", re.IGNORECASE),
        re.compile(r"<object", re.IGNORECASE),
        re.compile(r"eval\s*\(", re.IGNORECASE),
        re.compile(r"expression\s*\(", re.IGNORECASE),
        re.compile(r"vbscript:", re.IGNORECASE),
        re.compile(r"<img[^>]*src[^>]*>", re.IGNORECASE),
    ]
    
    # Path traversal
    PATH_TRAVERSAL = [
        re.compile(r"\.\./"),
        re.compile(r"\.\.\\"),
        re.compile(r"%2e%2e/", re.IGNORECASE),
        re.compile(r"%2e%2e\\", re.IGNORECASE),
        re.compile(r"\.\.%2f", re.IGNORECASE),
    ]
    
    # Command injection
    COMMAND_INJECTION = [
        re.compile(r";\s*(ls|cat|wget|curl|rm|chmod)", re.IGNORECASE),
        re.compile(r"\|\s*(ls|cat|wget|curl|rm|chmod)", re.IGNORECASE),
        re.compile(r"&&\s*(ls|cat|wget|curl|rm|chmod)", re.IGNORECASE),
        re.compile(r"`.*`"),  # Backticks
        re.compile(r"\$\(.*\)"),  # Command substitution
    ]
    
    # LDAP injection
    LDAP_INJECTION = [
        re.compile(r"\*\)(\(.*=\*)", re.IGNORECASE),
        re.compile(r"\(\|", re.IGNORECASE),
        re.compile(r"\(&", re.IGNORECASE),
    ]
    
    # XXE (XML External Entity)
    XXE = [
        re.compile(r"<!ENTITY", re.IGNORECASE),
        re.compile(r"<!DOCTYPE.*SYSTEM", re.IGNORECASE | re.DOTALL),
    ]


class PatternMatcher:
    """
    Matches request data against malicious patterns.
    """
    
    def __init__(self):
        self.patterns = MaliciousPatterns()
    
    def detect_sql_injection(self, text: str) -> Optional[str]:
        """
        Check if text contains SQL injection patterns.
        
        Args:
            text: Input text to check
            
        Returns:
            Matched pattern or None
        """
        for pattern in self.patterns.SQL_INJECTION:
            match = pattern.search(text)
            if match:
                return f"SQL injection pattern: {match.group(0)}"
        return None
    
    def detect_xss(self, text: str) -> Optional[str]:
        """
        Check if text contains XSS patterns.
        
        Args:
            text: Input text to check
            
        Returns:
            Matched pattern or None
        """
        for pattern in self.patterns.XSS:
            match = pattern.search(text)
            if match:
                return f"XSS pattern: {match.group(0)[:50]}"  # Limit length
        return None
    
    def detect_path_traversal(self, text: str) -> Optional[str]:
        """
        Check if text contains path traversal patterns.
        
        Args:
            text: Input text to check
            
        Returns:
            Matched pattern or None
        """
        for pattern in self.patterns.PATH_TRAVERSAL:
            match = pattern.search(text)
            if match:
                return f"Path traversal pattern: {match.group(0)}"
        return None
    
    def detect_command_injection(self, text: str) -> Optional[str]:
        """
        Check if text contains command injection patterns.
        
        Args:
            text: Input text to check
            
        Returns:
            Matched pattern or None
        """
        for pattern in self.patterns.COMMAND_INJECTION:
            match = pattern.search(text)
            if match:
                return f"Command injection pattern: {match.group(0)}"
        return None
    
    def detect_ldap_injection(self, text: str) -> Optional[str]:
        """
        Check if text contains LDAP injection patterns.
        
        Args:
            text: Input text to check
            
        Returns:
            Matched pattern or None
        """
        for pattern in self.patterns.LDAP_INJECTION:
            match = pattern.search(text)
            if match:
                return f"LDAP injection pattern: {match.group(0)}"
        return None
    
    def detect_xxe(self, text: str) -> Optional[str]:
        """
        Check if text contains XXE patterns.
        
        Args:
            text: Input text to check
            
        Returns:
            Matched pattern or None
        """
        for pattern in self.patterns.XXE:
            match = pattern.search(text)
            if match:
                return f"XXE pattern: {match.group(0)[:50]}"
        return None
    
    def scan_all(self, text: str) -> list[str]:
        """
        Scan text for all types of malicious patterns.
        
        Args:
            text: Input text to check
            
        Returns:
            List of detected patterns (empty if clean)
        """
        detections = []
        
        if result := self.detect_sql_injection(text):
            detections.append(result)
        
        if result := self.detect_xss(text):
            detections.append(result)
        
        if result := self.detect_path_traversal(text):
            detections.append(result)
        
        if result := self.detect_command_injection(text):
            detections.append(result)
        
        if result := self.detect_ldap_injection(text):
            detections.append(result)
        
        if result := self.detect_xxe(text):
            detections.append(result)
        
        return detections
