ARG NGINX_IMAGE=harbor-gn2.cicd.s15m.nl/ocw-lsp-pub/nginxinc/nginx-unprivileged:1.21.6-alpine_lsp
FROM ${NGINX_IMAGE}
USER root
RUN apk update
RUN apk upgrade
RUN apk add vim
RUN rm /etc/nginx/conf.d/default.conf
COPY ./dist /app/
COPY ./nginx /etc/nginx
CMD nginx -g "daemon off;"

# Expose ports
EXPOSE 8080:8080