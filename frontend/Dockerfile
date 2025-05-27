FROM node:alpine AS build

WORKDIR /home
COPY ./package.json ./yarn.lock ./
RUN yarn install --frozen-lockfile
COPY . ./
RUN yarn build


FROM nginx:alpine


COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=build /home/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]