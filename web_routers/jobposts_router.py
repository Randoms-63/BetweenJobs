from fastapi import APIRouter, Request, Depends, Query, Form, Response
from starlette.templating import Jinja2Templates
from data.database import get_session
from sqlmodel import Session
from utils import auth as au
from jobposts import jobpost_service as js
from utils import attribute_service as ats
from common.template_config import CustomJinja2Templates
from datetime import timedelta


jobs_router = APIRouter(prefix='/jobposts')
templates = CustomJinja2Templates(directory='templates')


@jobs_router.get('/')
def default_view(
    request: Request, 
    session: Session = Depends(get_session),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    job_adds = js.show_all_posts(session=session)

    all_jobs = len(job_adds)
    # Apply pagination
    start = (page -1) * limit
    end = start + limit
    paginated_jobs = job_adds[start:end]
    total_pages = (all_jobs + limit - 1) // limit

    # Get locations and employment tyepes for dropdown list
    locations = list(ats.get_all_locations(session))
    employments = list(ats.get_all_employments(session))
    # Map company logo by company ID
    logos = ats.get_all_logos(session)
    logo_dict = {company.company_id: company.logo_url for company in logos if company.logo_url}
    print(logo_dict)
    token = request.cookies.get('token')
    context={
        'request': request, 
        'jobadds': paginated_jobs,
        'alladds': all_jobs,
        'current_page': page,
        'total_pages': total_pages,
        'min': min, 
        'filters': {
            'search_field': None,
            'keyword': None
        },
        'locations': locations,
        'employments': employments,
        'logo_dict': logo_dict
    }

    if token:
        user = au.get_current_user(token)
        context['user'] = user

    return templates.TemplateResponse(
        request=request,
        name='job-listings.html', 
        context=context
    )

# Utility function for rendering search resuls in search()
def _get_search_data(
    keyword: str = Form(...),
    search_field: str = Form(...),
    region: str = Form(...),
    job_type: str = Form(...)
):
    return keyword, search_field, region, job_type


@jobs_router.post('/')
def search(
    request: Request, 
    session: Session = Depends(get_session),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    form_data = Depends(_get_search_data)
):
    # Obtain filtered elements
    keyword, search_field, region, jobtype = form_data
   
    # Map search_field to function arguments
    filter_args = {}
    if search_field and keyword:
        filter_args[search_field] = keyword
    if region:
        filter_args["location.name"] = region
    if jobtype:
        filter_args['employment.name'] = jobtype
    # Get job posts and sum of jobposts
    job_adds = js.show_all_posts(
        session=session,
        **filter_args
    )

    all_jobs = len(job_adds)
    # Apply pagination
    start = (page -1) * limit
    end = start + limit
    paginated_jobs = job_adds[start:end]
    total_pages = (all_jobs + limit - 1) // limit

    # Get locations and employment tyepes for dropdown list
    locations = list(ats.get_all_locations(session))
    employments = list(ats.get_all_employments(session))
    # Map company logo by company ID
    logos = ats.get_all_logos(session)
    logo_dict = {company.company_id: company.logo_url for company in logos if company.logo_url}

    token = request.cookies.get('token')
    context={
        'request': request, 
        'jobadds': paginated_jobs,
        'alladds': all_jobs,
        'current_page': page,
        'total_pages': total_pages,
        'min': min,
        'filters': {
            'search_field': search_field,
            'keyword': keyword
        },
        'locations': locations,
        'employments': employments,
        'filters': filter_args,
        'logo_dict': logo_dict
    }

    if token:
        user = au.get_current_user(token)
        context['user'] = user

    return templates.TemplateResponse(
        request=request,
        name='job-listings.html', 
        context=context
    )

@jobs_router.get('/{id}')
def show_jobpost(
    id: int,
    request: Request,
    response: Response, 
    session: Session = Depends(get_session)
):

    target_job = js.view_job_post_by_id(id, session)

    deadline = target_job.created_at + timedelta(days=30)
    location = ats.get_location_by_id(target_job.location_id, session)
    employment = ats.get_employment_type_by_id(target_job.employment_type_id, session)
    logo = ats.get_company_logo(target_job.company_id, session)

    # Get required skills for the job post
    skills = ats.get_skills_for_job(target_job.id, session)

    token = request.cookies.get('token')
    context={
        'request': request, 
        'jobad': target_job,
        'min': min,
        'location': location,
        'employment': employment,
        'skills': skills,
        'deadline': deadline,
        'logo': logo
    }

    if token:
        user = au.get_current_user(token)
        context['user'] = user
    
    # store job id and user id in cookies
    response.set_cookie(key="job_id", value=str(target_job.id))
    response.set_cookie(key="resume_id", value="6")

    return templates.TemplateResponse(
        request=request,
        name='job-single.html', 
        context=context
    )

    