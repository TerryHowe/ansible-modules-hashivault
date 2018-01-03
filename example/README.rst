Ansible Modules Hashivault
==========================

Example sandbox for Ansible modules for Hashicorp Vault.  These example
directions assume you have Docker installed.  You need to install the
Ansible module first to use it::

    pip install ansible-modules-hashivault

Optionally Run Vault in Docker
------------------------------

You can use the automated functional test to create a Vault instance running
in Docker.  The `./start.sh` script in the `functional` directory will start
an initialized vault instance. The script will create a `vaultenv.sh` which
contains the environment variables needed to communicate with Vault.::

    cd ../functional
    ./start.sh
    source ./vaultenv.sh

Run a Ansible Ready Container
-----------------------------

Use the `./run.sh` script to build and run a Ansible ready Docker container.
The container will be called `sandbox`.::

    ./run.sh

You can see it running with `docker ps` for example::

    $ docker ps
    CONTAINER ID        IMAGE                     COMMAND                  CREATED             STATUS              PORTS
    3b214f80daf0        sandbox:latest            "/usr/sbin/sshd -D"      6 minutes ago       Up 6 minutes        127.0.0.1:3022->22/tcp


There is a sample playbook here that writes a scret to Vault and writes it to
the sandbox::

    ansible-playbook test_remote_host.yml 

You can ssh into your sandbox and check your secret::

    $ ssh -i .ssh/id_rsa -p 3022 root@127.0.0.1
    Last login: Wed Jan  3 16:55:09 2018 from 172.17.0.1
    root@sandbox:~# cat /giant.txt 
    I smell the blood
    root@sandbox:~# 

If you run the sandbox more than once, you'll need to clear the entry in the
`~/.ssh/known_hosts` file
