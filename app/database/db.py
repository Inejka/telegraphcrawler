import datetime
import os
from enum import Enum

from sqlalchemy import TIMESTAMP, Column, Engine, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class MediaStatus(Enum):
    founded = 0
    alive = 1
    dead = 2
    failed_to_parse = 3


class AliveUrl(Base):
    __tablename__ = "alive_urls"

    url: Mapped[str] = mapped_column(String(8192), primary_key=True)
    keywords: Mapped[str] = mapped_column(String(8192))
    title: Mapped[str] = mapped_column(String(8192))
    creation_date = Column(TIMESTAMP, nullable=False)
    counter: Mapped[int]
    day_of_year: Mapped[datetime.date]
    plain_html = Column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(8192), nullable=True)
    crosslinks_count: Mapped[int]
    images_count: Mapped[int]
    video_count: Mapped[int]
    content_len: Mapped[int]
    found_date = Column(TIMESTAMP, nullable=False)

    def items(self) -> dict:
        return {
            "url": self.url,
            "keywords": self.keywords,
            "title": self.title,
            "creation_date": self.creation_date,
            "counter": self.counter,
            "day_of_year": self.day_of_year,
            "plain_html": self.plain_html,
            "author": self.author,
            "crosslinks_count": self.crosslinks_count,
            "images_count": self.images_count,
            "video_count": self.video_count,
            "content_len": self.content_len,
            "found_date": self.found_date,
        }.items()


class Images(Base):
    __tablename__ = "images"

    img_url: Mapped[str] = mapped_column(String(8192), primary_key=True)
    image_hash: Mapped[str] = mapped_column(String(32), nullable=True)
    source_url: Mapped[str] = mapped_column(String(8192))
    status: Mapped[int]

    local_path: Mapped[str] = mapped_column(String(8192), nullable=True)
    tags = Column(Text, nullable=True)

    def items(self) -> dict:
        return {
            "image_hash": self.image_hash,
            "source_url": self.source_url,
            "img_url": self.img_url,
            "status": self.status,
            "local_path": self.local_path,
            "tags": self.tags,
        }.items()


class Videos(Base):
    __tablename__ = "videos"

    video_url: Mapped[str] = mapped_column(String(8192), primary_key=True)
    video_hash: Mapped[str] = mapped_column(String(32), nullable=True)
    source_url: Mapped[str] = mapped_column(String(8192))
    status: Mapped[int]

    local_path: Mapped[str] = mapped_column(String(8192), nullable=True)
    tags = Column(Text, nullable=True)

    def items(self) -> dict:
        return {
            "video_hash": self.video_hash,
            "source_url": self.source_url,
            "video_url": self.video_url,
            "status": self.status,
            "local_path": self.local_path,
            "tags": self.tags,
        }.items()


class Hashes(Base):
    __tablename__ = "hashes"

    content_hash: Mapped[str] = mapped_column(
        String(32), nullable=False, primary_key=True
    )


engine = None
def get_engine() -> Engine:
    global engine
    if engine is not None:
        return engine
    connection_str = (
        "postgresql+psycopg2://%(user)s:%(pass)s@%(host)s:%(port)d/%(db)s"
        % {
            "user": os.environ["POSTGRES_USER"],
            "pass": os.environ["POSTGRES_PASSWORD"],
            "host": os.environ["DATABASE_HOST"],
            "port": int(os.environ["POSTGRES_PORT"]),
            "db": os.environ["POSTGRES_USER"],
        }
    )
    try:
        engine = create_engine(connection_str)
        engine.connect()
        Base.metadata.create_all(engine)
        return engine
    except Exception as e:
        raise(e)


if __name__ == "__main__":
    from sqlalchemy import select

    session = Session(engine)
    stmt = select(Images).where()

    for user in session.scalars(stmt):
        print(user.img_url)
