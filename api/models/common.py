from pydantic import BaseModel


class SuccessResponse(BaseModel):
    success: bool = True


class DeletedResponse(SuccessResponse):
    deleted: int
