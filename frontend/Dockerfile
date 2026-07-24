# syntax=docker/dockerfile:1

FROM node:22-alpine AS base
WORKDIR /app
COPY package.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm install

# --- dev: servidor Vite com hot-reload ---
FROM base AS dev
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev"]

# --- build: gera os assets estaticos de producao ---
FROM base AS build
COPY . .
RUN npm run build
