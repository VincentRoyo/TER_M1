FROM node:21 AS build

WORKDIR /app

COPY ../React/frontend/package.json ../React/frontend/package-lock.json ./

RUN npm install

COPY ../React/frontend ./

RUN npm run build

# Commande pour laisser le conteneur tourner
#CMD ["tail", "-f", "/dev/null"]

FROM nginx:alpine

COPY ../React/default.conf /etc/nginx/conf.d

COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
