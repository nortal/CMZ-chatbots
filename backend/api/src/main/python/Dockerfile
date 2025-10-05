FROM python:3-alpine

# Update Alpine packages to fix OpenSSL CVEs (CVE-2025-9230, CVE-2025-9231, CVE-2025-9232)
# Requires libssl3 and libcrypto3 >= 3.5.4-r0
RUN apk update && apk upgrade --no-cache

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

EXPOSE 8080

ENTRYPOINT ["python3"]

CMD ["-m", "openapi_server"]