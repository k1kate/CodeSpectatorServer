from io import StringIO
from pylint.lint import Run
from json import loads
from pathlib import Path
from src.Models.CodeReview import CodeReviewGet, ErrorLinter
import sys
from re import findall

from Classes.PathExtend import PathExtend
from aiofiles import open as open_aio
from fastapi import UploadFile
from uuid import uuid4


class CodeStyleService:
    def __init__(self):
        self.__re_var = r'\b(?!false|None|True|and|as|self|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b[a-zA-Z_][a-zA-Z0-9_]*\b'
        self.__metric = CodeReviewGet()

    @property
    def metric(self) -> CodeReviewGet:
        return self.__metric

    async def upload_file(self, file: UploadFile) -> str:
        name, extend = file.filename.split(".")

        new_name = PathExtend.create_file_name(extension=extend)

        filepath = PathExtend(new_name)
        async with open_aio(str(filepath), 'wb') as out_file:
            while content := await file.read(1024):
                await out_file.write(content)
        return str(filepath.path.name)

    def linter(self, path_file: Path) -> list[ErrorLinter]:
        stdout = sys.stdout
        sys.stdout = StringIO()

        ARGS = ["--output-format=JSON"]
        r = Run([str(path_file)]+ARGS, exit=False)

        test = sys.stdout.getvalue()
        sys.stdout.close()
        sys.stdout = stdout
        errors = []
        for i in loads(test):
            i["message_id"] = i["message-id"]
            errors.append(ErrorLinter.model_validate(i))
        return errors

    def map_linter(self, errors: list[ErrorLinter]) -> dict:
        map_linter = {}
        for i in errors:
            if i.type in ("refactor", "convention"):
                self.__metric.style_guide_per += 1
            if i.line not in map_linter:
                map_linter[i.line] = []
            map_linter[i.line].append(i)
        return map_linter

    def state_var(self, path_file: Path, map_linter: dict):
        all_count_var = 0
        all_count_call = 0

        map_var = set()

        with open(path_file) as file:
            lines = file.readlines()
            for num, line in enumerate(lines):
                if "#" in line:
                    self.__metric.count_comment += 1

                if "=" in line:
                    var = findall(self.__re_var, line.split("=")[0])
                    for v in var:
                        if v not in map_var:
                            if len(v) >= 3:
                                self.__metric.count_true_var += 1
                            elif map_linter.get(num + 1) is not None:
                                self.__metric.count_true_var += 1
                            map_var.add(v)
                elif "def" in line:
                    new_line = line.replace("def", "")
                    name_call, op = new_line.split("(")
                    name_call = findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", name_call)[0]
                    if len(name_call) >= 3:
                        self.__metric.count_true_call += 1
                    elif map_linter.get(num + 1) is not None:
                        self.__metric.count_true_call += 1
                    all_count_call += 1

                    var = findall(self.__re_var, op)
                    for v in var:
                        if len(v) >= 3:
                            self.__metric.count_true_var += 1
                        elif map_linter.get(num + 1) is not None:
                            self.__metric.count_true_var += 1
                        all_count_var += 1

                elif "class" in line:
                    new_line = line.replace("class", "")
                    name_call = findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", new_line)[0]
                    if len(name_call) >= 3:
                        self.__metric.count_true_call += 1
                    elif map_linter.get(num + 1) is not None:
                        self.__metric.count_true_call += 1
                    all_count_call += 1

                elif "for" in line:
                    var = findall(
                        r'\b(?!false|None|True|and|as|self|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b[a-zA-Z_][a-zA-Z0-9_]*\b',
                        line)
                    for v in var:
                        if len(v) >= 3:
                            self.__metric.count_true_var += 1
                        elif map_linter.get(num + 1) is not None:
                            self.__metric.count_true_var += 1
                        all_count_var += 1
            all_count_var += len(map_var)
        self.__metric.count_all_var = all_count_var
        self.__metric.count_all_call = all_count_call
        self.__metric.style_guide_per = round(self.__metric.style_guide_per / (num + 1), 2)
