from typing import Annotated
from fastapi import Depends

from api.services.user import UserService
from api.models.user import User


CheckAuthProvider = Annotated[User, Depends(UserService.check_auth)]
