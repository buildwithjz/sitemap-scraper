FROM python:3.7

RUN pip3 install ultimate-sitemap-parser

RUN mkdir -p /sitemaps-by-domain

COPY . /app

WORKDIR /app

ENTRYPOINT ["sh","-c","python3 sitemap-scraper.py $TOPIC $SEARCH_DOMAIN"]

# docker build . -t sitemap-scraper:latest
# docker run -e TOPIC=docker -e SEARCH_DOMAIN=https://docs.docker.com sitemap-scraper -v /sitemaps-by-domain:/sitemaps-by-domain

