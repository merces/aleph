#!/bin/bash

red="\e[0;31m"
gre="\e[0;32m"
yel="\e[0;33m"
ok="$gre[ok]\e[m"
fail="$red[fail]\e[m"
warn="$yel[warning]\e[m"

source aleph.conf 2>&- || { echo -e "$fail configuration file missing"; exit 1; }

usage() {
	echo "$0 {start|restart|stop|status}"
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
			rm -f "$pid_file"
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
		l_start ;;
	"restart")
		l_stop ;;
	"stop")
		l_stop
		exit ;;
	"status")
		l_status
		exit ;;
	*)
		usage ;;
esac

[ -d $base_dir ] || mkdir -p "$base_dir"
[ -d $ftp_incoming_dir ] || mkdir -p "$ftp_incoming_dir"
[ -d $internal_processing_dir ] || mkdir -p "$internal_processing_dir"
[ -d $internal_temporary_dir ] || mkdir -p "$internal_temporary_dir"
[ -d $internal_ready_dir ] || mkdir -p "$internal_ready_dir"
[ -d $internal_store_dir ] || mkdir -p "$internal_store_dir"
[ -d $internal_preparing_dir ] || mkdir -p "$internal_preparing_dir" 
[ -d $internal_reports_dir ] || mkdir -p "$internal_reports_dir" 
[ -d $internal_incoming_dir ] || mkdir -p "$internal_incoming_dir" 
[ -d $internal_unprocessed_dir ] || mkdir -p "$internal_unprocessed_dir" 

for i in grep pescan jshon mail rar unrar zip unzip tar gunzip bunzip2 pgrep; do
	which $i >/dev/null || { echo -e $fail where is $i?; exit 1; }
done

sudo ss &>/dev/null || { echo -e $fail where is ss?; exit 1; }

if $external_download; then
	ss -an | grep -qF "$external_port" || { echo -e $warn webserver is down; }
fi

echo starting daemon...
./alephd.sh &
sleep 1
pgrep -f 'bash.*alephd.sh' > "$pid_file"
sleep 1
update_pid
l_status
