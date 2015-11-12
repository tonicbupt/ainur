from werkzeug.utils import cached_property

from base import db, Base


class BaseImage(Base):
    __tablename__ = 'base_image'

    name = db.Column(db.String(64), unique=True, nullable=False)
