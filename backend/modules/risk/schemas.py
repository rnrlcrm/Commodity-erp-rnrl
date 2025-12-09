"""
Risk Module - Pydantic Schemas

All request/response schemas for Risk Engine API endpoints.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from backend.modules.common.schemas.responses import ErrorResponse


# =============================================================================
# RISK ASSESSMENT SCHEMAS
# =============================================================================

class RequirementRiskAssessmentRequest(BaseModel):
    """Request to assess requirement risk."""
    requirement_id: UUID = Field(description="Requirement UUID")


class AvailabilityRiskAssessmentRequest(BaseModel):
    """Request to assess availability risk."""
    availability_id: UUID = Field(description="Availability UUID")


class TradeRiskAssessmentRequest(BaseModel):
    """Request to assess bilateral trade risk."""
    requirement_id: UUID = Field(description="Buyer requirement UUID")
    availability_id: UUID = Field(description="Seller availability UUID")
    trade_quantity: Decimal = Field(ge=0, description="Proposed trade quantity")
    trade_price: Decimal = Field(ge=0, description="Proposed unit price")


class PartnerRiskAssessmentRequest(BaseModel):
    """Request to assess counterparty risk."""
    partner_id: UUID = Field(description="Partner UUID")
    partner_type: str = Field(description="BUYER or SELLER")
    
    @field_validator('partner_type')
    @classmethod
    def validate_partner_type(cls, v):
        if v not in ["BUYER", "SELLER", "TRADER"]:
            raise ValueError("partner_type must be BUYER, SELLER, or TRADER")
        return v


class RiskAssessmentResponse(BaseModel):
    """Generic risk assessment response."""
    status: str = Field(description="PASS, WARN, or FAIL")
    score: int = Field(ge=0, le=100, description="Risk score (0-100)")
    risk_factors: List[str] = Field(default_factory=list, description="Identified risk factors")
    recommended_action: str = Field(description="Recommended action")
    assessment_timestamp: datetime = Field(description="When assessment was performed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "PASS",
                "score": 85,
                "risk_factors": [],
                "recommended_action": "APPROVE: Low risk trade",
                "assessment_timestamp": "2025-11-25T10:30:00Z"
            }
        }


class TradeRiskAssessmentResponse(BaseModel):
    """Bilateral trade risk assessment response."""
    overall_status: str = Field(description="PASS, WARN, or FAIL")
    combined_score: int = Field(ge=0, le=100, description="Combined risk score")
    buyer_score: int = Field(ge=0, le=100, description="Buyer risk score")
    seller_score: int = Field(ge=0, le=100, description="Seller risk score")
    internal_trade_blocked: bool = Field(description="Whether same-branch trade blocked")
    party_links_detected: bool = Field(default=False, description="Related parties detected")
    party_links_severity: Optional[str] = Field(None, description="BLOCK, WARN, or PASS")
    party_links_violations: List[str] = Field(default_factory=list, description="Party link issues")
    risk_factors: List[str] = Field(default_factory=list, description="All risk factors")
    recommended_action: str = Field(description="Final recommendation")
    assessment_timestamp: datetime = Field(description="Assessment timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "overall_status": "PASS",
                "combined_score": 82,
                "buyer_score": 85,
                "seller_score": 79,
                "internal_trade_blocked": False,
                "party_links_detected": False,
                "party_links_severity": "PASS",
                "party_links_violations": [],
                "risk_factors": [],
                "recommended_action": "APPROVE: Low-risk trade",
                "assessment_timestamp": "2025-11-25T10:30:00Z"
            }
        }


# =============================================================================
# PARTY LINKS VALIDATION SCHEMAS
# =============================================================================

class PartyLinksCheckRequest(BaseModel):
    """Request to check party links between buyer and seller."""
    buyer_id: UUID = Field(description="Buyer partner UUID")
    seller_id: UUID = Field(description="Seller partner UUID")


class PartyLinksCheckResponse(BaseModel):
    """Party links validation response."""
    severity: str = Field(description="BLOCK, WARN, or PASS")
    violations: List[str] = Field(default_factory=list, description="Detected violations")
    recommendation: str = Field(description="Action recommendation")
    details: Dict[str, Any] = Field(default_factory=dict, description="Detailed findings")
    
    class Config:
        json_schema_extra = {
            "example": {
                "severity": "BLOCK",
                "violations": ["Same PAN number"],
                "recommendation": "REJECT: Buyer and seller have same PAN",
                "details": {
                    "pan_match": True,
                    "gst_match": False,
                    "mobile_match": False,
                    "email_domain_match": False
                }
            }
        }


# =============================================================================
# CIRCULAR TRADING VALIDATION SCHEMAS
# =============================================================================

class CircularTradingCheckRequest(BaseModel):
    """Request to check circular trading."""
    partner_id: UUID = Field(description="Partner UUID")
    commodity_id: UUID = Field(description="Commodity UUID")
    transaction_type: str = Field(description="BUY or SELL")
    transaction_date: Optional[datetime] = Field(None, description="Trade date (defaults to today)")
    
    @field_validator('transaction_type')
    @classmethod
    def validate_transaction_type(cls, v):
        if v not in ["BUY", "SELL"]:
            raise ValueError("transaction_type must be BUY or SELL")
        return v


class CircularTradingCheckResponse(BaseModel):
    """Circular trading validation response."""
    blocked: bool = Field(description="Whether circular trading detected")
    reason: str = Field(description="Explanation of result")
    existing_positions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Conflicting positions found"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "blocked": True,
                "reason": "Circular trading detected: Partner has SELL position for same commodity on same day",
                "existing_positions": [
                    {
                        "id": "uuid",
                        "type": "SELL",
                        "commodity": "Cotton",
                        "quantity": 1000,
                        "date": "2025-11-25"
                    }
                ]
            }
        }


# =============================================================================
# ROLE RESTRICTION VALIDATION SCHEMAS
# =============================================================================

class RoleRestrictionCheckRequest(BaseModel):
    """Request to validate partner role restrictions."""
    partner_id: UUID = Field(description="Partner UUID")
    transaction_type: str = Field(description="BUY or SELL")
    
    @field_validator('transaction_type')
    @classmethod
    def validate_transaction_type(cls, v):
        if v not in ["BUY", "SELL"]:
            raise ValueError("transaction_type must be BUY or SELL")
        return v


class RoleRestrictionCheckResponse(BaseModel):
    """Role restriction validation response."""
    allowed: bool = Field(description="Whether transaction allowed for this role")
    reason: str = Field(description="Explanation")
    partner_type: str = Field(description="Partner role: BUYER, SELLER, or TRADER")
    
    class Config:
        json_schema_extra = {
            "example": {
                "allowed": False,
                "reason": "BUYER partners cannot post SELL transactions",
                "partner_type": "BUYER"
            }
        }


# =============================================================================
# ML RISK MODEL SCHEMAS
# =============================================================================

class MLPredictionRequest(BaseModel):
    """Request for ML-based payment default prediction."""
    credit_utilization: float = Field(ge=0, le=100, description="Credit utilization %")
    rating: float = Field(ge=0, le=5, description="Partner rating (0-5)")
    payment_performance: int = Field(ge=0, le=100, description="Payment performance score")
    trade_history_count: int = Field(ge=0, description="Number of completed trades")
    dispute_rate: float = Field(ge=0, le=100, description="Dispute rate %")
    payment_delay_days: int = Field(ge=0, description="Average payment delay (days)")
    avg_trade_value: float = Field(ge=0, description="Average trade value")


class MLPredictionResponse(BaseModel):
    """ML model prediction response."""
    default_probability: float = Field(ge=0, le=100, description="Default probability %")
    risk_level: str = Field(description="LOW, MEDIUM, or HIGH")
    confidence: float = Field(ge=0, le=100, description="Model confidence %")
    contributing_factors: List[str] = Field(default_factory=list, description="Key risk factors")
    recommendation: str = Field(description="Risk-based recommendation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "default_probability": 15.5,
                "risk_level": "MEDIUM",
                "confidence": 85.0,
                "contributing_factors": [
                    "High credit utilization (85.5%)",
                    "Low payment performance (65/100)"
                ],
                "recommendation": "CAUTION: Monitor payment behavior closely"
            }
        }


class MLModelTrainRequest(BaseModel):
    """Request to train ML risk models."""
    use_synthetic_data: bool = Field(
        default=True,
        description="Use synthetic data for training (if no real data)"
    )
    num_samples: int = Field(default=10000, ge=1000, description="Number of synthetic samples")


class MLModelTrainResponse(BaseModel):
    """ML model training response."""
    success: bool = Field(description="Training success status")
    model_name: str = Field(description="Model identifier")
    metrics: Dict[str, float] = Field(description="Training metrics")
    samples_trained: int = Field(description="Number of samples used")
    training_time_seconds: float = Field(description="Training duration")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "model_name": "payment_default_predictor",
                "metrics": {
                    "roc_auc": 0.95,
                    "accuracy": 0.92,
                    "precision": 0.88,
                    "recall": 0.85
                },
                "samples_trained": 10000,
                "training_time_seconds": 12.5
            }
        }


# =============================================================================
# EXPOSURE MONITORING SCHEMAS
# =============================================================================

class ExposureMonitoringRequest(BaseModel):
    """Request to monitor partner exposure."""
    partner_id: UUID = Field(description="Partner UUID")


class ExposureMonitoringResponse(BaseModel):
    """Exposure monitoring response."""
    partner_id: UUID = Field(description="Partner UUID")
    credit_limit: Decimal = Field(description="Total credit limit")
    current_exposure: Decimal = Field(description="Current outstanding exposure")
    available_credit: Decimal = Field(description="Remaining available credit")
    utilization_percent: float = Field(ge=0, le=100, description="Credit utilization %")
    alert_level: str = Field(description="GREEN, YELLOW, or RED")
    alerts: List[str] = Field(default_factory=list, description="Alert messages")
    checked_at: datetime = Field(description="Monitoring timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "partner_id": "uuid",
                "credit_limit": 100000000,
                "current_exposure": 85000000,
                "available_credit": 15000000,
                "utilization_percent": 85.0,
                "alert_level": "YELLOW",
                "alerts": ["Credit utilization above 80%"],
                "checked_at": "2025-11-25T10:30:00Z"
            }
        }


# =============================================================================
# BATCH OPERATION SCHEMAS
# =============================================================================

class BatchRiskAssessmentResponse(BaseModel):
    """Response for batch risk assessments."""
    total_assessed: int = Field(description="Total entities assessed")
    passed: int = Field(description="Count with PASS status")
    warned: int = Field(description="Count with WARN status")
    failed: int = Field(description="Count with FAIL status")
    assessments: List[Dict[str, Any]] = Field(description="Individual assessment results")
    assessed_at: datetime = Field(description="Batch assessment timestamp")


# =============================================================================
# ERROR SCHEMAS
# =============================================================================
# ErrorResponse imported from modules.common.schemas.responses
