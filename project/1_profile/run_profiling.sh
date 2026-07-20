#!/bin/bash

DATA_DIR=~/cs131_data/pageviews

# Save all output to profiling.txt
exec > profiling.txt 2>&1

echo "===== PHASE 1 PROFILING ====="
echo
date
echo

############################################################
echo "Command:"
echo 'time du -ch "$DATA_DIR"/*.gz | tail -1'
echo
echo "Dataset Size"
time du -ch "$DATA_DIR"/*.gz | tail -1

echo
############################################################
echo "Command:"
echo 'time gzip -cd "$DATA_DIR"/*.gz | wc -l'
echo
echo "Total Rows"
time gzip -cd "$DATA_DIR"/*.gz | wc -l

echo
############################################################
echo "Command:"
echo 'time gzip -cd pageviews-20221128-000000.gz | head'
echo
echo "First 10 Rows"
time gzip -cd "$DATA_DIR"/pageviews-20221128-000000.gz | head

echo
############################################################
echo "Command:"
echo 'time gzip -cd pageviews-20221202-230000.gz | tail'
echo
echo "Last 10 Rows"
time gzip -cd "$DATA_DIR"/pageviews-20221202-230000.gz | tail

echo
############################################################
echo "Command:"
echo 'time gzip -cd "$DATA_DIR"/*.gz | cut -d" " -f1 | sort | uniq -c | sort -nr | head -20'
echo
echo "Top Domain Codes"
time gzip -cd "$DATA_DIR"/*.gz |
cut -d' ' -f1 |
sort |
uniq -c |
sort -nr |
head -20

echo
############################################################
echo "Command:"
echo 'time gzip -cd "$DATA_DIR"/*.gz | grep -Ec "^en(\.m)? "'
echo
echo "English Rows"
time gzip -cd "$DATA_DIR"/*.gz |
grep -Ec '^en(\.m)? '

echo
############################################################
echo "Command:"
echo 'time gzip -cd "$DATA_DIR"/*.gz | awk ...'
echo
echo "Total English Views"
time gzip -cd "$DATA_DIR"/*.gz |
awk '
($1=="en" || $1=="en.m") {
    sum += $3
}
END {
    print sum
}
'

echo
############################################################
echo "Command:"
echo 'time gzip -cd "$DATA_DIR"/*.gz | awk (AI pages)'
echo
echo "===== END PROFILING ====="
