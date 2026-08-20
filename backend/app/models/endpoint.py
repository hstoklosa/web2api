from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Endpoint(Base):
    __tablename__ = "endpoints"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    url: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    json_schema: Mapped[dict[str, Any]] = mapped_column(JSONB)
