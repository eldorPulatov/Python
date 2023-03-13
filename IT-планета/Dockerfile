FROM alpine:latest

RUN apk update && apk add sqlite

COPY wonderland.db /mydb.db

CMD ["sqlite3", "/wonderland.db"]