import pytest
import logging
from config.settings import settings

@pytest.fixture(scope="session",autouse=True)
def setup_logging():
    """初始化日志"""
    logging.basicConfig(level=logging.DEBUG)
    yield