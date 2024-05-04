from fastapi import APIRouter, Depends, Response, status, Form, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse

from ..Models.CodeReview import CodeReviewGet
from ..Services.CodeStyleServices import CodeStyleService
from Classes.PathExtend import PathExtend

from pathlib import Path
import os
from asyncio import sleep


router = APIRouter(prefix="/code_style", tags=["code style"])


def delete_file(file_name: str):
    os.remove(str(PathExtend(file_name).path))


@router.post("/", response_model=CodeReviewGet)
async def style_analize(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(),
        code_services: CodeStyleService = Depends()
):
    name_file = await code_services.upload_file(file)

    errors = code_services.linter(PathExtend(name_file).path)
    map_errors = code_services.map_linter(errors)
    code_services.state_var(PathExtend(name_file).path, map_errors)

    background_tasks.add_task(delete_file, name_file)

    return code_services.metric