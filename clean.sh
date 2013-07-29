#!/bin/bash

rm -rf "$internal_preparing_dir/*" "$internal_processing_dir/*" "$temporary_database_file"

[ "$1" = "--full" ] && rm -rf "$internal_ready_dir/*" \
"$internal_store_dir/*" "$internal_reports_dir/*"
