# DeepPhe Stream Multi-Container Stack - release branch

This multi-container docker stack consists of the following 2 containers: 

- 1 : `dphe-stream-nginx` (reverse proxy)
- 2 : `dphe-stream` (document and patient summary REST API)

## Overview of componments and architecture

- When the client makes an API call via HTTP request to the `dphe-stream-nginx` container, the request gets proxied to the upstream container `dphe-stream` which fullfills the actual handling.
- As a requirement, we don not persist information anywhere except temporarily within the jvm. We only use an embedded instance of neo4j for the system to read the ontology.
- The `dphe-stream` container is just a thin wrapper that exposes the REST API endpoints, and it is the backend pipeline that does the heavy lifting of NLP and returns the extracted information. 

## Overview of tools

- [Docker Engine](https://docs.docker.com/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)

Note: Docker Compose requires Docker to be installed and running first.

### Docker post-installation configurations   (optional)

The Docker daemon binds to a Unix socket instead of a TCP port. By default that Unix socket is owned by the user root and other users can only access it using sudo. The Docker daemon always runs as the root user. 

If you're using Linux and you don't want to preface the docker command with sudo, you can add users to the `docker` group:

````
sudo usermod -aG docker $USER
````

Then log out and log back in so that your group membership is re-evaluated. If testing on a virtual machine, it may be necessary to restart the virtual machine for changes to take effect.

Note: the following instructions with docker commands are based on managing Docker as a non-root user.

## Build docker images

### Specify auth token   (optional)

Before building the child images, specify the auth token in `dphe-stream/deepphe.properties`. This auth token will be used later when interacting with the REST API calls via the standard HTTP request `Authorization` header with the Bearer scheme:

````
Authorization: Bearer <token>
````

This auth layer applies to all the REST API requests before they can reach to the actual API endpoints.

A default token is provided in the `dphe-stream/deepphe.propertiers` file. For greater security, it is strongly advised that you change this token to a new value for deployment instance.

### Build `dphe-stream-nginx` and `dphe-stream` images

Next go back to the project root directory where you can find the `docker-compose.yml`:

````
docker-compose build --no-cache
````

### Vulnerability scanning for local images   (optional)

Vulnerability scanning for Docker local images allows us to review the security state of the container images and take actions to fix issues identified during the scan, resulting in more secure deployments. The `scan` command is available by default in Docker version 20.10.x and newer.

```
docker scan --dependency-tree --file ./dphe-stream/Dockerfile dphe-stream:0.2.0-cr
docker scan --dependency-tree --file ./dphe-stream-nginx/Dockerfile dphe-stream-nginx:0.2.0-cr
```

## Start up services

There are two configurable environment variables to keep in mind before starting up the containers:

- `HOST_UID`: the user id on the host machine to be mapped to all the containers. Default to 1000 if not set or null.
- `HOST_GID`: the user's group id on the host machine to be mapped to all the containers. Default to 1000 if not set or null.

We can use the default values if the ouput of the below command is 1000 for both `uid` and `gid` of the current user who's going to spin up the containers.

````
id
````

In security practice, the processes within a running container should not run as root, or assume that they are root. The system user on the host machine should be in the docker group and it should also be the user who builds the images and starts the containers. That's why we wanted to use this user's UID and GID within the containers to avoid security holes and file system permission issues as well.

````
docker-compose up -d
````

This command spins up all the services (in the background as detached mode and leaves them running) defiened in the `docker-compose.yml` and aggregates the output of each container. 

Note: Make sure the port `8080` and `8181` are not already allocated, otherwise the containers would fail to start.

Note: Container initialization takes some time, you can use the following command in another terminal window to monitor the progress:

````
docker-compose logs -f --tail="all" 
````


## Interact with the DeepPhe REST API

You will have the following API base URL for the REST API container:

- `dphe-stream`: `http://localhost:8080/deepphe`

Note: You will need to send over the auth token, specified in `dphe-stream/deepphe.properties`, in the `Authorization` header for each HTTP request:

````
Authorization: Bearer <token>
````

If the auth token is missing from request or an invalid token being used, you'll get the HTTP 401 Unauthorized response.

### Submit a document, do not cache information

Use the following URL pattern to process a document, and submit the document text in the request body. HTTP header `Content-Type: text/plain` is required to make the call. 

````
GET http://localhost:8080/deepphe/summarizeDoc/doc/<docId>
````

Example CURL command:

````
curl -i -X GET http://localhost:8080/deepphe/summarizeDoc/doc/doc1 \
     -H "Content-Type: text/plain" \
     -H "Authorization: Bearer AbCdEf123456" \
     --data-binary "@patientX_doc1_RAD.txt"
````

### Submit a document, cache information for patient summary

Use the following URL pattern to process a document for a given patient, and submit the document text in the PUT body with HTTP header `Content-Type: text/plain`. The patient ID is not used in document processing but is required for future patient summarization.

````
PUT http://localhost:8080/deepphe/summarizePatientDoc/patient/<patientId>/doc/<docId>
````

Example CURL command:

````
curl -i -X PUT http://localhost:8080/deepphe/summarizePatientDoc/patient/patientX/doc/doc1 \
     -H "Content-Type: text/plain" \
     -H "Authorization: Bearer AbCdEf123456" \
     --data-binary "@patientX_doc1_RAD.txt"
````

You can also queue up the process by using the following call with the document text in request body. HTTP header `Content-Type: text/plain` is required to make the call:

````
PUT http://localhost:8080/deepphe/queuePatientDoc/patient/<patientId>/doc/<docId>
````

Example CURL command:

````
curl -i -X PUT http://localhost:8080/deepphe/queuePatientDoc/patient/patientX/doc/doc1 \
     -H "Content-Type: text/plain" \
     -H "Authorization: Bearer AbCdEf123456" \
     --data-binary "@patientX_doc1_RAD.txt"
````

For this call, you won't get back the resulting JSON since the text processing is queued up.

Note: The document information cache is automatically cleaned every 15 minutes, removing any document information that has not been accessed within the last 60 minutes.

### Summarize a patient

A patient summary can only be created using document information that was cached.  This following call doesn't require a request body:

````
GET http://localhost:8080/deepphe/summarizePatient/patient/<patientId>
````

Example CURL command:

````
curl -i -X GET http://localhost:8080/deepphe/summarizePatient/patient/patientX \
     -H "Authorization: Bearer AbCdEf123456"
````

## Manage the contaners

### Shell into the running container   (optional)

Sometimes you may want to shell into a running container to check more details, this can be done by:

````
docker exec -it <container-id> bash
````

### Stop the running services

````
docker-compose stop
````
The above command stops all the running containers of this project without removing them. It preserves containers, volumes, and networks, along with every modification made to them. The stopped containers can be started again with `docker-compose start`. 

Instead of stopping all the containers, you can also stop a particular service:

````
docker-compose stop <service-name>
````

### Reset the status of our project

````
docker-compose down
````

This command stops both containers of this project and removes them as well the `dphe-stream-network`.  All cached document information will be lost.

Note: At this time DeepPhe Stream could be run with a single container.  The multi-container stack exists to facilitate addition future workflows that may require additional containers.   


## Integration tests   (optional)

Once the containers are up running, we can execute some integration tests written in Python to verify the pipeline output by submitting some sample reports to the REST API. The tests will be executed against the `dphe-stream-nginx` container, which proxies the requests to the backend REST API service.

The test cases and configuration are located at `dphe-stream-dock/dphe-stream-nginx/integration-test`. If a different auth token is specified during the image creation phase, that same auth token should be specified int he `test.cfg` as well.

### Run the tests manually within the container

````
docker exec -it dphe-stream-nginx bash
cd integration-test/
python3 test.py
````

### Add more tests and run against the container

We can also add more test cases within the `dphe-stream-nginx/integration-test` directory to improve the coverage and run the tests against the running contianers. To do so, we can create a Python virtual environment and install the dependencies:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Once the test changes are made, we can run it:

```
python3 test.py
```

### Trigger the tests via docker healthcheck

In the `docker-compose.yml` file, uncomment the healthcheck section with configuration changes if you prefer the tests to be triggered automatically against the running container on a periodic basis.

```
# Uncommnet the healthcheck section with desired configuration settings to determine if the state of the container is healthy
# This healthcheck triggers the python tests based on the options: interval, timeout and start_period
# healthcheck:
#   test: ["CMD", "python3", "/usr/src/app/integration-test/test.py"]
#   interval: 5m30s
#   timeout: 30s
#   retries: 3
#   start_period: 30s
```
