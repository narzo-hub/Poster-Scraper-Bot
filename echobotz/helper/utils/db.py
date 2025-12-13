from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
from pymongo.server_api import ServerApi

from config import Config
from ... import LOGGER, user_data


class _DbManager:
    def __init__(self):
        self._return = True
        self._conn = None
        self.db = None

    async def _connect(self):
        try:
            if self._conn is not None:
                await self._conn.close()
            if not Config.DATABASE_URL:
                LOGGER.error("DATABASE_URL missing in Config")
                self.db = None
                self._return = True
                self._conn = None
                return
            self._conn = AsyncIOMotorClient(
                Config.DATABASE_URL, server_api=ServerApi("1")
            )
            self.db = self._conn[Config.DATABASE_NAME]
            self._return = False
        except PyMongoError as e:
            LOGGER.error(f"Error in DB connection: {e}")
            self.db = None
            self._return = True
            self._conn = None

    async def _ensure(self):
        if self._return or self.db is None:
            await self._connect()
        return not self._return and self.db is not None

    async def _disconnect(self):
        self._return = True
        if self._conn is not None:
            await self._conn.close()
        self._conn = None
        self.db = None

    async def _update_user_data(self, user_id: int):
        if not await self._ensure():
            return
        data = user_data.get(user_id, {})
        try:
            await self.db.auth.update_one(
                {"_id": user_id},
                {"$set": data},
                upsert=True,
            )
        except PyMongoError as e:
            LOGGER.error(f"_update_user_data error: {e}")

    async def _load_all(self):
        if not await self._ensure():
            return
        try:
            cursor = self.db.auth.find({})
            async for doc in cursor:
                uid = doc.get("_id")
                if uid is None:
                    continue
                data = {k: v for k, v in doc.items() if k != "_id"}
                user_data[uid] = data
            LOGGER.info("Database loaded from MongoDB")
        except PyMongoError as e:
            LOGGER.error(f"_load_all error: {e}")

    async def _get_pm_uids(self):
        if not await self._ensure():
            return []
        try:
            return [doc["_id"] async for doc in self.db.pm_users.find({})]
        except PyMongoError as e:
            LOGGER.error(f"_get_pm_uids error: {e}")
            return []

    async def _set_pm_user(self, user_id: int):
        if not await self._ensure():
            return
        try:
            if not await self.db.pm_users.find_one({"_id": user_id}):
                await self.db.pm_users.insert_one({"_id": user_id})
                LOGGER.info(f"New PM User Added : {user_id}")
        except PyMongoError as e:
            LOGGER.error(f"_set_pm_user error: {e}")

    async def _rm_pm_user(self, user_id: int):
        if not await self._ensure():
            return
        try:
            await self.db.pm_users.delete_one({"_id": user_id})
        except PyMongoError as e:
            LOGGER.error(f"_rm_pm_user error: {e}")


database = _DbManager()
