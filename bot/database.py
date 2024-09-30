import asyncio
import os
import sys

from motor.motor_asyncio import AsyncIOMotorClient

DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")
DATABASE_NAME = os.getenv("DATABASE_NAME")

if DB_CONNECTION_STRING is None or DATABASE_NAME is None:
    sys.exit("Incorrect database connection parameters")

client = AsyncIOMotorClient(DB_CONNECTION_STRING)
db = client.get_database(DATABASE_NAME)
user_preferences_collection = db.get_collection("user_preferences")


# Асинхронная функция для получения данных
async def fetch_data():
    async for document in user_preferences_collection.find({}):
        print(document)


# Запускаем асинхронную функцию через asyncio
async def main():
    await fetch_data()


if __name__ == "__main__":
    asyncio.run(main())
