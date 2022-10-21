#!/bin/bash

# Pass the environment variables specified in docker-compose
HOST_GID=${HOST_GID}
HOST_UID=${HOST_UID}
UPSTREAM_ENDPOINT=${UPSTREAM_ENDPOINT}

# Nginx reverse proxy forwarding requires the upstream service to be running and ready to accept requests
# Otherweise we'll get 502 error
# Using --head will avoid downloading the response content, since we don't need it for this check
# Using --silent will avoid status or errors from being emitted by the check itself
until curl --output /dev/null --silent --head "$UPSTREAM_ENDPOINT"; do
    echo "The upstream 'dphe-stream' service is initializing and not ready yet - sleeping 5 seconds..."
    sleep 5
done
  
echo "The upstream 'dphe-stream' service is ready :-)"

echo "Started dphe-stream-nginx container with the mapped host user UID: $HOST_UID and GID: $HOST_GID"

# Create a new user with the same host UID to run processes on container
# The Filesystem doesn't really care what the user is called,
# it only cares about the UID attached to that user
# Check if user already exists and don't recreate across container restarts
getent passwd $HOST_UID > /dev/null 2&>1
# $? is a special variable that captures the exit status of last task
if [ $? -ne 0 ]; then
    groupadd -r -g $HOST_GID deepphe
    useradd -r -u $HOST_UID -g $HOST_GID -m deepphe
fi

# When running Nginx as a non-root user, we need to create the pid file
# and give read and write access to /var/run/nginx.pid, /var/cache/nginx, and /var/log/nginx
# In individual nginx *.conf, also don't listen on ports 80 or 443 because 
# only root processes can listen to ports below 1024
touch /var/run/nginx.pid
chown -R deepphe:deepphe /var/run/nginx.pid
chown -R deepphe:deepphe /var/cache/nginx
chown -R deepphe:deepphe /var/log/nginx

# Make /usr/src/app accessible 
chown -R deepphe:deepphe /usr/src/app

# Lastly we use gosu to execute our process "$@" as that user
# Remember CMD from a Dockerfile of child image gets passed to the entrypoint.sh as command line arguments
# "$@" is a shell variable that means "all the arguments"
exec /usr/local/bin/gosu deepphe "$@"
