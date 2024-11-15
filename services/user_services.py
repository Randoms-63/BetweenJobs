from fastapi import Depends
from data.models.dbmodels import User
from data.database import Session
from sqlmodel import select
from data.database import get_session


def get_all_users(session = Depends(get_session)):

    statement = select(User).order_by(User.id)
    
    users = session.execute(statement).scalars().all()

    return users