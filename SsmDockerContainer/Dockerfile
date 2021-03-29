# FROM centos:latest
FROM amazonlinux:2

# install systemd, sudo (needed to create ssm-user) and amazon-ssm-agent
RUN yum update -y && \
    yum install -y systemd sudo procps awscli jq && \
    amazon-linux-extras install docker vim -y && \
    yum install -y https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/2.3.701.0/linux_amd64/amazon-ssm-agent.rpm && \
    yum clean all && \
    rm -rf /var/cache/yum

# Install ssm agent (and needed dependencies)
RUN yum install -y epel-release systemd curl jq
RUN mkdir /tmp/ssm
RUN curl https://download-ssm-agent.bastionzero.com/release/latest/bzero-ssm-agent.rpm -o /tmp/ssm/bzero-ssm-agent.rpm
RUN yum install -y /tmp/ssm/bzero-ssm-agent.rpm

# Copy over local files
COPY  EntryScript/ /EntryScript/
RUN chmod -R 777 /EntryScript 

# the entrypoint script is expecting the following env vars to be set:
# ACTIVATION_ID
# ACTIVATION_CODE
# ACTIVATION_REGION
# ORG_ID
# ORG_PROVIDER

# Docker allows you pass in env vars via the cli with the following syntax
# -e ACTIVATION_REGION='us-east-1' -e ANOTHER_VAR='data'

# Start our entrypoint.sh script
ENTRYPOINT [ "./EntryScript/entrypoint.sh" ]