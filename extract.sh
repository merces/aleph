#!/bin/bash

source aleph.conf

function normalize_f {
	local i
	declare -l ext
	for i in *; do
		ext=${i//*.}
		mv "$i" "${i%.*}.$ext"
	done
}

function unzip_f {
	local i
	for i in $(ls *.zip 2>&-); do
		sha_1=$(sha1sum "$i")
		unzip -oP virus "$i";
		sha_2=$(sha1sum "$i")
		if [ "$sha_1" != "$sha_2" ]; then
			unzip -oP virus "$i"
		fi
	done
}

function unrar_f {
	local i
	for i in $(ls *.rar 2>&-); do
		rar x -o+ "$i"
	done
}

function ungzip_f {
	local i
	for i in $(ls *.gz 2>&-); do
		gunzip "$i"
	done
}

function untargz_f {
	local i
	for i in $(ls *.tgz 2>&-); do
		tar xzf "$i"
	done
}

function untar_f {
	local i
	for i in $(ls *.tar 2>&-); do 
		tar xf "$i"
	done
}

function move_f {
	local i
	local pref=
	for i in $(find . -mindepth 2 -type f); do
		if [ -f $(basename "$i") ]; then
			pref="$pref""_"
			mv "$i" "$pref"$(basename "$i")
		else
			mv "$i" .
		fi
		rmdir * 2> /dev/null
	done
}

cd "$internal_preparing_dir"

echo '[+] uncompressing files...'
for (( i=0; i < $uncompress_depth; i++ )); do
	$normalize_file_extensions && normalize_f &>/dev/null
	unzip_f &>/dev/null
	unrar_f &>/dev/null
	untargz_f &>/dev/null
	ungzip_f &>/dev/null
	untar_f &>/dev/null
	move_f &>/dev/null
	find . -type f -exec chmod -x {} \;
done

cd ..

./analyze.sh
