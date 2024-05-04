from fastapi import APIRouter
from .code_style import router as code_style_router

router = APIRouter(prefix="/v1")
router.include_router(code_style_router)