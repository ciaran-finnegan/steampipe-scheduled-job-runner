FROM debian:buster-slim
LABEL maintainer="Ciaran Finnegan https://github.com/ciaran-finnegan"

ARG TARGETVERSION=v0.15.3
ARG TARGETOS=linux
ARG TARGETARCH=amd64

# add a non-root 'steampipe' user
RUN adduser --system --disabled-login --ingroup 0 --gecos "steampipe user" --shell /bin/false --uid 9193 steampipe

# updates and installs - 'wget' for downloading steampipe, 'less' for paging in 'steampipe query' interactive mode
RUN apt-get update
RUN apt-get install -y wget less git jq curl unzip python3-pip

# download the release as given in TARGETVERSION, TARGETOS and TARGETARCH
RUN echo \
 && cd /tmp \
 && wget -nv https://github.com/turbot/steampipe/releases/download/${TARGETVERSION}/steampipe_${TARGETOS}_${TARGETARCH}.tar.gz \
 && tar xzf steampipe_${TARGETOS}_${TARGETARCH}.tar.gz \
 && mv steampipe /usr/local/bin/ \
 && rm -rf /tmp/steampipe_${TARGETOS}_${TARGETARCH}.tar.gz

# Install the AWS CLI (used to copy steampipe output file to AWS S3)

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install

# Change user to non-root
USER steampipe:0

# Use a constant workspace directory that can be mounted to
WORKDIR /workspace

# disable auto-update
ENV STEAMPIPE_UPDATE_CHECK=false

# disable telemetry
ENV STEAMPIPE_TELEMETRY=none

# Run steampipe service once
RUN steampipe service start --dashboard
# and stop it
RUN steampipe service stop

# remove the generated service .passwd file from this image, so that it gets regenerated in the container
RUN rm -f /home/steampipe/.steampipe/internal/.passwd

# Do not expose postgres service default port
# EXPOSE 9193

# Do no expose dashboard service default port
# EXPOSE 9194

# Install steampipe and other required plugins for Steampipe (as steampipe user).
RUN steampipe plugin install steampipe
RUN steampipe plugin install aws
RUN steampipe plugin install okta
RUN steampipe plugin install crowdstrike
RUN steampipe plugin install salesforce
RUN steampipe plugin install net
RUN steampipe plugin install csv

COPY requirements.txt /workspace/requirements.txt
RUN pip3 install -r requirements.txt

# Copy main.sh and make it executable
COPY main.sh /workspace/main.sh
COPY history_report.py /workspace/history_report.py

CMD ["/workspace/main.sh"]
