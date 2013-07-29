#!/bin/bash

source aleph.conf

def="\e[0;30m"
red="\e[0;31m"
green="\e[0;32m"
ok="$green[ok]$def"
fail="$red[fail]$def"

usage() {
	echo "$0 {start|stop|status}"
	exit 1
}

update_pid() {
	pid=$(cat "$pid_file" 2>/dev/null)
}

update_pid

l_start() {

	# check for other running instances
	pgrep -f 'bash.*alephd.sh' &> /dev/null

	# check for original aleph instance
	kill -0 $pid 2> /dev/null
	if [ $? -eq 0 ]; then
		echo -e "$fail aleph is already running."
		exit 1
	fi
}

l_stop() {
	if kill -0 $pid 2> /dev/null; then
		if kill -TERM $pid 2> /dev/null; then
			echo -e "$ok aleph stopped"
		else
			echo -e "$fail cannot stop aleph"
		fi
	else
		echo -e "$fail aleph is not running"
	fi
}

l_status() {
	if kill -0 $pid 2>/dev/null; then
		echo -e "$ok aleph is running"
	else
		echo -e "$fail aleph is not running"
	fi
}

case $1 in
	"start")
		l_start
	;;

	"stop")
		l_stop
		exit
	;;

	"status")
		l_status
	exit
	;;

	*)
	usage
	;;
esac

[ -d $base_dir ] || mkdir -p "$base_dir"
[ -d $ftp_incoming_dir ] || mkdir -p "$ftp_incoming_dir"
[ -d $internal_processing_dir ] || mkdir -p "$internal_processing_dir"
[ -d $internal_temporary_dir ] || mkdir -p "$internal_temporary_dir"
[ -d $internal_ready_dir ] || mkdir -p "$internal_ready_dir"
[ -d $internal_store_dir ] || mkdir -p "$internal_store_dir"
[ -d $internal_preparing_dir ] || mkdir -p "$internal_preparing_dir" 

for i in ss grep pescan jshon mail rar unrar zip unzip tar gunzip bunzip2; do
	which "$i" >/dev/null || exit
done

if $external_download; then
	/sbin/ss -an | grep -qF "$external_port" || exit
fi

echo starting daemon...
./alephd.sh &
sleep 1
pgrep -f 'bash.*alephd.sh' > "$pid_file"
sleep 2
update_pid
l_status
