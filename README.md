# thesis_venue_common
This repository holds data structures, modules and functions which are used by more than one micro-service in the infrastructure for our thesis.
# Testing
You need to set env vars to test redis
```
REDIS_HOST=localhost
REDIS_DB=0
REDIS_DB_FOR_TESTING=1
REDIS_PORT=9999
```
# Tips

## Use this library
To use this library in a project:
* add the following line to a`requirements.txt` file
`git+ssh://git@github.com/jorotenev/thesis_common.git@<TAG|COMMIT|BRANCH FROM THIS REPO>`
* Rebuild the image
* (if using docker-compose) remove containers with the old library,
`docker-compose build`
* i sometimes Invalidate the caches of pycharm and restart it too