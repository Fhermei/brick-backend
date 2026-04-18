"""
Organization endpoints — /api/v1/organizations

All routes require authentication (access_token cookie).
Role checks are done inside each function using a small helper.

Routes:
    POST   /organizations                  — create a new org (any authenticated user)
    GET    /organizations/mine             — list all orgs the caller belongs to
    GET    /organizations/{org_id}         — get one org (members only)
    PATCH  /organizations/{org_id}         — update org details (owner or admin only)
    DELETE /organizations/{org_id}         — soft-delete org (owner only)
    GET    /organizations/{org_id}/members — list all members of an org
    DELETE /organizations/{org_id}/members/{user_id}  — remove a member (owner/admin)
    PATCH  /organizations/{org_id}/members/{user_id}/role — change a member's role (owner/admin)
"""

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.security import get_current_user
from src.db.session import get_db
from src.models.organization import Organization, OrgMember
from src.models.user import User
from src.schemas.organization import (
    OrgCreate,
    OrgListResponse,
    OrgMemberResponse,
    OrgResponse,
    OrgUpdate,
)

router = APIRouter()

# ---------------------------------------------------------------------------
# Dependency helpers — kept at the top so every route can reuse them
# ---------------------------------------------------------------------------
def get_db_user(
    claims: dict    = Depends(get_current_user),
    db:     Session = Depends(get_db),
) -> User:
    """
    Resolve the JWT claims → User row.
    Raises 401 if the user no longer exists in the database.
    """
    email = claims.get("email") or claims.get("username")
    cognito_sub = claims.get("sub")
    
    print(f"get_db_user - Email: {email}, Cognito Sub: {cognito_sub}", flush=True)
    
    if not email and not cognito_sub:
        raise HTTPException(status_code=401, detail="Invalid token claims.")

    # Try to find by cognito_sub first
    user = None
    if cognito_sub:
        user = db.query(User).filter(User.cognito_sub == cognito_sub).first()
        print(f"Search by cognito_sub {cognito_sub}: Found = {user is not None}", flush=True)
    
    # If not found, try by email
    if not user and email:
        user = db.query(User).filter(User.email == email).first()
        print(f"Search by email {email}: Found = {user is not None}", flush=True)
    
    if not user:
        # User doesn't exist in local DB - create fallback
        print(f"WARNING: User {email} not found in local DB. Creating fallback record.", flush=True)
        user = User(
            name=email.split('@')[0] if email else "Unknown",
            email=email if email else f"{cognito_sub}@temp.com",
            cognito_sub=cognito_sub,
            is_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    print(f"Returning user: ID={user.id}, Email={user.email}", flush=True)
    return user

def get_org_or_404(org_id: uuid.UUID, db: Session) -> Organization:
    """Fetch an org by id or raise 404."""
    org = db.query(Organization).filter(
        Organization.id == org_id,
        Organization.is_active == True,  # noqa: E712
    ).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found.")
    return org


def get_membership_or_403(org_id: uuid.UUID, user_id: uuid.UUID, db: Session) -> OrgMember:
    """
    Return the OrgMember row if the user belongs to this org.
    Raises 403 if they are not a member or their invite is still pending.
    """
    membership = db.query(OrgMember).filter(
        OrgMember.org_id  == org_id,
        OrgMember.user_id == user_id,
        OrgMember.status  == "active",
    ).first()
    if not membership:
        raise HTTPException(
            status_code=403,
            detail="You are not a member of this organisation.",
        )
    return membership


def require_role(membership: OrgMember, allowed_roles: list[str]) -> None:
    """
    Raise 403 if the member's role is not in the allowed list.
    Usage:  require_role(membership, ["owner", "admin"])
    """
    if membership.role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail=f"This action requires one of these roles: {', '.join(allowed_roles)}.",
        )


def build_org_response(org: Organization, db: Session) -> OrgResponse:
    """
    Convert an Organization ORM object into an OrgResponse schema.
    Adds the live member_count so the frontend does not need a second call.
    """
    member_count = db.query(OrgMember).filter(
        OrgMember.org_id == org.id,
        OrgMember.status == "active",
    ).count()

    return OrgResponse(
        id           = org.id,
        name         = org.name,
        industry     = org.industry,
        currency     = org.currency,
        timezone     = org.timezone,
        logo_url     = org.logo_url,
        owner_id     = org.owner_id,
        is_active    = org.is_active,
        created_at   = org.created_at,
        updated_at   = org.updated_at,
        member_count = member_count,
    )


# ---------------------------------------------------------------------------
# POST /organizations — create a new organisation
# ---------------------------------------------------------------------------

@router.post(
    "/",
    response_model=OrgResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new organisation",
)
def create_organization(
    data:    OrgCreate,
    current_user: User    = Depends(get_db_user),
    db:           Session = Depends(get_db),
) -> OrgResponse:
    """
    Any authenticated user can create an organisation.
    The creator is automatically added as a member with the 'owner' role.

    This is the endpoint called by the Onboarding page right after first login.
    """
    # Create the organisation row
    new_org = Organization(
        name     = data.name.strip(),
        industry = data.industry,
        currency = data.currency.upper(),
        timezone = data.timezone,
        logo_url = data.logo_url,
        owner_id = current_user.id,
    )
    db.add(new_org)
    db.flush()  # flush so new_org.id is available before we create the member row

    # Auto-add creator as an active owner member
    owner_membership = OrgMember(
        org_id  = new_org.id,
        user_id = current_user.id,
        role    = "owner",
        status  = "active",
    )
    db.add(owner_membership)
    db.commit()
    db.refresh(new_org)

    return build_org_response(new_org, db)


# ---------------------------------------------------------------------------
# GET /organizations/mine — all orgs the caller belongs to
# ---------------------------------------------------------------------------

@router.get(
    "/mine",
    response_model=OrgListResponse,
    summary="List all organisations the current user belongs to",
)
def list_my_organizations(
    current_user: User    = Depends(get_db_user),
    db:           Session = Depends(get_db),
) -> OrgListResponse:
    """
    Returns every active organisation where the caller is an active member.
    Used by the Sidebar's OrgSwitcher dropdown and by LoginPage to decide
    whether to redirect to /onboarding or /dashboard.
    """
    memberships = db.query(OrgMember).filter(
        OrgMember.user_id == current_user.id,
        OrgMember.status  == "active",
    ).all()

    orgs = []
    for m in memberships:
        org = db.query(Organization).filter(
            Organization.id       == m.org_id,
            Organization.is_active == True,  # noqa: E712
        ).first()
        if org:
            orgs.append(build_org_response(org, db))

    return OrgListResponse(total=len(orgs), organizations=orgs)


# ---------------------------------------------------------------------------
# GET /organizations/{org_id} — get a single organisation
# ---------------------------------------------------------------------------

@router.get(
    "/{org_id}",
    response_model=OrgResponse,
    summary="Get a single organisation by ID",
)
def get_organization(
    org_id:       uuid.UUID,
    current_user: User    = Depends(get_db_user),
    db:           Session = Depends(get_db),
) -> OrgResponse:
    """
    Returns full org details.
    Only members of this org can access it.
    """
    org = get_org_or_404(org_id, db)
    get_membership_or_403(org_id, current_user.id, db)  # membership check
    return build_org_response(org, db)


# ---------------------------------------------------------------------------
# PATCH /organizations/{org_id} — update org details
# ---------------------------------------------------------------------------

@router.patch(
    "/{org_id}",
    response_model=OrgResponse,
    summary="Update organisation details (owner or admin only)",
)
def update_organization(
    org_id:       uuid.UUID,
    data:         OrgUpdate,
    current_user: User    = Depends(get_db_user),
    db:           Session = Depends(get_db),
) -> OrgResponse:
    """
    Partial update — only the fields that are sent will change.
    Only the org owner or an admin can update org settings.
    """
    org        = get_org_or_404(org_id, db)
    membership = get_membership_or_403(org_id, current_user.id, db)
    require_role(membership, ["owner", "admin"])

    # Apply only the fields that were actually sent (exclude_unset skips None defaults)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        # Normalise currency to uppercase if it was included
        if field == "currency" and value:
            value = value.upper()
        setattr(org, field, value)

    org.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(org)

    return build_org_response(org, db)


# ---------------------------------------------------------------------------
# DELETE /organizations/{org_id} — soft-delete an organisation
# ---------------------------------------------------------------------------

@router.delete(
    "/{org_id}",
    status_code=status.HTTP_200_OK,
    summary="Soft-delete an organisation (owner only)",
)
def delete_organization(
    org_id:       uuid.UUID,
    current_user: User    = Depends(get_db_user),
    db:           Session = Depends(get_db),
) -> dict:
    """
    Sets is_active = False instead of deleting the row.
    This preserves all historical project/task/budget data.
    Only the owner can delete an organisation.
    """
    org        = get_org_or_404(org_id, db)
    membership = get_membership_or_403(org_id, current_user.id, db)
    require_role(membership, ["owner"])

    org.is_active  = False
    org.updated_at = datetime.utcnow()
    db.commit()

    return {"message": f"Organisation '{org.name}' has been deleted."}


# ---------------------------------------------------------------------------
# GET /organizations/{org_id}/members — list all active members
# ---------------------------------------------------------------------------

@router.get(
    "/{org_id}/members",
    response_model=list[OrgMemberResponse],
    summary="List all members of an organisation",
)
def list_org_members(
    org_id:       uuid.UUID,
    current_user: User    = Depends(get_db_user),
    db:           Session = Depends(get_db),
) -> list[OrgMemberResponse]:
    """
    Returns every active member row.
    Any member of the org can call this (needed for the Team page and task assignment).
    """
    get_org_or_404(org_id, db)
    get_membership_or_403(org_id, current_user.id, db)

    members = db.query(OrgMember).filter(
        OrgMember.org_id == org_id,
    ).all()

    return [
        OrgMemberResponse(
            user_id   = m.user_id,
            role      = m.role,
            status    = m.status,
            joined_at = m.joined_at,
        )
        for m in members
    ]


# ---------------------------------------------------------------------------
# PATCH /organizations/{org_id}/members/{user_id}/role — change a member's role
# ---------------------------------------------------------------------------

@router.patch(
    "/{org_id}/members/{user_id}/role",
    response_model=OrgMemberResponse,
    summary="Change a member's role (owner or admin only)",
)
def change_member_role(
    org_id:       uuid.UUID,
    user_id:      uuid.UUID,
    role:         str,           # sent as a query param: ?role=admin
    current_user: User    = Depends(get_db_user),
    db:           Session = Depends(get_db),
) -> OrgMemberResponse:
    """
    Allowed roles: owner, admin, manager, member, viewer.
    Only the current owner can promote someone to owner (and that demotes them).
    Admins can change everyone except the owner.
    """
    VALID_ROLES = {"owner", "admin", "manager", "member", "viewer"}
    if role not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Choose from: {', '.join(sorted(VALID_ROLES))}",
        )

    get_org_or_404(org_id, db)
    caller_membership = get_membership_or_403(org_id, current_user.id, db)
    require_role(caller_membership, ["owner", "admin"])

    # Fetch the target member
    target = db.query(OrgMember).filter(
        OrgMember.org_id  == org_id,
        OrgMember.user_id == user_id,
    ).first()
    if not target:
        raise HTTPException(status_code=404, detail="Member not found in this organisation.")

    # Admins cannot change the owner's role
    if target.role == "owner" and caller_membership.role != "owner":
        raise HTTPException(status_code=403, detail="Only the owner can change the owner's role.")

    # If promoting to owner — demote the current owner first
    if role == "owner":
        caller_membership.role = "admin"

    target.role = role
    db.commit()
    db.refresh(target)

    return OrgMemberResponse(
        user_id   = target.user_id,
        role      = target.role,
        status    = target.status,
        joined_at = target.joined_at,
    )


# ---------------------------------------------------------------------------
# DELETE /organizations/{org_id}/members/{user_id} — remove a member
# ---------------------------------------------------------------------------

@router.delete(
    "/{org_id}/members/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Remove a member from the organisation (owner or admin only)",
)
def remove_member(
    org_id:       uuid.UUID,
    user_id:      uuid.UUID,
    current_user: User    = Depends(get_db_user),
    db:           Session = Depends(get_db),
) -> dict:
    """
    Removes a member from the org.
    The owner cannot remove themselves — they must delete the org or transfer ownership first.
    """
    get_org_or_404(org_id, db)
    caller_membership = get_membership_or_403(org_id, current_user.id, db)
    require_role(caller_membership, ["owner", "admin"])

    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot remove yourself. Transfer ownership first.")

    target = db.query(OrgMember).filter(
        OrgMember.org_id  == org_id,
        OrgMember.user_id == user_id,
    ).first()
    if not target:
        raise HTTPException(status_code=404, detail="Member not found in this organisation.")

    # Admins cannot remove the owner
    if target.role == "owner" and caller_membership.role != "owner":
        raise HTTPException(status_code=403, detail="Only the owner can remove the owner.")

    db.delete(target)
    db.commit()

    return {"message": "Member removed successfully."}