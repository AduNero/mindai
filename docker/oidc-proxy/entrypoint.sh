#!/bin/sh
# Publishes the self-signed cert onto the shared oidc_proxy_certs volume so
# the librechat container can point NODE_EXTRA_CA_CERTS at it and trust
# this proxy, then starts nginx normally.
set -eu
cp /etc/nginx/certs/oidc-proxy.crt /shared-certs/oidc-proxy.crt
exec nginx -g "daemon off;"
