import os
from motor.motor_asyncio import AsyncIOMotorClient,AsyncIOMotorDatabase
import logging
from typing import cast
from pymongo import IndexModel, ASCENDING
from pymongo.errors import DuplicateKeyError

logger = logging.getLogger("app")

class DB:
    client: AsyncIOMotorClient|None = None
    db: AsyncIOMotorDatabase|None = None

    

    @classmethod
    def connect_db(cls):
        if cls.client is None:
            

            print(os.getenv('DB_PORT'),os.getenv('DB_USERNAME'),os.getenv('DB_PASSWORD'))
            cls.client = AsyncIOMotorClient(
                host=os.getenv('DB_HOST'),
                port=int(os.getenv('DB_PORT', '27017')),
                username=os.getenv('DB_USERNAME','qsar_user'),
                password=os.getenv('DB_PASSWORD','qsar9527')
            )
            cls.db = cls.client['qsarDB']
            logger.info("Connected to MongoDB")

    @classmethod
    async def setup_db_index(cls): 
        # user = {
        #     "user": "qsar_user",
        #     "pwd": "qsar9527",
        #     "roles": [
        #         {"role": "readWrite", "db": "qsarDB"}
        #     ]
        # }
        # if cls.client is not None:
        #     try:
        #         admin_db=cls.client.admin
        #         # Check if the user already exists
        #         user_exists = await admin_db.command("usersInfo", {"user": user["user"], "db": "qsarDB"})
        #         if not user_exists["users"]:
        #             # Create the user if it does not exist
        #             await admin_db.command("createUser", user["user"], pwd=user["pwd"], roles=user["roles"])
        #             print("User created successfully")
        #         else:
        #             print("User already exists")
        #     except DuplicateKeyError:
        #         print("User already exists")
        #     except Exception as e:
        #         print(f"An error occurred: {e}")
        
        if cls.db is not None:
            # 建立unique index
            indexes_user=[IndexModel([("username", ASCENDING)], unique=True)]
            await cls.db['user'].create_indexes(indexes_user)

            # 建立unique index
            indexes_black_tokens = [
                IndexModel([("token", ASCENDING)], unique=True),
                IndexModel([("expireAt", ASCENDING)], expireAfterSeconds=0)  # TTL索引: 自动过期删除
            ]
            await cls.db['black_tokens'].create_indexes(indexes_black_tokens)
        else:
            cls.connect_db()
            

    @classmethod
    async def close_db(cls):
        if cls.client is not None:
            cls.client.close()
            cls.client = None
            cls.db = None
            logger.info("Disconnected from MongoDB")

    @classmethod
    async def get_db(cls) -> AsyncIOMotorDatabase:
        if cls.db is None:
            cls.connect_db()
        return cast(AsyncIOMotorDatabase, cls.db)
    
    @classmethod
    async def check_db(cls) -> bool :
        try:
            if cls.client is None:
                return False
            await cls.client["test"].command('ping')
            logger.info("MongoDB is ok")
            return True
        except Exception as e:
            logger.error(str(e))
            return False
        
