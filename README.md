# dynamic-access-example


## Development Recommendations

For testing out the dynamic-access-server we recommend running the server within a python virtual environment.

### Building the docker image

```bash
docker build -t <your username>/dynamic-access-ssm-container ./SsmDockerContainer/Dockerfile
```

Make sure to identify your docker image's name within the `dynamic-access-server.py` module

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

### Test your sever is running 

```bash
curl -XGET http://127.0.0.1:6001/health -v
```