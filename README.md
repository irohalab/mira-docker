A repo for docker compose files use for mira project.

This docker-compose includes all the dependencies except RabbitMQ service, you can setup your own amqp server or use CloudAMQP's service.

To use this in dev, you can select each profile name with `--profile`, you can read the [docker-compose document](https://docs.docker.com/compose/profiles/) for more information

## Prepare docker-compose and config files:
You can use `init.sh` to help you setup the environment and config files as well as update docker-compose.
```bash
$ ./init.sh
```
then you will be asked several questions.

**Note that if you choose generated password for admin account of Albireo, it will be printed in console. that's the
only place you can find the password. so write it down. you will need that to login afterward. 

Or you can also do it yourself manually.

## Build Deneb:
in the mira-docker directory. run the script
```bash
$ ./build.sh
```
Then you will be prompted for several questions. After build complete, built files will be copied to <target folder>/web

Then you should update the site section and domain section of albireo/config.yml file and nginx.conf to use your domain

## update some config manually
To make the site actually work. you need to setup your email server to enable Albireo to send mails to user
go to <target_folder>/albireo/config.yml, find the mail server settings. fill the settings

## Expose nginx port to host
If you want to access your web directly using nginx bundled with docker-compose. you need to expose the nginx port to host
by default, the port is 80, but if your host cannot use 80, you need to update this manually in the docker-compose.yml

## Additional Optional Steps

### Update nginx.conf
If you're using nginx as your only reverse proxy. You may have CORS policy issue in browser. To fix this. Add the following header
in the nginx.conf, inside directive `location ^~ /video/ {}`
```
add_header 'Access-Control-Allow-Origin' '*' always;
add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range' always;
add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range' always;
```

### Add sentry DSN for debug purpose (for developers)
If you want to use sentry for collecting error logs, you should add SENTRY_DSN environment variable for
all mira-download-manager, mira-video-manager services. depends on how many project your created,
you may need to set different SENTRY_DSN for each service.
For albireo related services, you should modify the sentry.yml in albireo configuration folder.

## Run services
In your target folder (default is ~/mira), run the following command
```bash
$ docker-compose --profile prod up -d
```