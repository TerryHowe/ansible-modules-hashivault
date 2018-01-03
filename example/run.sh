docker stop sandbox 2>/dev/null
docker rm -f sandbox 2>/dev/null
docker rmi -f sandbox 2>/dev/null
mkdir -p .ssh
chmod 700 .ssh
ssh-keygen -t rsa -f .ssh/id_rsa -N '' -q </dev/null
docker build --tag sandbox .
docker run --name sandbox -h sandbox  -p 127.0.0.1:3022:22 -d sandbox:latest
