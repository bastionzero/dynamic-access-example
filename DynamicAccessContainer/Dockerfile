FROM amazonlinux:2

ARG GIT_BRANCH=feat/onelogin-integration
ARG PACKAGE_NAME=bzero

# install system dependencies and bzero agent
RUN yum update -y && \
    yum install -y yum-utils git wget tar && \
    yum-config-manager --add-repo https://download-yum.bastionzero.com/bastionzero.repo && \
    yum update -y && \
    yum install -y $PACKAGE_NAME

# install go
RUN mkdir go-download && cd go-download && \
    wget https://dl.google.com/go/go1.18.8.linux-amd64.tar.gz -q && \
    tar -xvf go1.18.8.linux-amd64.tar.gz && \
    rm -rf /usr/local/go && \
    mv go /usr/local

# build from source
RUN cd && \
    git clone -b $GIT_BRANCH https://github.com/bastionzero/bzero.git /root/bzero && \
    export GOROOT=/usr/local/go && \
    export GOPATH=/root/go && \
    export GOCACHE=/root/.cache/go-build && \
    sh /root/bzero/update-agent-version.sh && \
    cd /root/bzero/bctl/agent && \
    /usr/local/go/bin/go build && \
    echo "Finished building agent" && \
    cp agent /usr/bin/${PACKAGE_NAME}

# Copy over local files
COPY  EntryScript/ /EntryScript/
RUN chmod -R 777 /EntryScript

# Start our entrypoint.sh script
ENTRYPOINT [ "./EntryScript/entrypoint.sh" ]