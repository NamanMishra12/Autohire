from app.database.base import Base
from app.database.session import engine

# Import all models so they register with Base.metadata
# before create_all() runs. This import is required even
# though `app.models` isn't referenced directly below.
from app.models import User, Resume


def init_database():
    Base.metadata.create_all(bind=engine)