#!/bin/bash

# Installation in Debian 7 i386 (english)
# - timezone set UTC-3

# passwd aleph
# addgroup aleph sudo

# basic packages
apt-get update && apt-get upgrade -y
apt-get install vsftpd ssh apache2 libapache2-mod-php5 git file zip unzip rar unrar bzip2 gzip curl exim4 ntpdate gcc make rcconf

# setting time
#dpkg-reconfigure tzdata
ntpdate ntp.cais.rnp.br

#pev
wget https://github.com/merces/libpe/archive/master.zip
unzip master.zip
cd libpe-master
make && make install
apt-get install libssl-dev libpcre3-dev
wget https://github.com/merces/pev/archive/master.zip
unzip master.zip
cd pev-master
make && make install

#jshon
apt-get install libjansson-dev
wget http://kmkeen.com/jshon/jshon.tar.gz
tar xf jshon.tar.gz
cd jshon*
make
gzip -c -9 jshon.1 > jshon.1.gz
install jshon /usr/local/bin/jshon
install jshon.1.gz /usr/share/man/man1/jshon.1.gz

# vim
apt-get install vim
echo -e "syntax on\nset nu\nset tabstop=3" > /home/aleph/.vimrc
cp /home/aleph/.vimrc /root
chown aleph: /home/aleph/.vimrc

# ssh
addgroup aleph-users
sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
echo -e "\nDenyGroups aleph-users" >> /etc/ssh/sshd_config
service ssh reload

# hardening + ipv6 disabling
cp hardening.conf /etc/sysctl.d

# apache httpd
a2dismodule autoindex
a2dissite default default-ssl
a2enmod ssl
cp aleph-ssl /etc/apache2/sites-available
a2ensite aleph-ssl
sed -i 's/^NameVirtualHost \*:80/#NameVirtualHost \*:80/' apache2.conf
sed -i 's/^Listen 80/#Listen 80/' /etc/apache2/ports.conf
service apache restart

# vsftp
sed -i 's/^anonymous_enable=YES/anonymous_enable=NO/' /etc/vsftpd.conf
sed -i 's/^#local_enable=YES/local_enable=YES/' /etc/vsftpd.conf
sed -i 's/^#write_enable=YES/write_enable=YES/' /etc/vsftpd.conf
service vsftpd restart


# aleph-master
mkdir /home/incoming
wget https://github.com/merces/aleph/archive/master.zip
unzip master.zip
mv aleph-master/* /home/aleph/
# ftp readme.txt
cp ftp-readme.txt /home/incoming

# cleaning
cd ~
rm -r .bash_history *
