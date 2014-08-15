#!/bin/bash

source aleph.conf

/usr/sbin/adduser --home "$ftp_incoming_dir"/$1 $1 || exit 1
rm -f "$ftp_incoming_dir"/$1/.bash* "$ftp_incoming_dir"/$1/.profile
/usr/sbin/addgroup $1 $aleph_group
ln "$ftp_incoming_dir"/ftp-readme.txt "$ftp_incoming_dir"/$1/readme.txt
mkdir "$ftp_incoming_dir"/$1/incoming
chown root: "$ftp_incoming_dir"/$1
chown -R $1:$aleph_group "$ftp_incoming_dir"/$1/incoming
chmod 0775 "$ftp_incoming_dir"/$1/incoming
chmod 0775 "$ftp_incoming_dir"/$1
