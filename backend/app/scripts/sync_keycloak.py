import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.core.models import User
from app.core.services import keycloak_service
from app.util.logger import logger


class Syncer:
    def __init__(self, session: AsyncSession):
        self.session = session
        self._users_app = None
        self._users_keycloak = None

    async def init_users(self):
        self._users_app = list((await self.session.scalars(select(User))).unique())
        self._users_keycloak = keycloak_service.client.get_users()

    @property
    def users_in_app(self):
        assert self._users_app is not None, "Call init_users first"
        return self._users_app

    @property
    def users_in_keycloak(self):
        assert self._users_keycloak is not None, "Call init_users first"
        return self._users_keycloak

    @property
    def usernames_in_app(self):
        return set(u.name for u in self.users_in_app)

    @property
    def usernames_in_keycloak(self) -> set[str]:
        return set(u["username"] for u in self.users_in_keycloak)

    def remove_orphan_keycloak_users(self):
        usernames_in_keycloak_not_in_app = self.usernames_in_keycloak - self.usernames_in_app

        for username in usernames_in_keycloak_not_in_app:
            logger.info(f"Deleting user '{username}' from Keycloak because it is not in the app database")
            keycloak_service.delete_user(username)

    def list_orphan_app_users(self):
        usernames_in_app_not_in_keycloak = self.usernames_in_app - self.usernames_in_keycloak
        for username in usernames_in_app_not_in_keycloak:
            logger.warning(f"User '{username}' is in the app database but not in Keycloak")


async def main():
    async with async_session.begin() as session:
        syncer = Syncer(session)
        await syncer.init_users()
        syncer.remove_orphan_keycloak_users()
        syncer.list_orphan_app_users()


if __name__ == "__main__":
    asyncio.run(main())
