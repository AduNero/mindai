# Dev-only TLS-terminating proxy in front of the backend's OIDC endpoints.
# See nginx.conf for why this exists. The self-signed cert is generated at
# build time (not committed — a fresh one is fine, it's dev-only and never
# trusted by anything outside this compose network).
FROM nginx:1.27-alpine

RUN apk add --no-cache openssl curl \
    && mkdir -p /etc/nginx/certs \
    && openssl req -x509 -nodes -newkey rsa:2048 -days 3650 \
       -keyout /etc/nginx/certs/oidc-proxy.key \
       -out /etc/nginx/certs/oidc-proxy.crt \
       -subj "/CN=oidc-proxy" \
       -addext "subjectAltName=DNS:oidc-proxy,DNS:backend,DNS:localhost"

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
