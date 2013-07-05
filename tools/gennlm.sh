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

cd $scriptdir/../docx

echo "INFO: Decompressing $infile."
unzip $infile

echo "INFO: Running saxon transform (DOCX->TEI): $javacmd"
$javacmd

mv $OUTFILE.tmp $scriptdir/../nlm/in.file

rm "[Content_Types].xml"
rm -rf ./word
rm -rf ./_rels
rm -rf ./docProps
rm -rf ./customXml

cd $scriptdir/../nlm

javacmd="java -jar $saxon -o ./out.xml ./in.file ./tei_to_nlm.xsl autoBlockQuote=true"
echo "INFO: Running saxon transform (TEI->NLM): $javacmd"
$javacmd

mv out.xml $scriptdir/$OUTFILE
cd $scriptdir

