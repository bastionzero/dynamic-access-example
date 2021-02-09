# dynamic-access-example

Bastionzero is a simple to use zero trust access SaaS for dynamic cloud environments. Bastionzero is the most secure way to lock down remote access to servers, containers, clusters, and VM’s in any cloud, public or private. For more information go to [Bastionzero](https://bastionzero.com).

## Dynamic Access Target

Bastionzero targets are resources that a user can log into, such as a server, container, or virtual machine.  Dynamic Access Targets are types of targets created as a result of a policy decision, such as a user access request.   When a user exits or logs off the target the Dynamic Access Target is torn down.  All of this is achievable through the use of web hooks.

This code repository provides a reference implementation of the web hook server and API for integrating with Bastionzero Dynamic Access Targets.


## API Specification

### POST Start 

The start endpoint is responsible for spinning up a container with the Bastionzero
agent on it and passing in the following environment variables into the container to
be consumed by the [`entrypoint.sh`](SsmDockerContainer/EntryScript/entrypoint.sh).

The `containerId` returned does not have to be the docker's container id, rather it
can be any reference id that will be returned to the provisioning server when 
Bastionzero hits the Stop endpoint.

```json
// Request
{
    "activationId": "string",
    "activationRegion": "string",
    "activationCode": "string"
}

// Response
{
    "containerId": "string"
}
```

### POST Stop

The stop endpoint is responsible for tearing down the container.

```json
// Request
{
    "containerId": "string"
}

// Response
// 200 HTTP OK
{ }
```


### GET Health

The health endpoint acts as a liveliness indicator for Bastionzero UI status updates.

```json
// Request 
// Empty query string

// Response
// 200 HTTP OK
{ }
```

## Development Recommendations

For testing out the dynamic-access-server we recommend running the server within a python virtual environment.

### Building the docker image

```bash
docker build -t <your username>/dynamic-access-ssm-container ./SsmDockerContainer/
```

Make sure to identify your docker image's name within the [`dynamic-access-server.py`](DynamicAccessServer/dynamic-access-server.py) module

### Create a new python virtual environment

```bash
homebrew install pyenv virtualenv
virtualenv dynamic-access-virtualenv
```

### Activate your virtual environment

```bash
source dynamic-access-virtualenv/bin/activate
```

### Install the python requirements

```bash
pip install -r reqs.txt
```

### To leave the virtual environment 
The following is a special command that the virtualenv will detect and detach itself
from your console.

```bash
deactivate
```

### Run the server
```bash
python3 DynamicAccessServer/dynamic-access-server.py
```

### Test your sever is running 

```bash
curl -XGET http://127.0.0.1:6001/health -v
```
