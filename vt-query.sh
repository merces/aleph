#!/bin/bash

source aleph.conf

[ $# -eq 1 ] || exit 

sha1="$1"
apikey="$virustotal_apikey"
user="$virustotal_user"
file_retr_url='https://www.virustotal.com/vtapi/v2/file/report'
tmpfile=$(mktemp)

wget -q --post-data="whoami=$user&resource=$sha1&apikey=$apikey" $file_retr_url -O $tmpfile

for i in $(jshon -e scans < $tmpfile | grep '{$' | tr -d ' ":{' | sort); do
	echo -n "$i: "
	r=$(jshon -e scans < $tmpfile | jshon -e "$i" | jshon -e result)
	[ "$r" = 'null' ] && r='-'
	echo "$r" | tr -d \"
done

rm -f "$tmpfile"
