from typing import Annotated
from fastapi import Depends

from api.services.security import Security
from api.models.security import User


CheckAuthProvider = Annotated[User, Depends(Security.check_auth)]
