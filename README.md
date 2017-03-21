# thesis_venue_common
This repository holds data structures, modules and functions which are used by more than one micro-service in our infrastructure.


# Tips
## Use this library
To use this library in a project, add the following line to the `requirements.txt` file.  
`http://python-packaging.readthedocs.io/en/latest/minimal.html
git+ssh://git@github.com/jorotenev/thesis_venue_common.git@<TAG FROM THIS REPO>

Normally this library is already added in the "base docker image". It is required to add ssh keys accessible to `pip`.
Here's a snippet from a Dockerfile, which creates a directory, copies files from the host to it, and updates the containers config. Adjust accordingly for non-docker use. The ssh (`thesis-thesis-user` and `thesis-thesis-user.pub`) files used are avaialbe on trello (search for `thesis-user ssh`. 
```
RUN mkdir /root/.ssh
RUN echo " IdentityFile /root/.ssh/github-thesis-user" >> /etc/ssh/ssh_config
COPY ~/.ssh/thesis-thesis-user /root/.ssh/thesis-thesis-user
COPY ~/.ssh/thesis-thesis-user.pub /root/.ssh/thesis-thesis-user.pub
```