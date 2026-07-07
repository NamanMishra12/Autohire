from sqlalchemy.orm import Session


class BaseRepository:

    def __init__(self, db: Session):

        self.db = db

    def add(self, obj):

        self.db.add(obj)

        self.db.commit()

        self.db.refresh(obj)

        return obj

    def update(self, obj):
        """
        Commits pending changes on an already-tracked object
        and refreshes it from the database.
        """
        self.db.commit()

        self.db.refresh(obj)

        return obj