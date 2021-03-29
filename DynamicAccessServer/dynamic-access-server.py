from flask import Flask, request, jsonify
import requests
import docker

# Define container name
containerImageName: str = ''

if(containerImageName == ''):
    print('Container not specified')
    exit(1)

# Define our flask app
app = Flask(__name__)

# Make a connection to our docker client
try:
    client = docker.from_env()
    # uncomment following line to clean up stopped containers on restart
    # client.containers.prune() # clean up stopped containers
except:
    print('Docker is likely not running or unreachable')
    exit(1)


# Base64 string that you pasted into the UI
def getBastionZeroSharedSecret() -> str:
    return 'Y29vbGJlYW5z'

# Authentication middleware
@app.before_request
def auth():
    print(request.headers)

    # skip auth header for health check
    if(not request.url.find('/health')):
        sharedSecret = getBastionZeroSharedSecret() # Call out to secret store here
        # Header parsing
        # Authentication: 'Basic <Base64String>'
        receivedSecret = request.headers.get('Authentication').split(' ')[1]
        # Python preforms sequence equals here
        if(receivedSecret is not None and receivedSecret != sharedSecret):
            return jsonify({'ErrorMessage': 'Authentication failed'}), 401 # return unauthorized to BastionZero


@app.route('/start', methods=['POST'])
def start(): 
    """
    Starts docker container and returns container ID

    request:
    {
        activationId: string,
        activationRegion: string,
        activationCode: string,
        orgId: string,
        orgProvider: string
    }

    response:
    {
        containerId: string
    }
    """
    # Parse our activationId, activationRegion and, activationCode
    requestJSON = request.json
    activationId, activationRegion, activationCode, orgId, orgProvider = requestJSON['activationId'], requestJSON['activationRegion'], requestJSON['activationCode'], requestJSON['orgId'], requestJSON['orgProvider']

    # Define our environment variables
    environment = {
        'ACTIVATION_ID': activationId,
        'ACTIVATION_REGION': activationRegion, 
        'ACTIVATION_CODE': activationCode,
        'ORG_ID': orgId,
        'ORG_PROVIDER': orgProvider
    }

    try:
        # Start the docker image
        # The docker requires sudo privileges to install the ssm agent to itself on start up
        # NOTE: please change the container name to whatever you build it as
        resp = client.containers.run(containerImageName, detach=True, environment=environment, privileged=True)
        
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
        container.stop() # Stop the container
        
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
        # The following print is a little spammy
        # print(info)
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