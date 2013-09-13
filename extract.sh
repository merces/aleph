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
	for i in *.zip; do
		unzip -oP virus "$i";
	done
}

function unrar_f {
	local i
	for i in *.rar; do
		rar x -o+ "$i"
	done
}

function ungzip_f {
	local i
	for i in *.gz; do
		gunzip "$i"
	done
}

function untargz_f {
	local i
	for i in *.tgz; do
		tar xzf "$i"
	done
}

function untar_f {
	local i
	for i in *.tar; do 
		tar xf "$i"
	done
}

function move_f {
	local i

	for i in $(find . -mindepth 2 -type f); do
		local pref=
		while [ -f "$pref"$(basename "$i") ]; do
			pref="$pref""_"
		done
		mv "$i" "$pref"$(basename "$i")
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
done

cd ..

./analyze.sh
