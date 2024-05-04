from pydantic import BaseModel


class CodeReviewGet(BaseModel):
    count_true_var: int = 0
    count_true_call: int = 0
    count_comment: int = 0
    style_guide_per: float = 0
    count_all_var: int = 0
    count_all_call: int = 0


class ErrorLinter(BaseModel):
    type: str
    module: str
    obj: str
    line: int
    column: int
    endLine: int | None
    endColumn: int | None
    path: str
    symbol: str
    message: str
    message_id: str
