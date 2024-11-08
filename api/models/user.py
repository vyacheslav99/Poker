from pydantic import BaseModel


class UserPatchBody(BaseModel):
    fullname: str | None = None
