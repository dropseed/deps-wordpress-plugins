FROM python:3.6-alpine

RUN apk --no-cache add git curl

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN pip install requests semantic_version

# add the deps utility to easily create pull requests on different git hosts
ENV DEPS_VERSION=2.4.1
ADD https://github.com/dependencies-io/deps/releases/download/${DEPS_VERSION}/deps_${DEPS_VERSION}_linux_amd64.tar.gz .
RUN mkdir deps && \
    tar -zxvf deps_${DEPS_VERSION}_linux_amd64.tar.gz -C deps && \
    ln -s /usr/src/app/deps/deps /usr/local/bin/deps

RUN git config --global user.email "bot@dependencies.io"
RUN git config --global user.name "Dependencies.io Bot"

ADD src/ /usr/src/app/

WORKDIR /repo

ENTRYPOINT ["python", "/usr/src/app/entrypoint.py"]
