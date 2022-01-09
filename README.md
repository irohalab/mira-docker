A repo for docker compose files use for mira project.

This docker-compose includes all the dependencies except RabbitMQ service

To use this in dev, you can specifiy each profile name with `--profile`, you can read the [docker-compose document](https://docs.docker.com/compose/profiles/) for more information

run in production:

docker-compose --profile prod up -d

## Prepare docker-compose and config files:
You can use init_helper.py to help you setup the environment and config files as well as update docker-compose.

In shell run `python3 -m init_helper.py`, then you will be asked several questions.

Or you can also do it yourself manually.
