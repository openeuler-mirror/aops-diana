FROM openeuler/openeuler:22.03-lts
WORKDIR /app
COPY *.repo  /app/
RUN dnf install aops-diana -y --setopt=reposdir=/app
ENTRYPOINT ["nohup","aops-diana","&"]