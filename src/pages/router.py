from fastapi import APIRouter,Request
from fastapi.templating import Jinja2Templates

template=Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/page",
    tags=["pages"]
)

@router.get("/")
def get_base_page(request:Request):
    return template.TemplateResponse("index.html",{"request":request})
