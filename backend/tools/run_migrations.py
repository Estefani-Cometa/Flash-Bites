from alembic import command
from alembic.config import Config

from app.db import normalize_database_url
from app.core.config import settings


if __name__ == "__main__":
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", normalize_database_url(settings.database_url).replace("%", "%%"))
    command.upgrade(config, "head")
