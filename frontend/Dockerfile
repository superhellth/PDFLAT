FROM node:19-alpine3.15

WORKDIR /usr/src/app
RUN echo "fs.inotify.max_user_watches=524288" >> /etc/sysctl.conf

COPY ./svelte.config.js ./
COPY ./vite.config.js ./
COPY ./tailwind.config.js ./
COPY ./package*.json ./

RUN npm install -g npm@9.6.5
RUN npm install
RUN npm update

USER root
COPY ./ ./

RUN npm run-script build

EXPOSE 5173


CMD npm run dev