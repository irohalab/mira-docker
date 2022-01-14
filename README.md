A repo for docker compose files use for mira project.

This docker-compose includes all the dependencies except RabbitMQ service, you can setup your own amqp server or use CloudAMQP's service.

To use this in dev, you can specifiy each profile name with `--profile`, you can read the [docker-compose document](https://docs.docker.com/compose/profiles/) for more information

run in production:

docker-compose --profile prod up -d

## Prepare docker-compose and config files:
You can use `init.sh` to help you setup the environment and config files as well as update docker-compose.
```bash
$ ./init.sh
```
then you will be asked several questions.

Or you can also do it yourself manually.

After generate the config and docker-compose. you should also download and buid your Deneb project
from irohalab/Deneb repo. then copy the content of dist folder to your NGINX_DENEB defined location
Then you should update the site section and domain section of albireo/config.yml file and nginx.conf to use your domain