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
saxon="$scriptdir/../runtime/saxon9.jar"

# setup variables from input
infile=$1
filename=$(basename "$1")
filename=${filename%.*}

metadata=$2

OUTFILE="./$(date +'%-m-%-e-%Y')-$filename.xml"

javacmd="java -jar $saxon -o $OUTFILE.tmp ./word/document.xml ./from/docxtotei.xsl"

if [ ! -f $infile ];
then
    echo "ERROR: Unable to locate $infile."
    exit
fi

if [ ! -f $scriptdir/../docx/from/docxtotei.xsl ];
then
    echo "ERROR: Unable to locate $scriptdir/../docx/from/docxtotei.xsl."
    exit
fi

if [$metadata == ""]
then
    echo "WARNING: metadata file wasn't specified. Falling back to $scriptdir/../metadata/metadataSample.xml."
    metadata="$scriptdir/../metadata/metadataSample.xml"
fi

if [ ! -f $metadata ];
then
    echo "ERROR: metadata file does not exist."
    exit
fi

cd $scriptdir/../docx

echo "INFO: Decompressing $infile."
unzip $infile

echo "INFO: Running saxon transform (DOCX->TEI): $javacmd"
$javacmd

mv $OUTFILE.tmp $scriptdir/../nlm/in.file

if [ -d ./word/media ];
then
	echo "INFO: Ripping out media directory"
	cp -r ./word/media $scriptdir/media
fi

rm "[Content_Types].xml"
rm -rf ./word
rm -rf ./_rels
rm -rf ./docProps
rm -rf ./customXml

cd $scriptdir/../nlm

javacmd="java -jar $saxon -o ./out.xml ./in.file ./tei_to_nlm.xsl autoBlockQuote=true"
echo "INFO: Running saxon transform (TEI->NLM): $javacmd"
$javacmd

mv out.xml $scriptdir/out.xml

cd $scriptdir

echo "INFO: merging metadata"

echo "METADATA: $metadata"

javacmd="java -jar $saxon -o $scriptdir/$OUTFILE $scriptdir/out.xml ../metadata/metadata.xsl metadataFile=$metadata"
echo "INFO: Running saxon transform (metadata->NLM): $javacmd"
$javacmd

rm $scriptdir/out.xml


