from sqlalchemy import VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from app.config.track_type import track_type_settings
from app.core.types import TrackTypes

from .base_model import BaseModel


class TrackType(BaseModel):
    __tablename__ = "track_type"

    name: Mapped[TrackTypes] = mapped_column(VARCHAR(256), nullable=False, unique=True)

    @property
    def settings(self):
        return track_type_settings[self.name]
