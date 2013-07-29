#!/bin/bash

source aleph.conf

submission_error=false
file=$(ls "$internal_processing_dir/")
size=$(ls -lh "$internal_processing_dir/$file" | cut -d' ' -f5)
url="http://$external_fqdn:$external_port/$file"
body=$(mktemp)

[ -f "$internal_processing_dir/$file" ] || exit

subject='New samples submitted'

if $submit_webservice; then
	response=$(curl -o $body -sw '%{http_code}' --form \
	"$webservice_file_field=@$internal_processing_dir/$file" "$webservice_url")

	sn=$(grep -oE '2[0-9]+' $body)
	rm -f $body
fi

mv "$internal_processing_dir/$file" "$internal_ready_dir/"

msg=" +++ The Lula Project +++

We have received new samples. Here is the list:

$(cat "$temporary_database_file")

Webservice submission response: $response
Submission ID: $sn

Go to http://$external_fqdn:$external_port and provide the sha1 to see the report for a specific file.

Have a nice day!"

if $notify; then
	echo "$msg" | mail -s "$subject" $(echo ${notify_addresses[*]} | tr ' ' ,)
else
	echo "$msg"
fi
