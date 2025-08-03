FROM nginx:alpine
COPY . /usr/share/nginx/html/
RUN sed -i 's/listen\(.*\)80;/listen 8181;/g' /etc/nginx/conf.d/default.conf
EXPOSE 8181
CMD ["nginx", "-g", "daemon off;"]
