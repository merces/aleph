#!/bin/bash

source aleph.conf

empty=false
>"$temporary_database_file"

echo '[+] removing old compressed files...'
cd "$internal_preparing_dir"
rm -f *.zip *.tar *.tgz *.gz *.rar
find . -type d ! -name '.' -exec rm -rf {} +; 2>&-
cd ..

for i in $internal_preparing_dir/*; do
	sha=$(sha1sum "$i" | cut -d' ' -f1)

	if grep -qF "$sha" "$database_file"; then
		rm "$i"
		continue
	fi

	if ! ls $internal_preparing_dir/* > /dev/null; then
		empty=true
		break;
	fi

	report=$internal_reports_dir/$sha.txt
	datetime=$(date)

	echo -e "basic\n---" > "$report"

	(echo -n "$datetime,$sha,$(basename "$i"),"
	wc -c "$i" | cut -d' ' -f1) | tee -a "$database_file" \
	"$temporary_database_file" >/dev/null

	type=$(file -b "$i")
	mime=$(file -bi "$i")

	echo -e "
date: $datetime
filename: $(basename "$i")
sha1: "$sha"
size: $(wc -c "$i" | cut -d' ' -f1)
type: "$type"
mimetype: "$mime"
" >> "$report"

	if (echo "$type" | grep -qE 'PE32|MS\-DOS'); then
		(echo -e "\npepack\n---"
		pepack -d /usr/share/pev/userdb.txt "$i"

		echo -e "\n\npesec\n---"
		pesec "$i"

		echo -e "\n\npescan\n---"
		pescan -v "$i"
		) >> "$report"
	fi

		(echo -e "\n\nfile related strings\n---"
		strings "$i" | grep -Ei '\.[a-z]{3}$' | sort -u

		echo -e "\n\nnetworking related strings\n---"
		strings "$i" | grep -Ei '([0-9]{1,3}\.){3}[0-9]{1,3}|tp://' | sort -u
		) >> "$report"

	if $virustotal_query; then
		echo -e "\n\nvirustotal\n---" >> "$report"
		vt_res=$(./vt-query.sh $sha | column -t)
		([ -n "$vt_res" ] && echo "$vt_res" || echo 'not found') >> "$report"
	fi

done

if ! ls $internal_preparing_dir/* > /dev/null 2>&1; then
	echo all new samples are known files
	exit
fi

echo '[+] creating submission zip package...'
zip -jP virus $internal_processing_dir/samples-$(date "+%Y%m%d-%H%M-$RANDOM").zip $internal_preparing_dir/*
rm -rf $internal_preparing_dir/*

./provide.sh
