#!/bin/bash

# Copyright (c) 2013 Martin Paul Eve
# Distributed under the GNU GPL v2. For full terms see the file docs/COPYING.

# determine the directory of the running script so we can find resources
SOURCE="${BASH_SOURCE[0]}"
DIR="$( dirname "$SOURCE" )"
while [ -h "$SOURCE" ]
do 
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
  DIR="$( cd -P "$( dirname "$SOURCE"  )" && pwd )"
done
scriptdir="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
saxon="$scriptdir/../runtime/saxon9he.jar:$scriptdir/../runtime/xml-resolver-1.1.jar"


usage="Usage: gennlm.sh [source.docx] [output folder] <metadata file.xml>"

# setup variables from input
infile="$1"
filename=$(basename "$1")
filename=${filename%.*}

outputfolder="$2"

metadata="$3"

OUTFILE="$filename.xml"

if [ ! -f "$infile" ];
then
    echo "ERROR: Unable to locate $infile."
    echo "$usage"
    exit
fi

if [ ! -f "$scriptdir/../docx/from/docxtotei.xsl" ];
then
    echo "ERROR: Unable to locate $scriptdir/../docx/from/docxtotei.xsl."
    echo "$usage"
    exit
fi

if [ "$outputfolder" == "" ];
then
    echo "ERROR: No output folder specified."
    echo "$usage"
    exit
fi

if [ -d "$outputfolder" ];
then
    echo "ERROR: Output directory $outputfolder already exists."
    echo "$usage"
    exit
fi

if [ "$metadata" == "" ];
then
    echo "WARNING: metadata file wasn't specified. Falling back to $scriptdir/../metadata/metadataSample.xml."
    metadata="$scriptdir/../metadata/metadataSample.xml"
fi

if [ ! -f "$metadata" ];
then
    echo "ERROR: metadata file does not exist."
    exit
fi

# make the output directory and remap it to an absolute path

mkdir "$outputfolder"
outputfolder=$(readlink -f "$outputfolder")

# OK, this is the grimmest part: XSLT using relative filenames expects the "rels" directory to be found
# relative to itself, not the file to which the transform is being applied, so we have to copy it

cp -r "$scriptdir/../docx" "$outputfolder"
cp -r "$scriptdir/../common2" "$outputfolder"

# copy the files into the docx subfolder for relative paths to work

cp "$infile" "$outputfolder/docx"

# remap the input file
# first to the output folder

infile=$(basename "$infile")
infile="$outputfolder/docx/$infile"

# then to an absolute path
infile=$(readlink -f "$infile")

cd "$outputfolder/docx"

# decompress the docx

echo "INFO: Decompressing $infile."
unzip "$infile"

# transform to TEI

javacmd="java -classpath $saxon net.sf.saxon.Transform -catalog:$scriptdir/../runtime/catalog.xml -o:$OUTFILE.tmp ./word/document.xml ./from/docxtotei.xsl"
echo "INFO: Running saxon transform (DOCX->TEI): $javacmd"
$javacmd
mv "$OUTFILE.tmp" "$outputfolder/in.file"

# if there's any media, move it to the output directory (we're still in ./docx)

if [ -d ./word/media ];
then
	echo "INFO: Ripping out media directory"
	cp -r ./word/media "$outputfolder/media"
fi

# move out of docx folder and cleanup

cd "$outputfolder"
rm -rf "./docx"

# transform to NLM

javacmd="java -classpath $saxon net.sf.saxon.Transform -catalog:$scriptdir/../runtime/catalog.xml -o:./out.xml ./in.file $scriptdir/../nlm/tei_to_nlm.xsl autoBlockQuote=true"
echo "INFO: Running saxon transform (TEI->NLM): $javacmd"
$javacmd

# merge in metadata file

echo "INFO: merging metadata FILE $metadata"
javacmd="java -classpath $saxon net.sf.saxon.Transform -catalog:$scriptdir/../runtime/catalog.xml -o:$outputfolder/$OUTFILE ./out.xml $scriptdir/../metadata/metadata.xsl metadataFile=$metadata"
echo "INFO: Running saxon transform (metadata->NLM): $javacmd"
$javacmd

# cleanup
rm "$outputfolder/out.xml"
rm "$outputfolder/in.file"
rm -rf "$outputfolder/common2"


