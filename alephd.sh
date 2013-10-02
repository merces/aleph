#!/bin/bash

source aleph.conf

>>"$database_file"

IFS=$'\n'
while :; do

	new_sample=false
	for i in $(find "$ftp_incoming_dir" -type f ! -name "*.txt"); do
		while :; do
			sha1=$(sha1sum "$i")
			sleep 2
			sha2=$(sha1sum "$i")
			tam=$(wc -c "$i" | cut -d' ' -f1)
			[ "$sha1" = "$sha2" ] && break
		done

		if [ $tam -ge $min_package_size -a $tam -le $max_package_size ]; then
			cp -pu "$i" "$internal_store_dir"
			sudo mv "$i" "$internal_incoming_dir"
			new_sample=true
		else
			mv "$i" "$internal_unprocessed_dir"
		fi
	done

	ls $internal_incoming_dir/* &>/dev/null
	if [ $? -eq 0 -o $new_sample = true ]; then
		mv "$internal_incoming_dir"/* "$internal_preparing_dir/" 2>/dev/null
		rm -rf "$internal_temporary_dir/*"
		./extract.sh
	fi

	# one-shot call
	[ "$1" = '-r' ] && break

	sleep $monitor_time

done
