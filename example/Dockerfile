FROM       ubuntu:xenial

RUN apt-get update
RUN apt-get install -y openssh-server python
RUN mkdir /var/run/sshd
RUN mkdir /root/.ssh
RUN chmod 0700 /root/.ssh
COPY .ssh/id_rsa.pub /root/.ssh/authorized_keys
RUN chmod 0600 /root/.ssh/authorized_keys
RUN echo 'root:root' |chpasswd
RUN echo 'PermitRootLogin yes' >>/etc/ssh/sshd_config
RUN sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config
RUN sed -ri 's/^#PubkeyAuthentication/PubkeyAuthentication/g' /etc/ssh/sshd_config
RUN sed -ri 's/^#AuthorizedKeysFile/AuthorizedKeysFile/g' /etc/ssh/sshd_config

EXPOSE 22

CMD    ["/usr/sbin/sshd", "-D"]
