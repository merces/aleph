#!/bin/bash

# Installation in Debian 7 i386 (english)
# - timezone set UTC-3

# passwd aleph
# addgroup aleph sudo

ask() {
	echo
	read -p "$1... Continue [Y/n]? " opt
	[ "$opt" = "n" ] && exit	
} 

echo -e '\naleph installation script\n'
ask 'Set up hardening'
bash firewall.sh
# hardening + ipv6 disabling
cp hardening.conf /etc/sysctl.d
sysctl -p /etc/sysctl.d/hardening.conf


ask 'Install packages using the internet'
# basic packages
apt-get update && apt-get upgrade -y
apt-get install -y vsftpd ssh apache2 libapache2-mod-php5 git file zip unzip rar \
unrar bzip2 gzip curl exim4 ntpdate gcc make rcconf vim libjansson-dev \
libssl-dev libpcre3-dev

ask 'Set timezone and current time'
# setting time
#dpkg-reconfigure tzdata
ntpdate ntp.cais.rnp.br

ask 'Download and build libpe'
wget https://github.com/merces/libpe/archive/master.zip -O libpe.zip
unzip -qo libpe.zip 
cd libpe-master
make
make install
cd ..

ask 'Download and build pev'
wget https://github.com/merces/pev/archive/master.zip -O pev.zip
unzip -qo pev.zip 
cd pev-master
cp ../libpe-master/* lib/libpe/
make && make install
cd ..

ask 'Download and build json'
wget http://kmkeen.com/jshon/jshon.tar.gz
tar xf jshon.tar.gz
cd jshon*
make
gzip -c -9 jshon.1 > jshon.1.gz
install jshon /usr/local/bin/jshon
install jshon.1.gz /usr/share/man/man1/jshon.1.gz
cd ..

ask 'Configure vim'
echo -e "syntax on\nset nu\nset tabstop=3" > /home/aleph/.vimrc
cp /home/aleph/.vimrc /root
chown aleph: /home/aleph/.vimrc

ask 'Configure OpenSSH Server'
addgroup aleph-users
sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
echo -e "\nDenyGroups aleph-users" >> /etc/ssh/sshd_config
service ssh reload

ask 'Configure Apache httpd'
a2dismod autoindex
a2dissite default default-ssl
a2enmod ssl
cp aleph-ssl /etc/apache2/sites-available
a2ensite aleph-ssl
sed -i 's/^NameVirtualHost \*:80/#NameVirtualHost \*:80/' /etc/apache2/ports.conf
sed -i 's/^Listen 80/#Listen 80/' /etc/apache2/ports.conf
service apache2 restart

ask 'Configure vsftpd'
sed -i 's/^anonymous_enable=YES/anonymous_enable=NO/' /etc/vsftpd.conf
sed -i 's/^#local_enable=YES/local_enable=YES/' /etc/vsftpd.conf
sed -i 's/^#write_enable=YES/write_enable=YES/' /etc/vsftpd.conf
service vsftpd restart

ask 'Download and install aleph'
mkdir -p /home/incoming
wget https://github.com/merces/aleph/archive/master.zip -O aleph.zip
unzip -qo aleph.zip
cp -r aleph-master/* /home/aleph/
chown -R aleph: /home/aleph
# ftp readme.txt
cp ftp-readme.txt /home/incoming

cd /home/aleph
./alephctl.sh start
