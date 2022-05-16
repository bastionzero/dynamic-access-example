FROM amazonlinux:2

# install bzero-beta  agent
RUN yum update -y && \
    yum install -y yum-utils && \
    yum-config-manager --add-repo https://download-yum.bastionzero.com/bastionzero-beta.repo \
    yum update -y && \
    yum install -y bzero-beta

# Copy over local files
COPY  EntryScript/ /EntryScript/
RUN chmod -R 777 /EntryScript

# Start our entrypoint.sh script
ENTRYPOINT [ "./EntryScript/entrypoint.sh" ]