FROM mysql:5.6

ADD init.sql /data/application/init.sql

COPY . /var/lib/mysql-files

RUN chown mysql:mysql /var/lib/mysql-files/test.txt
