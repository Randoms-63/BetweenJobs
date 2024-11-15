from fastapi import APIRouter
from common.exceptions import NotFoundException
from sqlmodel import Session
from data.database import get_session
from fastapi import Depends
from data.models.pydantic_models import UserResponse
from services.user_services import get_all_users

router = APIRouter()

# Endpoint to get a user and their companies
@router.get("/users/{user_id}", response_model=list[UserResponse])
def view_all_users(session: Session = Depends(get_session)):

    users = get_all_users(session)

    if not users:
        raise NotFoundException(detail = "No users found")

    return users
