#!/bin/bash

source aleph.conf

submission_error=false
file=$(ls "$internal_processing_dir/")
size=$(ls -lh "$internal_processing_dir/$file" | cut -d' ' -f5)
url="http://$external_fqdn:$external_port/$file"
body=$(mktemp)

[ -f "$internal_processing_dir/$file" ] || exit

[ "$external_port" -eq 443 -o -z "$external_port" ] && external_port= || external_port=":$external_port"

subject='New samples submitted'

if $submit_webservice; then
	response_code=$(curl -o $body -sw '%{http_code}' --form \
	"$webservice_file_field=@$internal_processing_dir/$file" "$webservice_url")

	[ -n "$webservice_response_regex" ] && response=$(grep -oE "$webservice_response_regex" $body)
	rm -f $body
fi

mv "$internal_processing_dir/$file" "$internal_ready_dir/"

msg=" +++ aleph +++

We have received new samples. Here is the list:

$(cat "$temporary_database_file")

$(if $submit_webservice; then echo -e \
"Webservice response code: $response_code\n\
Webservice result: $response"; fi)

Go to https://$external_fqdn$external_port and provide the sha1 to see the report for a specific file.

Have a nice day!"

if $notify; then
	echo "$msg" | mail -s "$notify_mail_subject" $(echo ${notify_mail_addresses[*]} | tr ' ' ,)
else
	echo "$msg"
fi
