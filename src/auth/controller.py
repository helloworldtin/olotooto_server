from fastapi import BackgroundTasks, UploadFile
from sqlmodel import select
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession

from sqlalchemy.exc import IntegrityError

from datetime import timedelta
from uuid import UUID

from .schemas import (
    CreteUserModel,
    VerifyOTPDataModel,
    LoginDataModel,
    ChangePasswordModel,
    UpdateDataModel,
    UpdatePasswordModel,
)
from .utils import (
    hash_password,
    verify_hashed_password,
    generate_otp,
    create_jwt_token,
)


from src.database.models import User, UserLinkModel
from src.database.cloudinary import upload_file, delete_file
from src.database.redis import (
    put_data_in_redis,
    get_data_from_redis,
    delete_data_from_redis,
)
from src.utils.mail import send_mail
from src.exceptions.exceptions import (
    UserAlreadyExist,
    UserNameAlreadyTaken,
    InterServerException,
    UserNotFound,
    InvalidOTP,
    InvalidCredentials,
    InvalidToken,
    InvalidOperation,
    AlreadyFollowed,
)

USER_PROFILE_FOLDER = "users/profile/"


class AuthController:
    async def get_user_by_email(self, email: str, session: AsyncSession) -> User | None:
        try:
            statement = select(User).where(User.email == email)
            user = await session.exec(statement=statement)
            return user.first()
        except Exception as e:
            print(e)
            raise InterServerException()

    async def get_user_by_username(
        self, username: str, session: AsyncSession
    ) -> User | None:
        try:
            statement = select(User).where(User.username == username)
            user = await session.exec(statement=statement)
            return user.first()
        except Exception as e:
            print(e)
            raise InterServerException()

    async def check_user_exist_by_email(
        self, email: str, session: AsyncSession
    ) -> bool:
        try:
            user = await self.get_user_by_email(email, session)
            return user is not None
        except Exception as e:
            print(e)
            raise InterServerException()

    async def create_user(
        self,
        user_data: CreteUserModel,
        session: AsyncSession,
        background_task: BackgroundTasks,
    ) -> User:

        try:
            # check if user exist
            user: User = await self.get_user_by_email(user_data.email, session=session)
            if user:
                raise UserAlreadyExist()
            # check if user with same username exist
            user = await self.get_user_by_username(user_data.username, session)
            if user:
                raise UserNameAlreadyTaken()
            # creating a user
            new_user = User(**user_data.model_dump())

            # hash user password
            new_user.hashed_password = hash_password(user_data.password)

            # upload file to the cloudinary
            new_user.profile_url = await upload_file(
                user_data.profile_file,
                USER_PROFILE_FOLDER,
            )
            otp_code = generate_otp()

            # save opt in redis
            await put_data_in_redis(key=new_user.email, data=otp_code)

            # adding data to database
            session.add(new_user)
            await session.commit()

            # send otp code to user email for verification
            background_task.add_task(
                send_mail,
                new_user.email,
                "Your OTP verification Code",
                f"Hey welcome to our app <br> your otp code is: <b>{otp_code}</b>.<br>Don't share to any one",
            )
            return new_user
        except (UserAlreadyExist, UserNameAlreadyTaken):
            raise
        except Exception as e:
            print(e)
            raise InterServerException()

    async def verify_otp(
        self, otp_verification_data: VerifyOTPDataModel, session: AsyncSession
    ) -> dict:
        try:
            user = await self.get_user_by_email(otp_verification_data.email, session)
            if not user:
                raise UserNotFound()

            otp = await get_data_from_redis(otp_verification_data.email)

            if not otp or not otp == otp_verification_data.otp:
                raise InvalidOTP()
            await delete_data_from_redis(otp_verification_data.email)
            return {"message": "OTP verified successfully"}
        except (UserNotFound, InvalidOTP):
            raise  # it is re-rasing the same exception
        except Exception as e:
            print(e)
            raise InterServerException()

    async def login(self, login_data: LoginDataModel, session: AsyncSession) -> dict:
        try:

            user = await self.get_user_by_email(login_data.email, session)
            if not user:
                raise InvalidCredentials()
            if not verify_hashed_password(login_data.password, user.hashed_password):
                raise InvalidCredentials()
            data = {
                "uid": str(user.uid),
                "username": user.username,
            }
            access_token = create_jwt_token(data=data)
            refresh_token = create_jwt_token(
                data=data,
                exp_time=timedelta(days=7),
                refresh=True,
            )
            return {
                "message": "operation successful",
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        except InvalidCredentials:
            raise
        except Exception as e:
            print(e)
            raise InterServerException()

    async def send_password_forgot_request(
        self,
        email: str,
        session: AsyncSession,
        bg_task: BackgroundTasks,
    ) -> dict:

        try:
            user = await self.get_user_by_email(email, session)
            if not user:
                raise UserNotFound()
            otp = generate_otp()
            bg_task.add_task(
                send_mail,
                email,
                "Your OTP verification Code",
                f"Hey don't worry <br> your otp code to change password is: <b>{otp}</b>.<br> Don't share to any one",
            )
            await put_data_in_redis(email, otp)
            return {"message": "check you email we have sent otp to change password."}
        except UserNotFound:
            raise
        except Exception as e:
            print(e)
            raise InterServerException()

    async def change_password_forgot(
        self, password_change_data: ChangePasswordModel, session: AsyncSession
    ) -> User:
        try:
            user: User | None = await self.get_user_by_email(
                password_change_data.email, session
            )
            if user is None:
                raise UserNotFound()  # not needed but for safety
            new_hash_password = hash_password(password_change_data.new_password)
            user.hashed_password = new_hash_password
            await session.commit()
            await session.refresh(user)
            return user

        except UserNotFound:
            raise
        except Exception as e:
            print(e)
            raise InterServerException()

    async def get_new_tokens(self, user_data: dict, session: AsyncSession) -> dict:
        try:
            user_email = user_data["user_data"]["username"]
            if not user_email:
                raise InvalidToken()
            user = await self.get_user_by_username(user_email, session)
            if not user:
                raise InvalidToken()
            data = {
                "uid": str(user.uid),
                "username": user.username,
            }
            access_token = create_jwt_token(data=data)
            refresh_token = create_jwt_token(
                data=data,
                exp_time=timedelta(days=7),
                refresh=True,
            )
            return {
                "message": "renew tokens successfully",
                "access_token": access_token,
                "refresh_token": refresh_token,
            }

        except InvalidToken:
            raise
        except Exception as e:
            print(e)
            raise InterServerException()

    async def update_profile(
        self, user_data: dict, new_profile_file: UploadFile, session: AsyncSession
    ) -> User:
        try:
            username = user_data["user_data"]["username"]
            user = await self.get_user_by_username(username, session)
            if user is None:
                raise UserNotFound()
            # delete user old profile
            await delete_file(user.profile_url, USER_PROFILE_FOLDER)
            new_profile_url = await upload_file(new_profile_file, USER_PROFILE_FOLDER)
            user.profile_url = new_profile_url
            await session.commit()
            await session.refresh(user)
            return user
        except UserNotFound:
            raise
        except Exception as e:
            print(e)
            raise InterServerException()

    async def update_user_data(
        self,
        update_data: UpdateDataModel,
        user_data: dict,
        session: AsyncSession,
    ):
        try:
            username = user_data["user_data"]["username"]
            user = await self.get_user_by_username(username, session)
            if not user:
                raise InvalidToken()
            # looping though all the element got form request
            for k, v in update_data.model_dump().items():
                # checking if user give same as in db
                if v is not None and getattr(user, k) != v:
                    # special check for username
                    if k == "username":
                        if await self.get_user_by_username(v, session):
                            raise UserNameAlreadyTaken()
                    # replacing value if change
                    setattr(user, k, v)
                    await session.commit()
                    await session.refresh(user)
            return user

        except (InvalidToken, UserNameAlreadyTaken):
            raise
        except Exception as e:
            print(e)
            raise InterServerException()

    async def update_password(
        self,
        update_password_data: UpdatePasswordModel,
        user_data: dict,
        session: AsyncSession,
    ):
        try:
            username = user_data["user_data"]["username"]
            user: User = await self.get_user_by_username(username, session)
            if not User:
                raise InvalidToken()
            if not verify_hashed_password(
                update_password_data.old_password, user.hashed_password
            ):
                raise InvalidCredentials()
            new_password_hashed = hash_password(update_password_data.new_password)
            if verify_hashed_password(
                update_password_data.new_password, user.hashed_password
            ):
                return {"message": "Same password no need to change"}
            user.hashed_password = new_password_hashed
            await session.commit()
            return {"message": "Password updated successfully"}
        except (InvalidToken, InvalidCredentials):
            raise
        except Exception as e:
            print(e)
            raise InterServerException()

    async def search_users(self, search_key: str, session: AsyncSession) -> list[User]:
        try:
            statement = select(User).where(User.full_name.ilike(f"{search_key}%"))
            users = await session.exec(statement)
            return users.all()
        except Exception as e:
            print(e)
            raise InterServerException()

    async def get_current_user(self, user_data: dict, session: AsyncSession) -> User:
        try:
            username = user_data["user_data"]["username"]
            statement = (
                select(User)
                .where(User.username == username)
                .options(selectinload(User.followers))
                .options(selectinload(User.following))
            )

            result = await session.exec(statement)
            user = result.first()

            if not user:
                raise InvalidToken()
            return user
        except InvalidToken:
            raise
        except Exception as e:
            print(e)
            raise InterServerException()

    async def follow_user(
        self,
        user_data: dict,
        following_to_username: str,
        session: AsyncSession,
    ) -> dict:
        try:
            following_to_user = await self.get_user_by_username(
                following_to_username, session
            )
            if not following_to_user:
                raise UserNotFound()
            current_user_uid = UUID(user_data["user_data"]["uid"])
            if following_to_user.uid == current_user_uid:
                raise InvalidOperation()
            new_link = UserLinkModel(
                follower_uid=current_user_uid, user_uid=following_to_user.uid
            )
            session.add(new_link)
            await session.commit()
            return {"message": f"You are following to {following_to_user.full_name} "}
        except IntegrityError:
            raise AlreadyFollowed()

        except (UserNotFound, InvalidOperation):
            raise
        except Exception as e:
            print(e)
            raise InterServerException()

    async def unfollow_user(
        self,
        user_data: dict,
        following_to_username: str,
        session: AsyncSession,
    ) -> dict:
        try:
            un_following_user = await self.get_user_by_username(
                following_to_username, session
            )
            if un_following_user is None:
                raise UserNotFound()
            current_user_uid = UUID(user_data["user_data"]["uid"])
            get_link_statement = select(UserLinkModel).where(
                UserLinkModel.follower_uid == current_user_uid
                and UserLinkModel.user_uid == un_following_user.uid
            )
            result = await session.exec(get_link_statement)
            await session.delete(result.first())
            await session.commit()
            return {
                "message": f"successfully unfollowed to {un_following_user.full_name} "
            }

        except UserNotFound:
            raise

        except Exception as e:
            print(e)
            raise InterServerException()

    async def delete_user(self, user_data: dict, session: AsyncSession) -> None:
        try:
            username = user_data["user_data"]["username"]
            user = await self.get_user_by_username(username, session)
            if not User:
                raise InvalidToken()
            await session.delete(user)
            await session.commit()
        except InvalidToken:
            raise
        except Exception as e:
            print(e)
            raise InterServerException()


auth_controller = AuthController()
