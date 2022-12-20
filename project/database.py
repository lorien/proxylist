from typing import Any

from pymongo import MongoClient
from pymongo.database import Database

from project.config import get_config


def connect_db() -> Database[Any]:
    config = get_config()
    conn = MongoClient(**config["mongodb"]["connection"])
    return conn[config["mongodb"]["dbname"]]
