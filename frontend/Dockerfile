FROM node:alpine AS build

WORKDIR /home
COPY ./package.json ./yarn.lock ./
RUN yarn install --frozen-lockfile
COPY . ./
RUN yarn build

# Serve with Nginx
FROM nginx:alpine

# Copy your Nginx configuration file
COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=build /home/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]