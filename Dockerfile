FROM python:3.7

RUN pip3 install ultimate-sitemap-parser

RUN mkdir -p /sitemaps-by-domain

COPY . /app

WORKDIR /app

ENTRYPOINT ["sh","-c","python3 sitemap-scraper.py"]