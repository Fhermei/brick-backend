"""
Team API Endpoints - Updated for Project-specific invites
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import uuid

from src.core.security import get_current_user
from src.db.session import get_db
from src.models.user import User
from src.models.organization import Organization, OrgMember
from src.models.project import Project, ProjectMember
from src.models.role import Role
from src.schemas.team import InviteRequest, InviteResponse, MemberResponse, UpdateMemberRole, TeamListResponse
from src.services.email_service import email_service
from datetime import timedelta

router = APIRouter()

@router.post("/invite", response_model=InviteResponse, status_code=status.HTTP_201_CREATED)
async def invite_member(
    invite_data: InviteRequest,
    org_id: uuid.UUID = Query(..., description="Organization ID"),
    project_id: Optional[uuid.UUID] = Query(None, description="Project ID (optional)"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Invite a new member to the organization or specific project."""
    from src.models.invite import Invite
    from src.services.notification_service import notification_service
    from datetime import timedelta
    
    try:
        # Get inviter
        inviter_id = current_user.get("id")
        if not inviter_id:
            raise HTTPException(status_code=401, detail="Invalid user authentication")
            
        inviter = db.query(User).filter(User.id == inviter_id).first()
        if not inviter:
            raise HTTPException(status_code=401, detail="Inviter user not found")
        
        # Check organization
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        # Check permission
        inviter_membership = db.query(OrgMember).filter(
            OrgMember.org_id == org_id,
            OrgMember.user_id == inviter.id,
            OrgMember.status == "active"
        ).first()
        
        if not inviter_membership or inviter_membership.role not in ["owner", "admin"]:
            raise HTTPException(status_code=403, detail="Only owners and admins can invite members")
        
        # Check project if provided
        project = None
        if project_id:
            project = db.query(Project).filter(Project.id == project_id, Project.org_id == org_id).first()
            if not project:
                raise HTTPException(status_code=404, detail="Project not found in this organization")
        
        # Get role name from request
        role_name = invite_data.role_name or "member"
        
        # Validate email format
        if not invite_data.email or "@" not in invite_data.email:
            raise HTTPException(status_code=400, detail="Invalid email address")
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == invite_data.email).first()
        
        if existing_user:
            # User exists - add them directly to organization
            existing_org_membership = db.query(OrgMember).filter(
                OrgMember.org_id == org_id,
                OrgMember.user_id == existing_user.id
            ).first()
            
            if not existing_org_membership:
                org_membership = OrgMember(
                    org_id=org_id,
                    user_id=existing_user.id,
                    role=role_name,
                    status="active"
                )
                db.add(org_membership)
                db.flush()
            
            # Add to project if specified
            if project_id and project:
                existing_project_membership = db.query(ProjectMember).filter(
                    ProjectMember.project_id == project_id,
                    ProjectMember.user_id == existing_user.id
                ).first()
                
                if not existing_project_membership:
                    project_membership = ProjectMember(
                        project_id=project_id,
                        user_id=existing_user.id,
                        role_id=role_name,
                        joined_at=datetime.utcnow()
                    )
                    db.add(project_membership)
            
            db.commit()
            
            # Send notification
            try:
                notification_service.notify_member_joined(db, org, existing_user.id, existing_user.name)
            except Exception as e:
                print(f"Notification failed: {e}")
            
            return InviteResponse(
                message=f"{invite_data.email} has been added to the organization",
                email=invite_data.email,
                invited_at=datetime.utcnow()
            )
        else:
            # User does not exist - just create an invite record
            token = str(uuid.uuid4())
            expires_at = datetime.utcnow() + timedelta(days=7)
            
            invite = Invite(
                email=invite_data.email,
                org_id=org_id,
                project_id=project_id,
                invited_by=inviter.id,
                role=role_name,
                token=token,
                expires_at=expires_at
            )
            db.add(invite)
            db.commit()
            
            # DO NOT create org_members or project_members for non-existent users
            # They will be created when the user signs up using the invite token
        
        # Send email invitation
        try:
            email_service.send_invite_email(
                to_email=invite_data.email,
                org_name=org.name,
                inviter_name=inviter.name,
                role=role_name,
                project_name=project.title if project else None,
                invite_token=token
            )
        except Exception as e:
            print(f"Email sending failed but invite was created: {e}")
        
        return InviteResponse(
            message=f"Invitation sent to {invite_data.email}",
            email=invite_data.email,
            invited_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in invite_member: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/project/{project_id}", response_model=TeamListResponse)
async def get_project_members(
    project_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all members of a specific project"""
    user_id = current_user.get("id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Check project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has access to this project
    project_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user.id
    ).first()
    
    org_member = db.query(OrgMember).filter(
        OrgMember.org_id == project.org_id,
        OrgMember.user_id == user.id,
        OrgMember.status == "active"
    ).first()
    
    if not project_member and not org_member:
        raise HTTPException(status_code=403, detail="Access denied to this project")
    
    # Get all project members
    members = db.query(ProjectMember).filter(ProjectMember.project_id == project_id).all()
    
    member_responses = []
    for m in members:
        user_obj = db.query(User).filter(User.id == m.user_id).first()
        if user_obj:
            member_responses.append(MemberResponse(
                id=m.id,
                user_id=m.user_id,
                name=user_obj.name,
                email=user_obj.email,
                role=m.role_id,
                role_id=None,
                status="active",
                joined_at=m.joined_at,
                avatar=None
            ))
    
    return TeamListResponse(total=len(member_responses), members=member_responses)


@router.delete("/project/{project_id}/member/{user_id}", status_code=status.HTTP_200_OK)
async def remove_project_member(
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a member from a specific project.
    Only project owners or organization admins can remove members.
    """
    email = current_user.get("email") or current_user.get("username")
    current_user_obj = db.query(User).filter(User.email == email).first()
    if not current_user_obj:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Check project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if current user has permission (project owner or org admin)
    is_project_owner = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user_obj.id,
        ProjectMember.role_id == "owner"
    ).first()
    
    org_role = db.query(OrgMember).filter(
        OrgMember.org_id == project.org_id,
        OrgMember.user_id == current_user_obj.id,
        OrgMember.status == "active"
    ).first()
    
    if not is_project_owner and not (org_role and org_role.role in ["owner", "admin"]):
        raise HTTPException(status_code=403, detail="Insufficient permissions to remove members")
    
    # Cannot remove yourself from the project
    if str(user_id) == str(current_user_obj.id):
        raise HTTPException(status_code=400, detail="You cannot remove yourself from the project")
    
    # Find the project member
    project_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()
    
    if not project_member:
        raise HTTPException(status_code=404, detail="Member not found in this project")
    
    # Cannot remove the project owner
    if project_member.role_id == "owner":
        raise HTTPException(status_code=403, detail="Cannot remove the project owner")
    
    db.delete(project_member)
    db.commit()
    
    return {"message": "Member removed from project successfully"}


@router.get("/", response_model=TeamListResponse)
async def list_members(
    org_id: uuid.UUID = Query(..., description="Organization ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all active members of an organization"""
    email = current_user.get("email") or current_user.get("username")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Check access
    membership = db.query(OrgMember).filter(
        OrgMember.org_id == org_id,
        OrgMember.user_id == user.id,
        OrgMember.status == "active"
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Access denied to this organization")
    
    # Get all active members
    members = db.query(OrgMember).filter(
        OrgMember.org_id == org_id,
        OrgMember.status == "active"
    ).all()
    
    member_responses = []
    for m in members:
        user_obj = db.query(User).filter(User.id == m.user_id).first()
        if user_obj:
            member_responses.append(MemberResponse(
                id=m.id,
                user_id=m.user_id,
                name=user_obj.name,
                email=user_obj.email,
                role=m.role,
                role_id=None,
                status=m.status,
                joined_at=m.joined_at,
                avatar=None
            ))
    
    return TeamListResponse(total=len(member_responses), members=member_responses)


@router.patch("/{member_id}/role", response_model=MemberResponse)
async def update_member_role(
    member_id: uuid.UUID,
    role_data: UpdateMemberRole,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a member's role in the organization (owner or admin only)"""
    email = current_user.get("email") or current_user.get("username")
    current_user_obj = db.query(User).filter(User.email == email).first()
    if not current_user_obj:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Get the member
    member = db.query(OrgMember).filter(OrgMember.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Get the organization
    org = db.query(Organization).filter(Organization.id == member.org_id).first()
    
    # Check if current user has permission
    current_membership = db.query(OrgMember).filter(
        OrgMember.org_id == member.org_id,
        OrgMember.user_id == current_user_obj.id,
        OrgMember.status == "active"
    ).first()
    
    if not current_membership or current_membership.role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Only owners and admins can update roles")
    
    # Cannot change owner's role unless you're the owner
    if member.role == "owner" and current_membership.role != "owner":
        raise HTTPException(status_code=403, detail="Only the organization owner can change the owner's role")
    
    # Update role
    new_role = role_data.role_name or "member"
    member.role = new_role
    db.commit()
    db.refresh(member)
    
    user_obj = db.query(User).filter(User.id == member.user_id).first()
    
    return MemberResponse(
        id=member.id,
        user_id=member.user_id,
        name=user_obj.name if user_obj else "Unknown",
        email=user_obj.email if user_obj else "unknown",
        role=member.role,
        role_id=role_data.role_id,
        status=member.status,
        joined_at=member.joined_at,
        avatar=None
    )


@router.patch("/project/{project_id}/member/{user_id}/role", response_model=MemberResponse)
async def update_project_member_role(
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    role: str = Query(..., description="New role for the member (owner, admin, manager, member, viewer)"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a member's role within a specific project.
    Only project owners or organization admins can update roles.
    """
    VALID_ROLES = {"owner", "admin", "manager", "member", "viewer"}
    if role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role. Choose from: {', '.join(VALID_ROLES)}")
    
    email = current_user.get("email") or current_user.get("username")
    current_user_obj = db.query(User).filter(User.email == email).first()
    if not current_user_obj:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Check project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if current user has permission (project owner or org admin)
    is_project_owner = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user_obj.id,
        ProjectMember.role_id == "owner"
    ).first()
    
    org_role = db.query(OrgMember).filter(
        OrgMember.org_id == project.org_id,
        OrgMember.user_id == current_user_obj.id,
        OrgMember.status == "active"
    ).first()
    
    if not is_project_owner and not (org_role and org_role.role in ["owner", "admin"]):
        raise HTTPException(status_code=403, detail="Insufficient permissions to update roles")
    
    # Find the project member
    project_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()
    
    if not project_member:
        raise HTTPException(status_code=404, detail="Member not found in this project")
    
    # Cannot change the project owner's role unless you're the owner
    if project_member.role_id == "owner" and not is_project_owner:
        raise HTTPException(status_code=403, detail="Only the project owner can change the owner's role")
    
    # Update role
    project_member.role_id = role
    db.commit()
    db.refresh(project_member)
    
    user_obj = db.query(User).filter(User.id == user_id).first()
    
    return MemberResponse(
        id=project_member.id,
        user_id=project_member.user_id,
        name=user_obj.name if user_obj else "Unknown",
        email=user_obj.email if user_obj else "unknown",
        role=project_member.role_id,
        role_id=None,
        status="active",
        joined_at=project_member.joined_at,
        avatar=None
    )


@router.delete("/{member_id}", status_code=status.HTTP_200_OK)
async def remove_member(
    member_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a member from the organization (owner or admin only)"""
    email = current_user.get("email") or current_user.get("username")
    current_user_obj = db.query(User).filter(User.email == email).first()
    if not current_user_obj:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Get the member
    member = db.query(OrgMember).filter(OrgMember.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Cannot remove yourself
    if member.user_id == current_user_obj.id:
        raise HTTPException(status_code=400, detail="You cannot remove yourself from the organization")
    
    # Check if current user has permission
    current_membership = db.query(OrgMember).filter(
        OrgMember.org_id == member.org_id,
        OrgMember.user_id == current_user_obj.id,
        OrgMember.status == "active"
    ).first()
    
    if not current_membership or current_membership.role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Only owners and admins can remove members")
    
    # Cannot remove owner unless you're the owner
    if member.role == "owner" and current_membership.role != "owner":
        raise HTTPException(status_code=403, detail="Only the organization owner can remove the owner")
    
    db.delete(member)
    db.commit()
    
    return {"message": "Member removed successfully"}