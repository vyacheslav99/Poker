from typing import Annotated
from fastapi import Depends

from api.services.security import Security
from api.models.user import User


RequiredAuthProvider = Annotated[User, Depends(Security.get_auth)]
OptionalAuthProvider = Annotated[User, Depends(Security.get_auth_optional)]
