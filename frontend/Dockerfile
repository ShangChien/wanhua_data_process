FROM node:18-alpine as build-stage

WORKDIR /app
RUN corepack enable
RUN corepack prepare pnpm@9.0.5 --activate

RUN npm config set registry https://registry.npmmirror.com

COPY  package.json pnpm-lock.yaml ./
RUN pnpm install 

COPY . .
# RUN pnpm build-dev
RUN pnpm build-prod

FROM nginx:stable-alpine as production-stage

COPY default.conf /etc/nginx/conf.d/default.conf

COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
RUN apk add bash

CMD ["nginx", "-g", "daemon off;"]