from pydantic.v1 import BaseSettings


class Config(BaseSettings):
    MAX_K: int = 8
    MAX_LEN: int = 10**MAX_K
    MAX_BATCH_SIZE: int = 10000


config = Config()
