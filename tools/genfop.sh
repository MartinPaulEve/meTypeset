#!/bin/bash

# Copyright (c) 2011 Martin Paul Eve
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
saxon="$scriptdir/saxon9.jar"

# setup variables from input
infile=$1
filename=$(basename "$1")
filename=${filename%.*}

# construct commands
javacmd="java -jar $saxon -o $scriptdir/../transform/debug/new.fo $infile $scriptdir/../transform/jpub/jpub3-APAcit-xslfo.xsl"
fopcmd="fop -c $scriptdir/../transform/fop.xconf $scriptdir/../transform/debug/new.fo ./$(date +'%-m-%-e-%Y')-$filename.pdf"


if [ ! -f $infile ];
then
    echo "ERROR: Input file $1 not found."
    exit
fi

if [ ! -f $saxon ];
then
    echo "ERROR: Unable to locate saxon9.jar. Please ensure that saxon9.jar is inside the meXml/tools directory."
    exit
fi

if [ ! -f $scriptdir/../transform/jpub/jpub3-APAcit-xslfo.xsl ];
then
    echo "ERROR: Unable to locate $scriptdir/../transform/jpub/jpub3-APAcit-xslfo.xsl."
    exit
fi

echo "INFO: Running saxon transform: $javacmd"
$javacmd

echo "INFO: Running FOP transform: $fopcmd"
$fopcmd
