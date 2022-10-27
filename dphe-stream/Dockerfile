# Base image
FROM redhat/ubi8:8.6

# Set Maven version to be installed, default to 3.8.6
ARG MAVEN_VERSION=3.8.6

WORKDIR /usr/src/app

# Copy everything else from host to image
COPY . .

# Reduce the number of layers in image by minimizing the number of separate RUN commands
# Update packages
# Install unzip, which, Java 8 via yum repository
# Download Maven tar file and install
# Unzip the DeepPhe dependencies source code
# Clean all yum cache
RUN yum update -y && \
    yum install -y unzip which java-1.8.0-openjdk java-1.8.0-openjdk-devel && \
    curl -fsSL https://archive.apache.org/dist/maven/maven-3/$MAVEN_VERSION/binaries/apache-maven-$MAVEN_VERSION-bin.tar.gz | tar xzf - -C /usr/share && \
    mv /usr/share/apache-maven-$MAVEN_VERSION /usr/share/maven && \
    ln -s /usr/share/maven/bin/mvn /usr/bin/mvn && \
    unzip v0.3.0-cr-release.zip && \
    yum clean all

# Set environment variables for Java and Maven
ENV JAVA_HOME /usr/lib/jvm/java
ENV M2_HOME /usr/share/maven
ENV maven.home $M2_HOME
ENV M2 $M2_HOME/bin
ENV PATH $M2:$PATH

# Install local dependencies
RUN mvn -f /usr/src/app/v0.3.0-cr-release/dphe-onto-db/pom.xml clean install -DskipTests && \
    mvn -f /usr/src/app/v0.3.0-cr-release/dphe-neo4j/pom.xml clean install -DskipTests && \
    mvn -f /usr/src/app/v0.3.0-cr-release/dphe-core/pom.xml clean install -DskipTests && \
    mvn -f /usr/src/app/v0.3.0-cr-release/dphe-stream/pom.xml clean install -DskipTests && \
    mvn -f /usr/src/app/v0.3.0-cr-release/dphe-stream-rest/pom.xml clean install -DskipTests

# Change directory to build the REST API application jar
WORKDIR /usr/src/app/v0.3.0-cr-release/dphe-stream-rest

# Remove the default application.properties 
# Remove the default deepphe.properties
# Replace with new application.properties(use port 8080 instead of 9000)
# Replace with new deepphe.properties(use a different auth token)
# Maven build
# Clear maven cache by deleting the .m2/repository directory
# Copy the entrypoint script and make it executible
# Install gosu for de-elevating root to deepphe user
RUN rm -rf src/main/resources/application.properties && \
    rm -rf src/main/resources/deepphe.properties && \
    mv /usr/src/app/application.properties src/main/resources/application.properties && \
    mv /usr/src/app/deepphe.properties src/main/resources/deepphe.properties && \
    mvn clean package -DskipTests && \
    rm -rf /root/.m2/repository && \
    cp /usr/src/app/entrypoint.sh /usr/local/bin/entrypoint.sh && \
    chmod +x /usr/local/bin/entrypoint.sh && \
    curl -o /usr/local/bin/gosu -SL "https://github.com/tianon/gosu/releases/download/1.14/gosu-amd64" && \
    curl -o /usr/local/bin/gosu.asc -SL "https://github.com/tianon/gosu/releases/download/1.14/gosu-amd64.asc" && \
    rm /usr/local/bin/gosu.asc && \
    chmod +x /usr/local/bin/gosu

# Set an entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# The EXPOSE instruction informs Docker that the container listens on the specified network ports at runtime.
# Here use 8080 because in application.properties we use port 8080
EXPOSE 8080

# Start the rest api server on port 8080 running as non-root
# Note: since the current work dir is /usr/src/app/v0.3.0-cr-release/dphe-stream-rest, the logs will be generated here too
# Thus we use /usr/src/app/v0.3.0-cr-release/dphe-stream-rest/logs for the volume mount in docker-compose.yml
CMD ["java", "-jar","-Xmx6G","/usr/src/app/v0.3.0-cr-release/dphe-stream-rest/target/deepphe-stream-rest-0.5.0.jar"]
