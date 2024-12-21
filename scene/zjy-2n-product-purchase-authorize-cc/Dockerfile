FROM trenx1999/of-watchdog:latest-dev-x86_64 as watchdog

FROM node:10.12.0-alpine

COPY --from=watchdog ./fwatchdog /usr/bin/fwatchdog
RUN chmod +x /usr/bin/fwatchdog

RUN apk --no-cache add mysql-client strace curl

RUN addgroup -S app && adduser -S -g app app && mkdir -p /home/app
USER app

WORKDIR /home/app
COPY . .
RUN npm install
RUN npm install mysql  

ENV fprocess="node index.js"
ENV mode="http"
ENV http_upstream_url="http://127.0.0.1:3000"


ENV DB_HOST="cc-db"               
ENV DB_USER="root"                
ENV DB_PASS="pass"                  
ENV DB_NAME="helloRetail"         


ENV exec_timeout="0s"

HEALTHCHECK --interval=5s CMD [ -e /tmp/.lock ] || exit 1
CMD ["fwatchdog"]
