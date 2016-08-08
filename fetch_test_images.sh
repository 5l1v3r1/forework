#!/bin/bash

PROJECT="dftt/Test%20Images"
IMAGES='1_%20Extended%20Partition/1-extend-part.zip 11_%20Basic%20Data%20Carving%20%231/11-carve-fat.zip 8_%20JPEG%20Search%20%231/8-jpeg-search.zip'
OUTDIR="./tests/images"

mkdir -p "$OUTDIR"
for image in $IMAGES
do
    wget -c -N -P "$OUTDIR" "https://downloads.sourceforge.net/project/$PROJECT/$image"
done

cd "$OUTDIR"
for file in *.zip
do
    unzip -o $file
done
