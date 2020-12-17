FROM python:3.7

RUN pip3 install ultimate-sitemap-parser
RUN pip3 install pymongo

RUN mkdir -p /sitemaps-by-domain

COPY . /app

WORKDIR /app

ENTRYPOINT ["sh","-c","python3 sitemap_scraper.py"]