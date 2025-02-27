import cloudinary
import cloudinary.uploader as uploader
from fastapi import UploadFile

import asyncio

from src.config import Config
from src.exceptions.exceptions import InterServerException

config = cloudinary.config(
    cloud_name=Config.CLOUD_NAME,
    api_key=Config.CLOUDINARY_API_KEY,
    api_secret=Config.CLOUDINARY_API_SECRET,
    secure=True,
)


async def upload_file(file: UploadFile, folder_dir: str) -> str:
    try:
        # Run the blocking uploader function in a separate thread
        result: dict = await asyncio.to_thread(
            uploader.upload, file.file, folder=folder_dir
        )
        return result["secure_url"]
    except Exception as e:
        print(f"Error while uploading file: {e}")
        raise InterServerException()


async def delete_file(url: str, folder_path: str) -> None:
    try:
        # sample url sample is public id
        # https://res.cloudinary.com/demo/image/upload/v1612312323/sample.jpg
        public_id = f"{folder_path}{url.split("/")[-1].split(".")[0]}"
        result: dict = await asyncio.to_thread(uploader.destroy, public_id)
        if result["result"] != "ok":
            raise Exception("Error wile deleting file")
        return None
    except Exception as e:
        print(f"Error while deleting file: {e}")
        raise InterServerException()
