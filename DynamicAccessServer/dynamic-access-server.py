from flask import Flask, request, jsonify
import requests
import docker
from auth import validateSignature

# Define container name
containerName: str = 'cwc/dynamic-access-ssm-container:latest'

if(containerName == ''):
    print('Container not specified')
    exit(1)

# Define our flask app
app = Flask(__name__)

# Make a connection to our docker client
try:
    client = docker.from_env()
except:
    print('Docker is likely not running or unreachable')
    exit(1)


# Does not have to be a hex string, any utf-8 serialization works
# Whatever you pasted into the UI should be what you return from
# this getter function
def getBastionZeroSharedSecret() -> str:
    return 'deadbeef'

@app.route('/start', methods=['POST'])
def start(): 
    """
    Starts docker container and returns container ID

    request:
    {
        activationId: string,
        activationRegion: string,
        activationCode: string
    }

    response:
    {
        containerId: string
    }
    """
    # for the logger
    print(request.headers)
    
    privateKey = getBastionZeroSharedSecret() # call out to secret store here
    if(not validateSignature('start', request, privateKey)):
        return jsonify({'ErrorMessage': 'Authentication failed'}), 401 # return unauthorized to BastionZero

    # Parse our activationId, activationRegion and, activationCode
    requestJSON = request.json
    activationId, activationRegion, activationCode = requestJSON['activationId'], requestJSON['activationRegion'], requestJSON['activationCode']

    # Define our environment variables
    environment = {
        'ACTIVATION_ID': activationId,
        'ACTIVATION_REGION': activationRegion, 
        'ACTIVATION_CODE': activationCode
    }

    try:
        # Start the docker image
        # The docker requires sudo privileges to install the ssm agent to itself on start up
        # NOTE: please change the container name to whatever you build it as
        resp = client.containers.run(containerName, detach=True, environment=environment, privileged=True)
        
        # Return the containerId
        return jsonify({'containerId': resp.id})
    except docker.errors.APIError as ex:
        print(f'Docker is likely not running, {ex}')
        return jsonify({'ErrorMessage': 'Internal System Error'}), 500 # return 500 to BastionZero


@app.route('/stop', methods=['POST'])
def stop(): 
    """
    Stops docker container and returns 200

    request:
    {
        containerId: string
    }

    response:
    HTTP 200
    { } // empty body
    """

    print(request.headers)

    privateKeyHex = getBastionZeroSharedSecret() # call out to secret store here
    if(not validateSignature('stop', request, privateKeyHex)):
        return jsonify({'ErrorMessage': 'Authentication failed'}), 401 # return unauthorized to BastionZero

    
    # Parse out the containerId
    requestJSON = request.json
    containerId = requestJSON['containerId']

    # Find the container
    try:
        container = client.containers.get(containerId)
    except docker.errors.APIError as ex:
        # This probably means the container does not exist locally
        print(f'Docker could not locate the container, {ex}')
        return jsonify({'ErrorMessage': 'Internal System Error'}), 500 # return 500 to BastionZero


    try:
        # Stop the container
        container.stop()
        
        # Return the containerId
        return jsonify({})
    except docker.errors.APIError as ex:
        print(f'Docker is likely not running, {ex}')
        return jsonify({'ErrorMessage': 'Internal System Error'}), 500 # return 500 to BastionZero


# NOTE: unauthenticated for testing purposes
@app.route('/health', methods=['GET'])
def health():
    """
    response:
    HTTP 200
    { } // empty body
    """
    try:
        info = client.info()
        print(info)
    except docker.errors.APIError as ex:
        print(f'Docker is likely not running, {ex}')
        return jsonify({'ErrorMessage': 'Internal System Error'}), 500 # return 500 to BastionZero


    return jsonify({})


# This is an insecure way to run the server, ideally you set up
# an https server, rather than the http server this will provide
# you. 
# Recomendations on https: https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6001)