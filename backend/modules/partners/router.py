"""
Partner API Router

REST API endpoints for business partner onboarding and management.

Endpoints:
- POST /onboarding/start - Start onboarding
- POST /onboarding/{app_id}/documents - Upload documents
- POST /onboarding/{app_id}/submit - Submit for approval
- GET /onboarding/{app_id}/status - Check status
- POST /partners/{partner_id}/approve - Approve partner (manager/director)
- POST /partners/{partner_id}/reject - Reject application
- GET /partners - List all partners
- GET /partners/{partner_id} - Get partner details
- POST /partners/{partner_id}/amendments - Request amendment
- POST /partners/{partner_id}/employees - Add employee
- POST /partners/{partner_id}/kyc/renew - Initiate KYC renewal
- GET /partners/kyc/expiring - Get partners with expiring KYC
"""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.events.emitter import EventEmitter
from backend.db.session import get_db
from backend.modules.partners.enums import PartnerStatus, PartnerType, KYCStatus
from backend.modules.partners.schemas import (
    AmendmentRequest,
    ApprovalDecision,
    BusinessPartnerResponse,
    EmployeeInvite,
    KYCRenewalRequest,
    OnboardingApplicationCreate,
    OnboardingApplicationResponse,
    PartnerDocumentResponse,
    PartnerEmployeeResponse,
    PartnerLocationResponse,
    PartnerVehicleResponse,
    VehicleData,
)
from backend.modules.partners.services import (
    PartnerService,
    ApprovalService,
    KYCRenewalService,
    DocumentProcessingService,
)
from backend.modules.partners.repositories import (
    BusinessPartnerRepository,
    OnboardingApplicationRepository,
    PartnerDocumentRepository,
    PartnerEmployeeRepository,
    PartnerLocationRepository,
    PartnerVehicleRepository,
)

router = APIRouter(prefix="/partners", tags=["partners"])


# ===== DEPENDENCIES =====

def get_current_user_id() -> UUID:
    """Get current user ID from auth context"""
    # TODO: Replace with actual auth dependency
    from uuid import uuid4
    return uuid4()


def get_current_organization_id() -> UUID:
    """Get current organization ID from auth context"""
    # TODO: Replace with actual auth dependency
    from uuid import uuid4
    return uuid4()


def get_event_emitter(db: AsyncSession = Depends(get_db)) -> EventEmitter:
    """Get event emitter instance"""
    return EventEmitter(db)


# ===== ONBOARDING ENDPOINTS =====

@router.post(
    "/onboarding/start",
    response_model=OnboardingApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start Partner Onboarding",
    description="""
    Start partner onboarding process.
    
    Automatically:
    - Verifies GST and fetches business details
    - Geocodes location (auto-verifies if confidence >90%)
    - Creates draft application
    
    Next step: Upload required documents
    """
)
async def start_onboarding(
    data: OnboardingApplicationCreate,
    db: AsyncSession = Depends(get_db),
    event_emitter: EventEmitter = Depends(get_event_emitter),
    user_id: UUID = Depends(get_current_user_id),
    organization_id: UUID = Depends(get_current_organization_id)
):
    """Start partner onboarding with GST verification and geocoding"""
    service = PartnerService(db, event_emitter, user_id, organization_id)
    
    try:
        application = await service.start_onboarding(data)
        return application
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/onboarding/{application_id}/documents",
    response_model=PartnerDocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Document",
    description="""
    Upload document with OCR extraction.
    
    Automatically extracts:
    - GST Certificate: GSTIN, business name
    - PAN Card: PAN number, name
    - Bank Proof: Account number, IFSC
    - Vehicle RC: Registration number, owner name
    """
)
async def upload_document(
    application_id: UUID,
    document_type: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    organization_id: UUID = Depends(get_current_organization_id)
):
    """Upload document and extract data using OCR"""
    # TODO: Upload file to storage (S3/GCS)
    file_url = f"https://storage.example.com/{file.filename}"
    
    # Extract data using OCR
    doc_service = DocumentProcessingService()
    
    if document_type == "GST_CERTIFICATE":
        extracted_data = await doc_service.extract_gst_certificate(file_url)
    elif document_type == "PAN_CARD":
        extracted_data = await doc_service.extract_pan_card(file_url)
    elif document_type == "BANK_PROOF":
        extracted_data = await doc_service.extract_bank_proof(file_url)
    elif document_type == "VEHICLE_RC":
        extracted_data = await doc_service.extract_vehicle_rc(file_url)
    else:
        extracted_data = {}
    
    # Create document record
    doc_repo = PartnerDocumentRepository(db)
    
    # Get application to find partner_id
    app_repo = OnboardingApplicationRepository(db)
    application = await app_repo.get_by_id(application_id, organization_id)
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Create document
    document = await doc_repo.create(
        partner_id=application.id,  # For now, link to application
        organization_id=organization_id,
        document_type=document_type,
        file_url=file_url,
        file_name=file.filename,
        file_size=file.size,
        mime_type=file.content_type,
        ocr_extracted_data=extracted_data,
        ocr_confidence=extracted_data.get("confidence", 0),
        uploaded_by=user_id
    )
    
    await db.commit()
    
    return document


@router.post(
    "/onboarding/{application_id}/submit",
    summary="Submit for Approval",
    description="""
    Submit application for approval after documents uploaded.
    
    Automatically:
    - Calculates risk score
    - Routes to auto-approve/manager/director
    - Low risk (>70): Auto-approved within 1 hour
    - Medium risk (40-70): Manager review, 24-48 hours
    - High risk (<40): Director review, 3-5 days
    """
)
async def submit_for_approval(
    application_id: UUID,
    db: AsyncSession = Depends(get_db),
    event_emitter: EventEmitter = Depends(get_event_emitter),
    user_id: UUID = Depends(get_current_user_id),
    organization_id: UUID = Depends(get_current_organization_id)
):
    """Submit application for approval with risk-based routing"""
    service = PartnerService(db, event_emitter, user_id, organization_id)
    
    try:
        result = await service.submit_for_approval(application_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/onboarding/{application_id}/status",
    response_model=OnboardingApplicationResponse,
    summary="Check Application Status"
)
async def get_application_status(
    application_id: UUID,
    db: AsyncSession = Depends(get_db),
    organization_id: UUID = Depends(get_current_organization_id)
):
    """Get current status of onboarding application"""
    app_repo = OnboardingApplicationRepository(db)
    application = await app_repo.get_by_id(application_id, organization_id)
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    return application


# ===== APPROVAL ENDPOINTS (Manager/Director only) =====

@router.post(
    "/partners/{application_id}/approve",
    response_model=BusinessPartnerResponse,
    summary="Approve Partner Application",
    description="Manager/Director approves partner application"
)
async def approve_partner(
    application_id: UUID,
    decision: ApprovalDecision,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """Approve partner application (manager/director only)"""
    # TODO: Check user has manager/director role
    
    approval_service = ApprovalService(db, user_id)
    
    # Get application to fetch risk assessment
    app_repo = OnboardingApplicationRepository(db)
    application = await app_repo.get_by_id(application_id)
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Create risk assessment from application
    from backend.modules.partners.schemas import RiskAssessment
    
    risk_assessment = RiskAssessment(
        risk_score=application.risk_score or 50,
        risk_category=application.risk_category,
        approval_route="manual",
        factors=[],
        assessment_date=application.submitted_at
    )
    
    try:
        partner = await approval_service.process_approval(
            application_id,
            risk_assessment,
            decision
        )
        await db.commit()
        return partner
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/partners/{application_id}/reject",
    summary="Reject Partner Application"
)
async def reject_partner(
    application_id: UUID,
    decision: ApprovalDecision,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """Reject partner application"""
    # Set approved=False
    decision.approved = False
    
    approval_service = ApprovalService(db, user_id)
    app_repo = OnboardingApplicationRepository(db)
    application = await app_repo.get_by_id(application_id)
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    from backend.modules.partners.schemas import RiskAssessment
    
    risk_assessment = RiskAssessment(
        risk_score=application.risk_score or 0,
        risk_category=application.risk_category,
        approval_route="manual",
        factors=[]
    )
    
    try:
        await approval_service.process_approval(
            application_id,
            risk_assessment,
            decision
        )
        await db.commit()
        return {"message": "Application rejected", "reason": decision.rejection_reason}
    except ValueError as e:
        return {"message": str(e)}


# ===== PARTNER MANAGEMENT ENDPOINTS =====

@router.get(
    "/",
    response_model=List[BusinessPartnerResponse],
    summary="List Partners",
    description="List all business partners with filters"
)
async def list_partners(
    skip: int = 0,
    limit: int = 100,
    partner_type: Optional[PartnerType] = None,
    status: Optional[PartnerStatus] = None,
    kyc_status: Optional[KYCStatus] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    organization_id: UUID = Depends(get_current_organization_id)
):
    """List all partners with filters (auto-isolated by organization)"""
    bp_repo = BusinessPartnerRepository(db)
    
    partners = await bp_repo.list_all(
        organization_id=organization_id,
        skip=skip,
        limit=limit,
        partner_type=partner_type,
        status=status,
        kyc_status=kyc_status,
        search=search
    )
    
    return partners


@router.get(
    "/{partner_id}",
    response_model=BusinessPartnerResponse,
    summary="Get Partner Details"
)
async def get_partner(
    partner_id: UUID,
    db: AsyncSession = Depends(get_db),
    organization_id: UUID = Depends(get_current_organization_id)
):
    """Get partner details by ID"""
    bp_repo = BusinessPartnerRepository(db)
    partner = await bp_repo.get_by_id(partner_id, organization_id)
    
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found"
        )
    
    return partner


@router.get(
    "/{partner_id}/locations",
    response_model=List[PartnerLocationResponse],
    summary="Get Partner Locations"
)
async def get_partner_locations(
    partner_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get all locations for a partner"""
    location_repo = PartnerLocationRepository(db)
    locations = await location_repo.get_by_partner(partner_id)
    return locations


@router.get(
    "/{partner_id}/employees",
    response_model=List[PartnerEmployeeResponse],
    summary="Get Partner Employees"
)
async def get_partner_employees(
    partner_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get all employees for a partner"""
    employee_repo = PartnerEmployeeRepository(db)
    employees = await employee_repo.get_by_partner(partner_id)
    return employees


@router.get(
    "/{partner_id}/documents",
    response_model=List[PartnerDocumentResponse],
    summary="Get Partner Documents"
)
async def get_partner_documents(
    partner_id: UUID,
    document_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all documents for a partner"""
    doc_repo = PartnerDocumentRepository(db)
    documents = await doc_repo.get_by_partner(partner_id, document_type)
    return documents


@router.get(
    "/{partner_id}/vehicles",
    response_model=List[PartnerVehicleResponse],
    summary="Get Partner Vehicles"
)
async def get_partner_vehicles(
    partner_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get all vehicles for a transporter partner"""
    vehicle_repo = PartnerVehicleRepository(db)
    vehicles = await vehicle_repo.get_by_partner(partner_id)
    return vehicles


# ===== AMENDMENT ENDPOINTS =====

@router.post(
    "/{partner_id}/amendments",
    summary="Request Amendment",
    description="Request to change partner details post-approval"
)
async def request_amendment(
    partner_id: UUID,
    amendment: AmendmentRequest,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """Request amendment to partner details"""
    # TODO: Implement amendment service
    return {
        "message": "Amendment request submitted",
        "amendment_id": "mock-uuid",
        "status": "pending_approval"
    }


# ===== EMPLOYEE MANAGEMENT ENDPOINTS =====

@router.post(
    "/{partner_id}/employees",
    response_model=PartnerEmployeeResponse,
    summary="Invite Employee",
    description="Add employee to partner account (max 2 additional employees)"
)
async def invite_employee(
    partner_id: UUID,
    employee: EmployeeInvite,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    organization_id: UUID = Depends(get_current_organization_id)
):
    """Invite employee to partner account"""
    employee_repo = PartnerEmployeeRepository(db)
    
    # Check employee limit
    active_count = await employee_repo.count_active_employees(partner_id)
    if active_count >= 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 2 employees allowed per partner"
        )
    
    # Create employee invitation
    new_employee = await employee_repo.create(
        partner_id=partner_id,
        organization_id=organization_id,
        user_id=user_id,  # Will be updated when they accept
        employee_name=employee.name,
        employee_email=employee.email,
        employee_phone=employee.phone,
        designation=employee.designation,
        role="employee",
        status="invited"
    )
    
    await db.commit()
    
    # TODO: Send invitation email
    
    return new_employee


# ===== KYC RENEWAL ENDPOINTS =====

@router.get(
    "/kyc/expiring",
    response_model=List[BusinessPartnerResponse],
    summary="Get Partners with Expiring KYC",
    description="Get partners with KYC expiring in next 30 days"
)
async def get_expiring_kyc_partners(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    organization_id: UUID = Depends(get_current_organization_id)
):
    """Get partners with KYC expiring soon"""
    kyc_service = KYCRenewalService(db, UUID("00000000-0000-0000-0000-000000000000"))
    partners = await kyc_service.check_kyc_expiry(organization_id, days)
    return partners


@router.post(
    "/{partner_id}/kyc/renew",
    summary="Initiate KYC Renewal",
    description="Start yearly KYC renewal process"
)
async def initiate_kyc_renewal(
    partner_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """Initiate KYC renewal for partner"""
    kyc_service = KYCRenewalService(db, user_id)
    
    try:
        renewal = await kyc_service.initiate_kyc_renewal(partner_id)
        await db.commit()
        
        return {
            "message": "KYC renewal initiated",
            "renewal_id": renewal.id,
            "due_date": renewal.due_date,
            "status": renewal.status
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{partner_id}/kyc/complete",
    summary="Complete KYC Renewal"
)
async def complete_kyc_renewal(
    partner_id: UUID,
    renewal: KYCRenewalRequest,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """Complete KYC renewal with new documents"""
    kyc_service = KYCRenewalService(db, user_id)
    
    try:
        partner = await kyc_service.complete_kyc_renewal(
            renewal.renewal_id,
            renewal.new_document_ids,
            verified=True
        )
        await db.commit()
        
        return {
            "message": "KYC renewal completed successfully",
            "partner_id": partner.id,
            "new_expiry_date": partner.kyc_expiry_date,
            "kyc_status": partner.kyc_status
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ===== VEHICLE MANAGEMENT (for Transporters) =====

@router.post(
    "/{partner_id}/vehicles",
    response_model=PartnerVehicleResponse,
    summary="Add Vehicle",
    description="Add vehicle for transporter partner"
)
async def add_vehicle(
    partner_id: UUID,
    vehicle: VehicleData,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    organization_id: UUID = Depends(get_current_organization_id)
):
    """Add vehicle for transporter"""
    vehicle_repo = PartnerVehicleRepository(db)
    
    # TODO: Verify vehicle from RTO
    
    new_vehicle = await vehicle_repo.create(
        partner_id=partner_id,
        organization_id=organization_id,
        registration_number=vehicle.registration_number,
        vehicle_type=vehicle.vehicle_type,
        manufacturer=vehicle.manufacturer,
        model=vehicle.model,
        year_of_manufacture=vehicle.year_of_manufacture,
        capacity_tons=vehicle.capacity_tons,
        is_active=True,
        created_by=user_id
    )
    
    await db.commit()
    
    return new_vehicle
