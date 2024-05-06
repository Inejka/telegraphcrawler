import sys
from datetime import datetime
from typing import Any

import scrapy
import scrapy.http
import scrapy.http.response
import temp_d
from scrapy.linkextractors import LinkExtractor
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session


class RandomIndexer(scrapy.Spider):
    name = "random_indexer"
    base_url = "https://telegra.ph/"
    media_base_url = "https://telegra.ph"
    year = "2024"
    max_days = 366

    for x in sys.argv:
        if "ignore_errors=" in x:
            custom_settings = {
                "SPIDER_MIDDLEWARES": {
                    "scrapy.spidermiddlewares.httperror.HttpErrorMiddleware": None,
                    "telegraph.middlewares.MyHttpErrorMiddleware": 50,
                },
            }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.session = Session(temp_d.get_engine())
        self.link_extractor = LinkExtractor()
        if not hasattr(self, "max_date_depth"):
            self.max_date_depth = 5
        else:
            self.max_date_depth = int(self.max_date_depth)
        self.hashed_pages = set()

    def start_requests(self):  # noqa: ANN201
        if hasattr(self, "words"):
            for word in self.words.split(" "):
                for day_of_year in range(1, RandomIndexer.max_days + 1):
                    url_creation_date = datetime.strptime(RandomIndexer.year + "-" + str(day_of_year), "%Y-%j")
                    url = RandomIndexer.base_url + word + url_creation_date.strftime("-%m-%d")
                    rq = scrapy.Request(url=url, callback=self.parse)
                    rq.counter = 0
                    rq.url_creation_date = url_creation_date
                    rq.keywords = word
                    yield rq
                    for next_url, counter in self.generate_next_urls(url + "-1"):
                        rq = scrapy.Request(url=next_url, callback=self.parse)
                        rq.counter = counter
                        rq.url_creation_date = url_creation_date
                        rq.keywords = word
                        yield rq
            return

    def generate_next_urls(self, base_url: str):  # noqa: ANN201
        index_of_separator = base_url.rfind("-")
        start_num = int(base_url[index_of_separator + 1 :])
        base_url = base_url[: index_of_separator + 1]
        for i in range(1, self.max_date_depth + 1):
            yield (base_url + str(start_num + i)), (start_num + i)

    def parse(self, response: scrapy.http.response):  # noqa: ANN201
        page_content = response.xpath('//*[@id="_tl_editor"]').get()
        hash_of_a_page = hash(page_content)
        if hash_of_a_page not in self.hashed_pages:
            self.hashed_pages.add(hash_of_a_page)

            stmt = insert(temp_d.AliveUrl).values(
                {
                    "url": response.url,
                    "keywords": response.request.keywords,
                    "title": response.xpath("/html/body/div[1]/div[1]/main/header/h1/text()").get(),
                    "creation_date": datetime.strptime(
                        response.xpath("/html/body/div[1]/div[1]/main/header/address/time/@datetime").get(),
                        "%Y-%m-%dT%H:%M:%S%z",
                    ),
                    "counter": response.request.counter,
                    "day_of_year": response.request.url_creation_date,
                    "plain_html": response.text,
                    "author": response.xpath("/html/body/div[1]/div[1]/main/header/address/a/text()").get(),
                    "crosslinks_count": len(self.link_extractor.extract_links(response)),
                    "images_count": len(response.css("img")),
                    "video_count": len(response.css("video")),
                    "content_len": len(page_content),
                    "found_date": datetime.now(),
                }
            )
            stmt = stmt.on_conflict_do_nothing(index_elements=["url"])
            self.session.execute(stmt)

            for i in response.css("img::attr(src)").getall():
                stmt = insert(temp_d.Images).values(
                    image_hash=None,
                    source_url=response.url,
                    img_url=self.media_base_url + i if "http" not in i else i,
                    status=temp_d.MediaStatus.founded.value,
                    local_path=None,
                    tags=None,
                )
                stmt = stmt.on_conflict_do_nothing(index_elements=["img_url"])
                self.session.execute(stmt)

            for i in response.css("video::attr(src)").getall():
                stmt = insert(temp_d.Videos).values(
                    video_hash=None,
                    source_url=response.url,
                    video_url=self.media_base_url + i if "http" not in i else i,
                    status=temp_d.MediaStatus.founded.value,
                    local_path=None,
                    tags=None,
                )
                stmt = stmt.on_conflict_do_nothing(index_elements=["video_url"])
                self.session.execute(stmt)

            self.session.commit()

        for next_url, counter in self.generate_next_urls(response.url):
            rq = scrapy.Request(url=next_url, callback=self.parse)
            rq.counter = counter
            rq.url_creation_date = response.request.url_creation_date
            rq.keywords = response.request.keywords
            yield rq
