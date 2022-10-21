FROM deepphe/dphe-stream-base:latest

WORKDIR /usr/src/app

# Copy everything else from host to image
COPY . .

# Build the application jar
WORKDIR /usr/src/app/dphe-stream-rest

# Remove the default application.properties 
# Remove the default deepphe.properties
# Replace with new application.properties(use port 8080 instead of 9000)
# Replace with new deepphe.properties(use a different auth token)
# Maven build
# Clear maven cache by deleting the .m2/repository directory
# Copy the entrypoint script and make it executible
RUN rm -rf src/main/resources/application.properties && \
    rm -rf src/main/resources/deepphe.properties && \
    mv /usr/src/app/application.properties src/main/resources/application.properties && \
    mv /usr/src/app/deepphe.properties src/main/resources/deepphe.properties && \
    mvn clean package -DskipTests && \
    rm -rf /root/.m2/repository && \
    cp /usr/src/app/entrypoint.sh /usr/local/bin/entrypoint.sh && \
    chmod +x /usr/local/bin/entrypoint.sh

# Set an entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# The EXPOSE instruction informs Docker that the container listens on the specified network ports at runtime.
# Here use 8080 because in application.properties we use port 8080
EXPOSE 8080

# Start the rest api server on port 8080 running as non-root
# Note: since the current work dir is /usr/src/app/dphe-stream-rest, the logs will be generated here too
# Thus we use /usr/src/app/dphe-stream-rest/logs for the volume mount in docker-compose.yml
CMD ["java", "-jar","-Xmx6G","/usr/src/app/dphe-stream-rest/target/deepphe-stream-rest-0.5.0.jar"]
