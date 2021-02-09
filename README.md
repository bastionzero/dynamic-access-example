# dynamic-access-example

## What this is

BASTION ZERO COPY TEXT AND DYNAMIC ACCESS COPY TEXT

## API Specification

### POST Start 

The start endpoint is responsible for spinning up a container with the BastionZero
agent on it and passing in the following environment variables into the container to
be consumed by the [`entrypoint.sh`](SsmDockerContainer/EntryScript/entrypoint.sh).

The `containerId` returned does not have to be the docker's container id, rather it
can be any reference id that will be returned to the provisioning server when 
BastionZero hits the Stop endpoint.

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

The health endpoint acts as a liveliness indicator for BastionZero UI status updates.

```json
// Request 
// Empty query string

// Response
// 200 HTTP OK
{ }
```

## Authentication Specification

BastionZero provides you the option to authenticate the incoming requests with an
[HMAC](https://en.wikipedia.org/wiki/HMAC) based signing algorithm. At a high level
this algorithm canonically orders the critical parts of the http request object and
produces a signatured using a key derived from the metadata of the http request and 
a shared secret that you provide to BastionZero when setting up a new Dynamic Access
Config. The implementation can be found in [`auth.py`](./DynamicAccessServer/auth.py).

```
// actions = start, stop, or health

// constants
KEY_PREFIX = 'BZERO'
SIG_SUFFIX = 'bzero_request'
ALGO_NAME  = 'HMAC-SHA256'

// Returns byte array
sign(key, messageString):
    return HMAC-SHA256(key, GetUtf8Bytes(messageString))

// Returns byte array
generateSigningKey(sharedSecretString, timeStampInSeconds, actionString):
    sharedSecretBytes = GetUtf8Bytes(sharedSecretString)
    prefixBytes = GetUtf8Bytes(KEY_PREFIX)
    prefixedKeyBytes = contact(prefixBytes, sharedSecretBytes)
    // three nested signatures
    derivedSigningKey =  
        sign(
            sign(
                sign(prefixedKeyBytes, timeStampInSeconds),
            actionString),
        SIG_SUFFIX)

    return derivedSigningKey

// Returns a boolean
validateSignature(action, requestObject, sharedSecretString):
    timeStampInSeconds = request.headers['X-Timestamp']
    signatureReceived = request.headers['X-Signature']

    derivedSigningKey = generateSigningKey(sharedSecretString, timeStampInSeconds, action)
    
    // Serialize with no spaces, no indents, and keys in camel case, get bytes
    requestJsonBytes = GetUtf8Bytes(json.serialize(request.json))
    requestBytesHashedHex = SHA256(requestJsonBytes).toHexDigest()

    canonicalOrdering = 
        ALGO_NAME           + '\n' +    // concatenate   
        timeStampInSeconds  + '\n' + 
        action              + '/'  +    // yes a forward slash
        SIG_SUFFIX          + '\n' +
        requestBytesHashedHex // END OF LINE
    
    derivedSignature = sign(derivedSigningKey, canonicalOrdering)
    return signatureReceived == derivedSignature

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