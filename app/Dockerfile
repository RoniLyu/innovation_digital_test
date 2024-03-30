FROM --platform=linux/amd64 surnet/alpine-wkhtmltopdf:3.17.0-0.12.6-full AS wkhtmltopdf
FROM --platform=linux/amd64 python:3.11.1-alpine3.17

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk add --no-cache \
    libstdc++ \
    libx11 \
    libxrender \
    libxext \
    libssl1.1 \
    ca-certificates \
    fontconfig \
    freetype \
    ttf-dejavu \
    ttf-droid \
    ttf-freefont \
    ttf-liberation \
    # more fonts
  && apk add --no-cache --virtual .build-deps \
    msttcorefonts-installer \
  # Install microsoft fonts
  && update-ms-fonts \
  && fc-cache -f \
  # Clean up when done
  && rm -rf /tmp/* \
  && apk del .build-deps

# install psycopg2 dependencies
RUN apk add --no-cache postgresql-dev gcc python3-dev musl-dev linux-headers g++ openssl

COPY --from=wkhtmltopdf /bin/wkhtmltopdf /bin/wkhtmltopdf

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh


COPY . .

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]