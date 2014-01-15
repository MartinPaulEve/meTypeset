meTypeset
=========

meTypeset is a tool to covert from Microsoft Word .docx format to NLM/JATS-XML for scholarly/scientific article typesetting.

meTypeset is a fork of the OxGarage stack and uses TEI as an intemediary format to facilitate interchange. Components are licensed under the Mozilla Public Licence version 1.1 and the Creative Commons Attribution-Sharealike 3.0 clauses, according to the various original sources of the fork.

The transforms within this software can be invoked in several different ways:

1. Run through a *nix compatible command line with the bin/meTypeset.py script.

2. A limited set of the transforms can be called through any renderer capable of parsing XSLT 1.0. This will not include the meTypeset classifier stages.

The modfications to the OxGarage stack contained within this project are Copyright Martin Paul Eve 2014 and released under the licenses specified in each respective file.


Running the python script
=========

First off, ensure you have the correct stack installed for your environment. meTypeset needs a valid python environment, a valid Java environment, the command line tools "unzip" and "basename" and a shell interpreter (eg Bash). Saxon, which is required, is pre-bundled. It has been shown to work correctly on *Nix derivatives and Mac OS X.

```
Usage:
    meTypeset.py docx               <input>     <output_folder> [options]
    meTypeset.py docxextracted      <input>     <output_folder> [options]

Options:
    -d, --debug                     Enable debug output
    -h, --help                      Show this screen.
    -m, --metadata <metadata_file>  Metadata file
    -s, --settings <settings_file>  Settings file
    --version                       Show version.
```

When running with the docx command, input should be a Word DOCX file.

When running with the docxextracted command, input should be a folder containing the usually compressed contents of a Word DOCX file (unzip x.docx).

Developer information
=========
Most of the heavy lifting for the transforms is done in the files within the docx/from and nlm directories.

The process is as follows:

1. Unzip the docx

2. Transform the docx document.xml to intermediary TEI format

3. Rip out the media directory from the docx (if it exists)

4. Transform the TEI to NLM

5. Merge the contents of the metadataFile into the NLM (see metadata/metadataSample.xml)



