from flask import Flask, request, jsonify
import docker

# Define container name
containerImageName: str = 'bzero/dynamic-access-example'

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
        serviceUrl: string,
        activationToken: string,
        environmentId: string
    }

    response:
    {
        uniqueId: string
        error: bool
        errorReasonString: string
    }
    """
    # Parse the activationToken and environmentId from the request
    requestJSON = request.json
    serviceUrl = requestJSON['serviceUrl']
    activationToken = requestJSON['activationToken']
    environmentId = requestJSON['environmentId']

    # Define our environment variables
    environment = {
        'SERVICE_URL': serviceUrl,
        'ACTIVATION_TOKEN': activationToken,
        'ENVIRONMENT_ID': environmentId
    }

    try:
        # Start the docker image
        # NOTE: please change the container name to whatever you build it as
        resp = client.containers.run(containerImageName, detach=True, environment=environment)
        
        # Return the containerId as the uniqueId
        return jsonify({'uniqueId': resp.id})
    except Exception as ex:
        print(f'Docker is likely not running, {ex}')
        return jsonify({'ErrorMessage': f'Error starting the container: {ex}'}), 500 # return 500 to BastionZero


@app.route('/stop', methods=['POST'])
def stop(): 
    """
    Stops docker container and returns 200

    request:
    {
        uniqueId: string
    }

    response:
    HTTP 200
    { } // empty body
    """
    # Parse out the containerId
    requestJSON = request.json
    uniqueId = requestJSON['uniqueId']

    # Find the container
    try:
        container = client.containers.get(uniqueId)
    except Exception as ex:
        # This probably means the container does not exist locally
        print(f'Docker could not locate the container, {ex}')
        return jsonify({'ErrorMessage': f'Docker could not find the container with id {uniqueId}: {ex}'}), 500 # return 500 to BastionZero


    try:
        container.stop() # Stop the container
        return jsonify({})
    except Exception as ex:
        print(f'Docker is likely not running, {ex}')
        return jsonify({'ErrorMessage': f'Docker failed to start container: {ex}'}), 500 # return 500 to BastionZero


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
        print('Docker is still running...sending healthy response in health check')
    except Exception as ex:
        print(f'Docker is likely not running, {ex}')
        return jsonify({'ErrorMessage': 'Internal System Error'}), 500 # return 500 to BastionZero


    return jsonify({})


# This is an insecure way to run the server, ideally you set up
# an https server, rather than the http server this will provide
# you. 
# Recomendations on https: https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6001)