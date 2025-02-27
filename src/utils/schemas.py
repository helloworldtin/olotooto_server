from pydantic import BaseModel


class GeneralResponseModel(BaseModel):
    message: str
