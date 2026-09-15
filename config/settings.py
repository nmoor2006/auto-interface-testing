import os
from pathlib import Path

class Settings:
    BASE_DIR=Path(__file__).resolve().parent.parent#resolve()是把文件路径转化为绝对路径
    DATA_DIR=BASE_DIR/"datas"
    REPORT_DIR=BASE_DIR/"report"
    LOG_DIR=BASE_DIR/"logs"
    ENV=os.getenv("TEST_ENV","test")#默认环境为test

settings=Settings()