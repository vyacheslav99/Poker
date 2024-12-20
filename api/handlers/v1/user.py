from fastapi import APIRouter, status, UploadFile

from api.handlers.auth import RequiredAuthProvider
from api.models.user import (UserPublic, ChangePasswordBody, ChangeUsernameBody, UserPatchBody, DeleteUserBody,
                             ClientParams)
from api.models.game import GameOptions
from api.models.security import Token, LoginBody
from api.models.common import SuccessResponse, error_responses
from api.services.user import UserService

router = APIRouter(prefix='/user', tags=['user'])


@router.post(
    path='',
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary='Зарегистрировать нового пользователя',
    description='Регистрация нового пользователя. Пароль принимает в зашифрованном виде. Шифрование публичным ключем, '
                'выдаваемым сервером по ручке `get /public-key`',
    responses=error_responses()
)
async def create_user(body: LoginBody):
    return await UserService().create_user(body)


@router.get(
    path='',
    response_model=UserPublic,
    summary='Текущий пользователь',
    description='Получить текущего авторизованного пользователя',
    responses=error_responses()
)
async def get_current_user(user: RequiredAuthProvider):
    return user


@router.patch(
    path='',
    response_model=UserPublic,
    summary='Изменить данные пользователя',
    description='Изменить данные текущего пользователя. Меняет только те поля, что переданы в запросе, '
                'остальные остаются без изменений',
    responses=error_responses()
)
async def change_user(user: RequiredAuthProvider, body: UserPatchBody):
    return await UserService().change_user(user, body)


@router.put(
    path='/avatar',
    response_model=UserPublic,
    summary='Загрузить аватарку пользователя',
    description='Загрузить файл аватарки текущему пользователю',
    responses=error_responses()
)
async def change_avatar(user: RequiredAuthProvider, file: UploadFile):
    return await UserService().change_avatar(user, file)


@router.delete(
    path='/avatar',
    response_model=UserPublic,
    summary='Удалить аватарку',
    description='Удалить изображение аватарки текущего пользователя',
    responses=error_responses()
)
async def clear_avatar(user: RequiredAuthProvider):
    return await UserService().clear_avatar(user)


@router.patch(
    path='/passwd',
    response_model=SuccessResponse,
    summary='Сменить пароль пользователя',
    description='Изменить пароль текущего пользователя на новый. Требует передачи корректного текущего пароля. '
                'Пароли принимает в зашифрованном виде. Шифрование публичным ключем, выдаваемым сервером по ручке '
                '`get /public-key`. Опционально завершает все остальные активные сеансы пользователя',
    responses=error_responses()
)
async def change_password(user: RequiredAuthProvider, body: ChangePasswordBody):
    await UserService().change_password(user, body.password, body.new_password, close_sessions=body.close_sessions)
    return SuccessResponse()


@router.patch(
    path='/username',
    response_model=Token,
    summary='Изменение логина пользователя',
    description='Изменяет логин текущего пользователя на переданный. Из-за изменения логина текущий токен сессии '
                'становится недействительным, поэтому пересоздаст его и вернет новый. Все остальные активные сеансы '
                'пользователя будут завершены',
    responses=error_responses()
)
async def change_username(user: RequiredAuthProvider, body: ChangeUsernameBody):
    return await UserService().change_username(user, body.new_username)


@router.delete(
    path='',
    response_model=SuccessResponse,
    summary='Удалить текущего пользователя',
    description='Физически удаляет текущего пользователя и все его данные с сервера. Без возможности восстановления! '
                'Для подтверждения этой операции требует передачи текущего пароля (в зашифрованном виде)',
    responses=error_responses()
)
async def delete_user(user: RequiredAuthProvider, body: DeleteUserBody):
    await UserService().delete_user(user, body.password)
    return SuccessResponse()


@router.get(
    path='/params',
    response_model=ClientParams,
    summary='Получить настройки gui-клиента',
    description='Получить сохраненные на сервере настройки игрового клиента по текущему пользователю',
    responses=error_responses()
)
async def get_user_params(user: RequiredAuthProvider):
    return await UserService().get_user_params(user)


@router.put(
    path='/params',
    response_model=SuccessResponse,
    summary='Сохранить настройки gui-клиента',
    description='Сохранить на сервере настройки игрового клиента в данных текущего пользователя',
    responses=error_responses()
)
async def set_user_params(user: RequiredAuthProvider, body: ClientParams):
    await UserService().set_user_params(user, body)
    return SuccessResponse()


@router.get(
    path='/game_options',
    response_model=GameOptions,
    summary='Получить игровые договоренности',
    description='Получить сохраненные на сервере игровые договоренности по текущему пользователю',
    responses=error_responses()
)
async def get_user_game_options(user: RequiredAuthProvider):
    return await UserService().get_user_game_options(user)


@router.put(
    path='/game_options',
    response_model=SuccessResponse,
    summary='Сохранить игровые договоренности',
    description='Сохранить на сервере игровые договоренности в данных текущего пользователя',
    responses=error_responses()
)
async def set_user_game_options(user: RequiredAuthProvider, body: GameOptions):
    await UserService().set_user_game_options(user, body)
    return SuccessResponse()


@router.delete(
    path='/statistics',
    response_model=SuccessResponse,
    summary='Сброс статистики пользователя',
    description='Обнулить игровую статистику текущего пользователя',
    responses=error_responses()
)
async def reset_user_statistics(user: RequiredAuthProvider):
    await UserService().reset_user_statistics(user)
    return SuccessResponse()
