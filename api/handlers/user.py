from api.models.user import SignupSchema, UserSchema, SessionSchema

api = Router('/api/v1')


@api.endpoint('/signup', HttpMethods.POST, body_schema=SignupSchema(), response_schema=UserSchema())
def create_user(request: Request):
    pass


@api.endpoint('/signin', HttpMethods.POST, body_schema=SignupSchema(), response_schema=SessionSchema())
def login(request: Request):
    pass