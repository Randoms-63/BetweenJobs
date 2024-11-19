from typing import Optional, Union
from data.database import get_session
from sqlmodel import Session
from fastapi import APIRouter, Depends, Query
from resumes.resume_models import ResumeRequest, ResumeResponse, ResumeUpdate
from common.exceptions import NotFoundException, UnauthorizedException
from resumes import resume_services as rs
from typing import List
from typing import Literal
from users.auth import get_current_user
from users.user_models import UserModel

router = APIRouter(prefix='/api/resumes', tags=['Resumes'])

@router.get('/', response_model=Union[List[ResumeResponse], ResumeResponse, ]) 
def view_resumes(session: Session = Depends(get_session), 
                 name: Optional[str] = Query(None),
                 location: Optional[str] = Query(None),
                 employment_type: Optional[Literal['Full-time', 'Part-time', 'Contract', 'Temporary', 'Internship', 'Volunteer']] = Query(None),
                 education: Optional[Literal['High School', 'Undergraduate degree', 'Postgraduate degree', 'PhD', 'Diploma']] = Query(None),
                 status: Optional[Literal['Active', 'Hidden', 'Private', 'Matched', 'Archived', 'Busy']] = Query(None),
                 title: Optional[str] = Query(None),
                 skills: Optional[List[str]] = Query(None),
                 current_user: UserModel = Depends(get_current_user)):
    
    if not current_user:
        raise UnauthorizedException(detail='You must be logged in to view resumes')
                                    
    resumes = rs.get_all_resumes(session=session, name=name, location=location, employment_type=employment_type, education=education, status=status, title=title, skills=skills)

    if not resumes:
        raise NotFoundException(detail='No resumes found')

    return resumes


@router.get('/{id}', response_model=ResumeResponse)
def view_resume(id: int, session: Session = Depends(get_session), current_user: UserModel = Depends(get_current_user)):

    if not current_user:
        raise UnauthorizedException(detail='You must be logged in to view resumes')

    resume = rs.get_resume_by_id(id, session)

    if not resume:
        raise NotFoundException(detail='Resume not found')

    return resume


@router.post('/create', response_model=ResumeResponse)
def create_resume(resume_form: ResumeRequest, session: Session = Depends(get_session), current_user: UserModel = Depends(get_current_user)):

    if not current_user:
        raise UnauthorizedException(detail='You must be logged in to create a resume')

    resume = rs.create_resume(resume_form, session)

    if not resume:
        raise NotFoundException(detail='Resume could not be created')

    return resume


@router.put('/update/{id}', response_model=ResumeResponse)
def update_resume(id: int, resume_form: ResumeUpdate, session: Session = Depends(get_session), current_user: UserModel = Depends(get_current_user)):

    if not current_user:
        raise UnauthorizedException(detail='You must be logged in to update a resume')

    resume = rs.update_resume(id, resume_form, session)

    if not resume:
        raise NotFoundException(detail='Resume could not be updated')

    return resume


@router.delete('/delete/{id}', response_model=None)

def delete_resume(id: int, session: Session = Depends(get_session), current_user: UserModel = Depends(get_current_user)):

    if not current_user:
        raise UnauthorizedException(detail='You must be logged in to delete a resume')
    
    resume = rs.delete_resume(id, session)

    if not resume:
        raise NotFoundException(detail='Resume could not be deleted')

    return resume