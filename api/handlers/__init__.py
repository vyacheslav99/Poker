from typing import Annotated
from fastapi import Depends

from api.services.security import Security
from api.models.security import UserBase


CheckAuthProvider = Annotated[UserBase, Depends(Security.check_auth)]
