#!/bin/sh

VERSION="1.0.3"

echo "Clean up old files"
rm -rf .out/archive
rm -f .out/*


echo "Create folder structure for ZIP"
mkdir -p .out/archive/plugins
mkdir -p .out/archive/resources

echo "Copy files to destination"
cp *.py .out/archive/plugins
cp *.png .out/archive/plugins
cp pcm/icon.png .out/archive/resources
cp pcm/metadata.template.json .out/archive/metadata.json

echo "Write version info to file"
echo $VERSION > .out/archive/plugins/VERSION

echo "Modify archive metadata.json"
sed -i "s/VERSION_HERE/$VERSION/g" .out/archive/metadata.json
sed -i "s/\"kicad_version_max\": \"9.0\",/\"kicad_version_max\": \"9.0\"/g" .out/archive/metadata.json
sed -i "/SHA256_HERE/d" .out/archive/metadata.json
sed -i "/DOWNLOAD_SIZE_HERE/d" .out/archive/metadata.json
sed -i "/DOWNLOAD_URL_HERE/d" .out/archive/metadata.json
sed -i "/INSTALL_SIZE_HERE/d" .out/archive/metadata.json

echo "Zip PCM archive"
cd .out/archive
zip -r ../jlc-kicad-lib-loader-$VERSION-pcm.zip .
cd ../..

echo "Gather data for repo rebuild"
CI_ENV="${CI_ENV:-.out/env}"

echo VERSION=$VERSION >> $CI_ENV
echo DOWNLOAD_SHA256=$(shasum --algorithm 256 .out/jlc-kicad-lib-loader-$VERSION-pcm.zip | xargs | cut -d' ' -f1) >> $CI_ENV
echo DOWNLOAD_SIZE=$(ls -l .out/jlc-kicad-lib-loader-$VERSION-pcm.zip | xargs | cut -d' ' -f5) >> $CI_ENV
echo DOWNLOAD_URL="https://github.com/dsa-t/jlc-kicad-lib-loader/releases/download/$VERSION/jlc-kicad-lib-loader-$VERSION-pcm.zip" >> $CI_ENV
echo INSTALL_SIZE=$(unzip -l .out/jlc-kicad-lib-loader-$VERSION-pcm.zip | tail -1 | xargs | cut -d' ' -f1) >> $CI_ENV
