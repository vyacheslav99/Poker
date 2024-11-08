from typing import Annotated
from fastapi import Depends

from api.services.security import Security
from api.models.user import User


CheckAuthProvider = Annotated[User, Depends(Security.check_auth)]
