A repo for docker compose files use for mira project.

To use this in dev, you can specifiy each profile name with `--profile`, you can read the [docker-compose document](https://docs.docker.com/compose/profiles/) for more information

run in production:

docker-compose --profile prod up -d

you may also need to prepare your environment variables that can be passed in. read the docker-compose file for more details.