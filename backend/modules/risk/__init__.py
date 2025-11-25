"""
Risk Module

Comprehensive risk management system with:
- Credit risk assessment
- Fraud detection (party links, circular trading)
- Role-based restrictions
- ML-based predictions
- Real-time exposure monitoring

Components:
- RiskEngine: Core risk assessment logic
- RiskService: Business logic layer
- MLRiskModel: Machine learning predictions
- Routes: REST API endpoints
- Schemas: Request/response models
"""

from backend.modules.risk.risk_engine import RiskEngine
from backend.modules.risk.risk_service import RiskService
from backend.modules.risk.ml_risk_model import MLRiskModel
from backend.modules.risk.routes import router
from backend.modules.risk import schemas

__version__ = "1.0.0"

__all__ = [
    "RiskEngine",
    "RiskService",
    "MLRiskModel",
    "router",
    "schemas",
]