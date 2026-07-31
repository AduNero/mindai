# syntax=docker/dockerfile:1
#
# Three targets:
#   development — hot-reloading Vite dev server (used by docker-compose.yml)
#   build       — intermediate stage that produces the static bundle
#   production  — that bundle served by a minimal Nginx (used by docker-compose.prod.yml,
#                 itself fronted by the main reverse-proxy Nginx — see docker/nginx/)

FROM node:20-slim AS base
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .

FROM base AS development
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

FROM base AS build
RUN npm run build

FROM nginx:1.27-alpine AS production
COPY --from=build /app/dist /usr/share/nginx/html
# The static-file-serving nginx.conf is mounted at runtime (see
# docker-compose.prod.yml), not copied here — the build context is
# ./frontend, and that config lives under docker/frontend/, outside it.
EXPOSE 80
