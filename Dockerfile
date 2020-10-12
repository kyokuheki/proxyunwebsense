FROM python:3-alpine
LABEL maintainer="Kenzo Okuda <kyokuheki@gmail.com>"

RUN set -x \
 && apk add --no-cache --virtual .build-deps gcc libc-dev libxml2-dev libxslt-dev \
 && apk add --no-cache libxslt \
 && pip3 install requests lxml \
 && apk del .build-deps \
 && rm -rf /root/.cache/pip

COPY ./proxyunwebsense.py /proxyunwebsense.py
RUN chmod a+rx /proxyunwebsense.py
ENTRYPOINT ["/proxyunwebsense.py"]
CMD ["-h"]
