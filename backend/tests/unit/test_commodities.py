"""
Unit tests for Commodity Master module.
Tests models, repositories, services, and API endpoints.
"""
import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from backend.modules.settings.commodities.models import (
    Commodity,
    CommodityVariety,
    CommodityParameter,
    SystemCommodityParameter,
    TradeType,
    BargainType,
    PassingTerm,
    WeightmentTerm,
    DeliveryTerm,
    PaymentTerm,
    CommissionStructure,
)
from backend.modules.settings.commodities.repositories import (
    CommodityRepository,
    CommodityVarietyRepository,
    CommodityParameterRepository,
)
from backend.modules.settings.commodities.services import (
    CommodityService,
    CommodityVarietyService,
    CommodityParameterService,
)
from backend.modules.settings.commodities.schemas import (
    CommodityCreate,
    CommodityUpdate,
    CommodityVarietyCreate,
    CommodityParameterCreate,
)


# ============================================================================
# MODEL TESTS
# ============================================================================

class TestCommodityModel:
    """Test Commodity model."""

    def test_create_commodity(self, db_session: Session):
        """Test creating a commodity."""
        commodity = Commodity(
            name="Cotton",
            code="COTTON-001",
            category="raw_material",
            hsn_code="5201",
            unit_of_measure="bales",
            is_active=True
        )
        db_session.add(commodity)
        db_session.commit()
        db_session.refresh(commodity)

        assert commodity.id is not None
        assert commodity.name == "Cotton"
        assert commodity.code == "COTTON-001"
        assert commodity.category == "raw_material"
        assert commodity.is_active is True

    def test_commodity_variety_relationship(self, db_session: Session):
        """Test commodity-variety relationship."""
        commodity = Commodity(
            name="Cotton",
            code="COTTON-001",
            category="raw_material",
            is_active=True
        )
        db_session.add(commodity)
        db_session.commit()

        variety = CommodityVariety(
            commodity_id=commodity.id,
            name="Shankar-6",
            code="S6",
            is_active=True
        )
        db_session.add(variety)
        db_session.commit()
        db_session.refresh(commodity)

        assert len(commodity.varieties) == 1
        assert commodity.varieties[0].name == "Shankar-6"


class TestTradeTypeModel:
    """Test TradeType model."""

    def test_create_trade_type(self, db_session: Session):
        """Test creating a trade type."""
        trade_type = TradeType(
            name="FOB",
            code="FOB",
            description="Free On Board",
            is_active=True
        )
        db_session.add(trade_type)
        db_session.commit()
        db_session.refresh(trade_type)

        assert trade_type.id is not None
        assert trade_type.name == "FOB"
        assert trade_type.code == "FOB"


# ============================================================================
# REPOSITORY TESTS
# ============================================================================

class TestCommodityRepository:
    """Test CommodityRepository."""

    def test_create_commodity(self, db_session: Session):
        """Test repository create method."""
        repo = CommodityRepository(db_session)
        
        commodity_data = {
            "name": "Cotton",
            "code": "COTTON-001",
            "category": "raw_material",
            "is_active": True
        }
        
        commodity = repo.create(commodity_data)
        
        assert commodity.id is not None
        assert commodity.name == "Cotton"

    def test_get_by_code(self, db_session: Session):
        """Test get_by_code method."""
        repo = CommodityRepository(db_session)
        
        commodity = repo.create({
            "name": "Cotton",
            "code": "COTTON-001",
            "category": "raw_material",
            "is_active": True
        })
        
        found = repo.get_by_code("COTTON-001")
        assert found is not None
        assert found.id == commodity.id

    def test_get_by_category(self, db_session: Session):
        """Test get_by_category method."""
        repo = CommodityRepository(db_session)
        
        repo.create({
            "name": "Cotton",
            "code": "COTTON-001",
            "category": "raw_material",
            "is_active": True
        })
        repo.create({
            "name": "Yarn",
            "code": "YARN-001",
            "category": "processed",
            "is_active": True
        })
        
        raw_materials = repo.get_by_category("raw_material")
        assert len(raw_materials) == 1
        assert raw_materials[0].name == "Cotton"


class TestCommodityVarietyRepository:
    """Test CommodityVarietyRepository."""

    def test_get_by_commodity(self, db_session: Session):
        """Test get_by_commodity method."""
        commodity_repo = CommodityRepository(db_session)
        variety_repo = CommodityVarietyRepository(db_session)
        
        commodity = commodity_repo.create({
            "name": "Cotton",
            "code": "COTTON-001",
            "category": "raw_material",
            "is_active": True
        })
        
        variety_repo.create({
            "commodity_id": commodity.id,
            "name": "Shankar-6",
            "code": "S6",
            "is_active": True
        })
        
        varieties = variety_repo.get_by_commodity(commodity.id)
        assert len(varieties) == 1
        assert varieties[0].name == "Shankar-6"


# ============================================================================
# SERVICE TESTS
# ============================================================================

class TestCommodityService:
    """Test CommodityService."""

    def test_create_commodity(self, db_session: Session):
        """Test service create method."""
        service = CommodityService(db_session)
        
        commodity_data = CommodityCreate(
            name="Cotton",
            code="COTTON-001",
            category="raw_material",
            hsn_code="5201",
            unit_of_measure="bales",
            is_active=True
        )
        
        commodity = service.create_commodity(commodity_data)
        
        assert commodity.id is not None
        assert commodity.name == "Cotton"

    def test_update_commodity(self, db_session: Session):
        """Test service update method."""
        service = CommodityService(db_session)
        
        commodity = service.create_commodity(CommodityCreate(
            name="Cotton",
            code="COTTON-001",
            category="raw_material",
            is_active=True
        ))
        
        update_data = CommodityUpdate(
            name="Premium Cotton",
            description="High quality cotton"
        )
        
        updated = service.update_commodity(commodity.id, update_data)
        
        assert updated.name == "Premium Cotton"
        assert updated.description == "High quality cotton"
        assert updated.code == "COTTON-001"  # Unchanged


# ============================================================================
# API ENDPOINT TESTS
# ============================================================================

class TestCommodityAPI:
    """Test Commodity API endpoints."""

    def test_create_commodity_endpoint(self, client: TestClient):
        """Test POST /api/v1/commodities/"""
        response = client.post(
            "/api/v1/commodities/",
            json={
                "name": "Cotton",
                "code": "COTTON-001",
                "category": "raw_material",
                "hsn_code": "5201",
                "unit_of_measure": "bales",
                "is_active": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Cotton"
        assert data["code"] == "COTTON-001"
        assert "id" in data

    def test_get_commodity_endpoint(self, client: TestClient):
        """Test GET /api/v1/commodities/{id}"""
        # Create commodity first
        create_response = client.post(
            "/api/v1/commodities/",
            json={
                "name": "Cotton",
                "code": "COTTON-001",
                "category": "raw_material",
                "is_active": True
            }
        )
        commodity_id = create_response.json()["id"]
        
        # Get commodity
        response = client.get(f"/api/v1/commodities/{commodity_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == commodity_id
        assert data["name"] == "Cotton"

    def test_list_commodities_endpoint(self, client: TestClient):
        """Test GET /api/v1/commodities/"""
        # Create multiple commodities
        client.post(
            "/api/v1/commodities/",
            json={
                "name": "Cotton",
                "code": "COTTON-001",
                "category": "raw_material",
                "is_active": True
            }
        )
        client.post(
            "/api/v1/commodities/",
            json={
                "name": "Yarn",
                "code": "YARN-001",
                "category": "processed",
                "is_active": True
            }
        )
        
        # List all
        response = client.get("/api/v1/commodities/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    def test_update_commodity_endpoint(self, client: TestClient):
        """Test PUT /api/v1/commodities/{id}"""
        # Create commodity
        create_response = client.post(
            "/api/v1/commodities/",
            json={
                "name": "Cotton",
                "code": "COTTON-001",
                "category": "raw_material",
                "is_active": True
            }
        )
        commodity_id = create_response.json()["id"]
        
        # Update commodity
        response = client.put(
            f"/api/v1/commodities/{commodity_id}",
            json={
                "name": "Premium Cotton",
                "description": "High quality"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Premium Cotton"
        assert data["description"] == "High quality"

    def test_delete_commodity_endpoint(self, client: TestClient):
        """Test DELETE /api/v1/commodities/{id}"""
        # Create commodity
        create_response = client.post(
            "/api/v1/commodities/",
            json={
                "name": "Cotton",
                "code": "COTTON-001",
                "category": "raw_material",
                "is_active": True
            }
        )
        commodity_id = create_response.json()["id"]
        
        # Delete commodity
        response = client.delete(f"/api/v1/commodities/{commodity_id}")
        
        assert response.status_code == 200
        
        # Verify deleted
        get_response = client.get(f"/api/v1/commodities/{commodity_id}")
        assert get_response.status_code == 404


class TestCommodityVarietyAPI:
    """Test Commodity Variety API endpoints."""

    def test_create_variety_endpoint(self, client: TestClient):
        """Test POST /api/v1/commodities/{id}/varieties"""
        # Create commodity first
        commodity_response = client.post(
            "/api/v1/commodities/",
            json={
                "name": "Cotton",
                "code": "COTTON-001",
                "category": "raw_material",
                "is_active": True
            }
        )
        commodity_id = commodity_response.json()["id"]
        
        # Create variety
        response = client.post(
            f"/api/v1/commodities/{commodity_id}/varieties",
            json={
                "name": "Shankar-6",
                "code": "S6",
                "is_active": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Shankar-6"
        assert data["commodity_id"] == commodity_id

    def test_list_varieties_endpoint(self, client: TestClient):
        """Test GET /api/v1/commodities/{id}/varieties"""
        # Create commodity
        commodity_response = client.post(
            "/api/v1/commodities/",
            json={
                "name": "Cotton",
                "code": "COTTON-001",
                "category": "raw_material",
                "is_active": True
            }
        )
        commodity_id = commodity_response.json()["id"]
        
        # Create varieties
        client.post(
            f"/api/v1/commodities/{commodity_id}/varieties",
            json={"name": "Shankar-6", "code": "S6", "is_active": True}
        )
        client.post(
            f"/api/v1/commodities/{commodity_id}/varieties",
            json={"name": "MCU-5", "code": "MCU5", "is_active": True}
        )
        
        # List varieties
        response = client.get(f"/api/v1/commodities/{commodity_id}/varieties")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


class TestBulkOperationsAPI:
    """Test bulk import/export API endpoints."""

    def test_bulk_import_validation(self, client: TestClient):
        """Test that bulk import validates data."""
        # This would require creating actual Excel file
        # For now, test that endpoint exists
        response = client.post(
            "/api/v1/commodities/bulk/import",
            files={"file": ("test.xlsx", b"fake_data", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
        
        # Expect validation error, not 404
        assert response.status_code in [400, 422]  # Validation error or unprocessable entity

    def test_export_template_endpoint(self, client: TestClient):
        """Test GET /api/v1/commodities/bulk/template"""
        response = client.get("/api/v1/commodities/bulk/template")
        
        assert response.status_code == 200
        # Should return Excel file
        assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class TestTradeTermsAPI:
    """Test Trade Terms API endpoints."""

    def test_create_trade_type(self, client: TestClient):
        """Test POST /api/v1/commodities/trade-types"""
        response = client.post(
            "/api/v1/commodities/trade-types",
            json={
                "name": "FOB",
                "code": "FOB",
                "description": "Free On Board",
                "is_active": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "FOB"
        assert data["code"] == "FOB"

    def test_list_trade_types(self, client: TestClient):
        """Test GET /api/v1/commodities/trade-types"""
        # Create trade type
        client.post(
            "/api/v1/commodities/trade-types",
            json={
                "name": "FOB",
                "code": "FOB",
                "is_active": True
            }
        )
        
        # List all
        response = client.get("/api/v1/commodities/trade-types")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestCommodityIntegration:
    """Integration tests for complete commodity workflows."""

    def test_full_commodity_workflow(self, client: TestClient):
        """Test creating commodity with varieties and parameters."""
        # 1. Create commodity
        commodity_response = client.post(
            "/api/v1/commodities/",
            json={
                "name": "Cotton",
                "code": "COTTON-001",
                "category": "raw_material",
                "hsn_code": "5201",
                "is_active": True
            }
        )
        assert commodity_response.status_code == 200
        commodity_id = commodity_response.json()["id"]
        
        # 2. Add variety
        variety_response = client.post(
            f"/api/v1/commodities/{commodity_id}/varieties",
            json={
                "name": "Shankar-6",
                "code": "S6",
                "is_active": True
            }
        )
        assert variety_response.status_code == 200
        
        # 3. Add quality parameter
        param_response = client.post(
            f"/api/v1/commodities/{commodity_id}/parameters",
            json={
                "name": "Staple Length",
                "parameter_type": "quality",
                "data_type": "decimal",
                "unit": "mm",
                "min_value": 25.0,
                "max_value": 35.0,
                "is_mandatory": True
            }
        )
        assert param_response.status_code == 200
        
        # 4. Verify commodity with relationships
        get_response = client.get(f"/api/v1/commodities/{commodity_id}")
        assert get_response.status_code == 200
        commodity_data = get_response.json()
        assert commodity_data["name"] == "Cotton"
        
        # 5. List varieties
        varieties_response = client.get(f"/api/v1/commodities/{commodity_id}/varieties")
        assert varieties_response.status_code == 200
        assert len(varieties_response.json()) == 1
        
        # 6. List parameters
        params_response = client.get(f"/api/v1/commodities/{commodity_id}/parameters")
        assert params_response.status_code == 200
        assert len(params_response.json()) == 1
