#!/usr/bin/env bash

set -euo pipefail

DATA_DIR="${DATA_DIR:-$HOME/cs131_data/pageviews}"

mkdir -p "$DATA_DIR"
cd "$DATA_DIR"

download_day() {
    year="$1"
    month="$2"
    day="$3"

    for hour in $(seq -w 0 23); do
        filename="pageviews-${year}${month}${day}-${hour}0000.gz"
        url="https://dumps.wikimedia.org/other/pageviews/${year}/${year}-${month}/${filename}"

        echo "Downloading: $filename"
        wget -c "$url"
    done
}

# Three days before/including ChatGPT release.
download_day 2022 11 28
download_day 2022 11 29
download_day 2022 11 30

# Two days after ChatGPT release.
download_day 2022 12 01
download_day 2022 12 02

echo
echo "Download complete."
echo "Files downloaded:"
find "$DATA_DIR" -maxdepth 1 -name 'pageviews-*.gz' | wc -l

echo
echo "Compressed dataset size:"
du -ch "$DATA_DIR"/*.gz | tail -n 1
