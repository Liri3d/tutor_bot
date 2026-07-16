# from typing import Optional
# from sqlalchemy import select, and_
# from sqlalchemy.ext.asyncio import AsyncSession

# from .models import User

# async def db_create_user(
#     session: AsyncSession,
#     telegram_id: int,
#     role: str,
#     username: Optional[str] = None,
#     first_name: Optional[str] = None
# ) -> User:
#     """Создать нового пользователя"""
#     user = User(
#         telegram_id=telegram_id,
#         username=username,
#         first_name=first_name,
#         role=role
#     )
#     session.add(user)
#     await session.commit()
#     await session.refresh(user)
#     return user

# async def db_create_user_with_password(
#     session: AsyncSession,
#     login: str,
#     password_hash: str,
#     first_name: str,
#     role: str = "tutor"
# ) -> User:
#     """Создать пользователя с логином и паролем (без Telegram)"""
#     user = User(
#         login=login,
#         password_hash=password_hash,
#         first_name=first_name,
#         role=role,
#         telegram_id=None,  # ← Явно указываем None
#         username=None
#     )
#     session.add(user)
#     await session.commit()
#     await session.refresh(user)
#     return user

# async def db_get_user_by_telegram_id(
#     session: AsyncSession,
#     telegram_id: int
# ) -> Optional[User]:
#     """Получить пользователя по Telegram ID"""
#     stmt = select(User).where(User.telegram_id == telegram_id)
#     result = await session.execute(stmt)
#     return result.scalar_one_or_none()

# async def db_get_user_by_id(
#     session: AsyncSession,
#     user_id: int
# ) -> Optional[User]:
#     """Получить пользователя по ID"""
#     stmt = select(User).where(User.id == user_id)
#     result = await session.execute(stmt)
#     return result.scalar_one_or_none()

# async def db_get_user_by_login(
#     session: AsyncSession,
#     login: str
# ) -> Optional[User]:
#     """Получить пользователя по логину"""
#     stmt = select(User).where(User.login == login)
#     result = await session.execute(stmt)
#     return result.scalar_one_or_none()