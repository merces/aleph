#!/bin/bash

list=$(cut -d, -f3 ../db.csv)

for i in exe cpl dll bat vbs pdf scr sys; do
	echo -ne ".$i\t"
	echo "$list" | grep -i "\.$i$" | wc -l
done | sort -rnk2
