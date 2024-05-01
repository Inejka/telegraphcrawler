FROM python:3.11.9-slim-bookworm
COPY /app/requirements.txt ./app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./app /app
COPY ./app/database/db.py /app/scrapy_spiders/temp_d.py
CMD [ "textual", "run","--dev","/app/app.py"]