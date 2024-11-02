from abc import abstractmethod


class SecurityProvider:

    @abstractmethod
    def exec(self, request: Request):
        raise NotImplementedError()


class AuthorizationRequiredProvider(SecurityProvider):

    def exec(self, request: Request):
        if not request.headers.get('Authorization'):
            raise HTTPException(401, message='Authorization required')
        # todo: дальше надо будет расшифровывать токен в хедере, искать пользователя по id сеанса, проверять сенас,
        #   пользователя, сверять таймштам в расшифрованном токене с текущим временем