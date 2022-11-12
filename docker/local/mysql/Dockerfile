# Primary
FROM mysql:8.0

COPY docker/local/mysql/initdb.d /docker-entrypoint-initdb.d

RUN chmod -R +x /docker-entrypoint-initdb.d \
    && mkdir /var/log/mysql \
    && touch /var/log/mysql/mysqld.log \
    && touch /var/log/mysql/mysql-error.log \
    && touch /var/log/mysql/slow-query.log
