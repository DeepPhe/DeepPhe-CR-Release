# ======Intermediate image======
FROM alpine:3 AS intermediate

# Install git and ssh
RUN apk add --no-cache git openssh

# Add credentials on build
ARG SSH_PRIVATE_KEY

# Set permission on the private key file
# Make sure github.com domain is accepted
# Git clone all required the repos
RUN mkdir ~/.ssh/ && \
    echo "${SSH_PRIVATE_KEY}" > ~/.ssh/id_rsa && \
    cat ~/.ssh/id_rsa && \
    chmod 400 ~/.ssh/id_rsa && \
    touch ~/.ssh/known_hosts && \
    ssh-keyscan github.com >> ~/.ssh/known_hosts && \
    git clone git@github.com:DeepPhe/dphe-onto-db.git && \
    git clone git@github.com:DeepPhe/dphe-neo4j.git && \
    git clone git@github.com:DeepPhe/dphe-core.git && \
    git clone git@github.com:DeepPhe/dphe-stream.git && \
    git clone git@github.com:DeepPhe/dphe-stream-rest.git

# ======Final base image======
FROM redhat/ubi8:8.6

LABEL description="DeepPhe Stream Docker Base Image"

# When trying to run "yum updates" or "yum install" the "system is not registered with an entitlement server" error message is given
# To fix this issue:
RUN echo $'[main]\n\
enabled=0\n\\n\
# When following option is set to 1, then all repositories defined outside redhat.repo will be disabled\n\
# every time subscription-manager plugin is triggered by dnf or yum\n\
disable_system_repos=0\n'\
>> /etc/yum/pluginconf.d/subscription-manager.conf

# Set Maven version to be installed
ARG MAVEN_VERSION=3.8.6

WORKDIR /usr/src/app

# Copy the repos form the intermediate image
COPY --from=intermediate /dphe-onto-db dphe-onto-db
COPY --from=intermediate /dphe-neo4j dphe-neo4j
COPY --from=intermediate /dphe-core dphe-core
COPY --from=intermediate /dphe-stream dphe-stream

# Will do maven build individually for the following projects in separate Dockerfile
COPY --from=intermediate /dphe-stream-rest dphe-stream-rest

# Copy everything else from host to image
COPY . .

# Reduce the number of layers in image by minimizing the number of separate RUN commands
# Update packages
# Install the prerequisites
# Install which (otherwise 'mvn version' prints '/usr/share/maven/bin/mvn: line 93: which: command not found') and Java 8 via yum repository
# Download Maven tar file and install
# Clean all yum cache
# Install gosu for de-elevating root to deepphe user
RUN yum update -y && \
    yum install -y yum-utils && \
    yum install -y which java-1.8.0-openjdk java-1.8.0-openjdk-devel && \
    curl -fsSL https://archive.apache.org/dist/maven/maven-3/$MAVEN_VERSION/binaries/apache-maven-$MAVEN_VERSION-bin.tar.gz | tar xzf - -C /usr/share && \
    mv /usr/share/apache-maven-$MAVEN_VERSION /usr/share/maven && \
    ln -s /usr/share/maven/bin/mvn /usr/bin/mvn && \
    yum clean all && \
    curl -o /usr/local/bin/gosu -SL "https://github.com/tianon/gosu/releases/download/1.14/gosu-amd64" && \
    curl -o /usr/local/bin/gosu.asc -SL "https://github.com/tianon/gosu/releases/download/1.14/gosu-amd64.asc" && \
    rm /usr/local/bin/gosu.asc && \
    chmod +x /usr/local/bin/gosu

# Set environment variables for Java and Maven
ENV JAVA_HOME /usr/lib/jvm/java
ENV M2_HOME /usr/share/maven
ENV maven.home $M2_HOME
ENV M2 $M2_HOME/bin
ENV PATH $M2:$PATH

# Install local dependencies
RUN mvn -f /usr/src/app/dphe-onto-db/pom.xml clean install -DskipTests && \
    mvn -f /usr/src/app/dphe-neo4j/pom.xml clean install -DskipTests && \
    mvn -f /usr/src/app/dphe-core/pom.xml clean install -DskipTests && \
    mvn -f /usr/src/app/dphe-stream/pom.xml clean install -DskipTests
