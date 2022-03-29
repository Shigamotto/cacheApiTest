FROM python:3.10-alpine

ARG SITES_HOME=/home/projects
ARG PROJECT_NAME=cacheApi
ARG PROJECT_HOME=${SITES_HOME}/${PROJECT_NAME}
ARG PROJECT_ROOT=${PROJECT_HOME}/.www

RUN apk update \
    && apk add make gcc python3-dev musl-dev

COPY back/docker_entrypoint.sh $PROJECT_HOME/
COPY back/init.sh $PROJECT_HOME/
RUN chmod a+x $PROJECT_HOME/docker_entrypoint.sh \
    && chmod a+x $PROJECT_HOME/init.sh

WORKDIR $PROJECT_ROOT

COPY back/requirements.txt $PROJECT_ROOT/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r $PROJECT_ROOT/requirements.txt

ENTRYPOINT ["../docker_entrypoint.sh"]
CMD ["../init.sh"]