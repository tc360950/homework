# homework

## Deploy locally
Run: 
```commandline
make up-rebuild
```

## Development
If you are developing on your local machine, create a virtual environment and install poetry:

```commandline

python3 -m venv venv
source venv/bin/activate
python3 -m pip install poetry==2.1.3
```

Now you can install the backend:
```commandline
cd service && python3 -m poetry install
```


### Test
You can run unit tests with:
```commandline
make test-unit
```