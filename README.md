#meTypeset

meTypeset is a tool to covert from Microsoft Word .docx format to NLM/JATS-XML for scholarly/scientific article typesetting.

meTypeset is a fork of the OxGarage stack and uses TEI as an intemediary format to facilitate interchange. Components are licensed under the Mozilla Public Licence version 1.1 and the Creative Commons Attribution-Sharealike 3.0 clauses, according to the various original sources of the fork.

The transforms within this software can be invoked in several different ways:

1. Run through a *nix compatible command line with the bin/meTypeset.py script.

2. A limited set of the transforms can be called through any renderer capable of parsing XSLT 1.0. This will not include the meTypeset classifier stages.

The modfications to the OxGarage stack contained within this project are Copyright Martin Paul Eve 2014 and released under the licenses specified in each respective file.

##Features

* Automated Microsoft Word (docx) to JATS XML
* Intelligent size processing and section grouping algorithm
* Reference list detection
* Free-text list detection
* Footnote handling
* Full table support
* Metadata handling from platform-generated input
* Built-in bibliographic database

##Running meTypeset

First off, ensure you have the correct stack installed for your environment. meTypeset needs a valid python environment, a valid Java environment, the command line tools "unzip" and "basename" and a shell interpreter (eg Bash). Saxon, which is required, is pre-bundled. It has been shown to work correctly on *Nix derivatives and Mac OS X.

```
meTypeset: text parsing library to convert word documents to the JATS XML format

Usage:
    meTypeset.py docx <input> <output_folder> [options]
    meTypeset.py docxextracted <input> <output_folder> [options]
    meTypeset.py bibscan <input> [options]

Options:
    -a, --aggression <aggression_level>             Parser aggression level 0-10 [default: 10].
    -c, --chain <xslt>                              Specify a subsequent XSL transform to pass the NLM to.
    -d, --debug                                     Enable debug output.
    -h, --help                                      Show this screen.
    -m, --metadata <metadata_file>                  Metadata file.
    -s, --settings <settings_file>                  Settings file.
    -v, --version                                   Show version.
```

When running with the docx command, input should be a Word DOCX file.

When running with the docxextracted command, input should be a folder containing the usually compressed contents of a Word DOCX file (unzip x.docx).

When running with the bibscan command, input should be an NLM XML file, from which bibliographic reference information will be extracted.

##Unparseable Elements

Occasionally, meTypeset will encounter a document with a greater number of idiosyncracies than it can handle. In this event, an error log will be written to "errors.txt" in the path specified by the [mt:error configuration value](bin/settings.xml). This document consists of a list of errors, each line beginning with a \[ERROR_NUMBER\] text (eg \[001\]).

Furthermore, the parser will attempt to append an attribute named "rend" to the tags that it felt most problematic with the error number specified within (eg \<p rend="error-001"\>. This is designed to aid visual tools in analysing the problematic areas.

###List of Error Codes and Tagging Behaviour

* 001 - the number of linebreaks found in the document exceeded 80. The parser will mark up elements containing more than 3 comments with rend="error-001"

#Developer Information

##Main Function and Initialization
meTypeset works on a modular basis. The initial call to [meTypeset](bin/meTypeset.py) creates a new instance of the meTypeset class. This, in turn, initializes the debugger and the global settings variable class. It also parses the command line options using [docopt](http://docopt.org/).

The main module then sequentially calls the submodules and classifiers that handle different processes in the parsing of the document. Whether or not these modules are called is defined by the --aggression switch. Aggression levels correlate to the risk involved in running each of the procedures as some are more statistically likely to fail and also to falsely classify other parts of the document.

##docx and docxextracted Procedure

###Extraction and setup
If the command argument given is docx or docxextracted, the first call is to the [DOCX to TEI parser](bin/docxtotei.py). This module extracts the docx file (if argument was "docx") to a temporary folder, copies across all necessary [transform stylesheets](docx/from), extracts any media files embedded in the word document to the "media" folder and then calls [Saxon](runtime/saxon9.jar) to perform an initial transform to TEI format.

###Size Classifier
If the appropriate aggression level is set, the next step is to proceed to the [Size Classifier](bin/sizeclassifier.py). This module handles classification of sizes and headings within the document. Taking a given minimum size cutoff (16) as a basis, it classifies text above this level as a heading, so long as no more than 40 headings of this size exist in a document. It then proceeds to organize these headings into different nested sub-levels using a [TEI-Manipulator](bin/teimanipulator.py) object to do the heavy lifting. The procedure for all this is as follows:

1. Classify all bold headings as root-level titles
2. Process well-formed Word headings and correlate them to other sizes in the document (i.e. Word's "heading 2" correlates to the second largest size heading specified elsewhere by font size, for example)
3. Organize these headings into sections, including downsizing of heading elements that try to be larger than the root node

###List Classifier
While properly formatted Word lists are handled in the XML transforms, we often encounter documents where the user has employed a variety of homegrown stylings, such as successive paragraphs beginning with (1) etc. [This module](bin/listclassifier.py) has three steps:

1. Classify lists beginning with -
2. Classify lists beginning with (1)
3. Classify reference lists and footnotes parsed as \[1\]

The final step is the most difficult. If we find a list at the end of the document in the \[1\] format that is /not referenced elsewhere/, then we treat it as a bibliography. If, however, we find a list in this format, but then additional mentions of \[1\] and \[2\] earlier in the document, then we assume that this is ad-hoc footnote syntax and convert to that, instead.

###Bibliographic Addins Classifier
The [bibliographic addins classifier](bin/bibliographyaddins.py) processes Zotero and Mendeley references, enclosing them within the format that the [bibliography classifier](bin/bibliographyclassifier.py) can then subsequently handle. It then [optionally](bin/settings.py) drops any other addins that we don't know about to avoid courrupted text and JSON strings in the document.

###Bibliography Classifier
The [bibliography classifier](bin/bibliographyclassifier.py) converts marked-up paragraphs into proper bibliography format ready for post-processing and reference parsing.

###Miscellaneous TEI Transformations
The [TEI Manipulator](bin/teimanipulate.py) then changes WMF files into PNG images for maximum compatibility and removes any empty tags and sections that consist /only/ of title elements.

###NLM Transformation
The [TEI to NLM transform](bin/teitonlm.py) procedure is then called, which as with the DOCX to TEI portion calls Saxon on a stylesheet.

###Metadata Merge
The [metadata merge](bin/metadata.py) merges in a metadata heading with the NLM. Ideally, this is produced by a plugin in your journal/content management system.

###Bibliographic Database
The [bibliographic database](bin/bibliographydatabase.py) inserts fully marked-up JATS element-citation blocks for citations that it has encountered previously. These can be imported by using the "bibscan" command.

###Chain
Finally, an [optional additional XSL](bin/xslchainer.py) file can be specified to be transformed by passing the --chain option.

#Credits

meTypeset is a fork of the [TEI Consortium's OxGarage stylesheets](https://github.com/TEIC/Stylesheets).

The lead developer is Dr. [Martin Paul Eve](https://www.martineve.com).

Additional contributions were made, in alphabetical order) by:

* [Rodrigo DLG](https://github.com/josille) (josille@gmail.com)
* [Alex Garnett](https://github.com/axfelix) (axfelix@gmail.com)
* [Dulip Withnage](https://github.com/withanage) (dulip.withanage@gmail.com)
