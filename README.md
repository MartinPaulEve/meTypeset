meTypeset
=========

meTypeset is a tool to covert from Microsoft Word .docx format to NLM/JATS-XML for scholarly/scientific article typesetting.

meTypeset is a fork of the OxGarage stack and uses TEI as an intemediary format to facilitate interchange. Components are licensed under the Mozilla Public Licence version 1.1 and the Creative Commons Attribution-Sharealike 3.0 clauses, according to the various original sources of the fork.

The transforms within this software can be invoked in several different ways:

1. Run through a *nix compatible command line with the tools/gennlm.sh bash script.

2. Called through any renderer capable of parsing XSLT 1.0.

The modfications to the OxGarage stack contained within this project are Copyright Martin Paul Eve 2013 and released under the licenses specified in each respective file.

Running the bash script
=========

First off, ensure you have the correct stack installed for your environment. meTypeset needs a valid Java environment, the command line tool "unzip"  and a shell interpreter (eg Bash). Saxon, which is required, is pre-bundled. It has been shown to work correctly on *Nix derivatives and Mac OS X.

To run the typesetter use:

./tools/gennlm.sh path_to_docx [metadataFile]

Developer information
=========
Most of the heavy lifting for the transforms is done in the files within the docx/from and nlm directories.

The process is as follows:

1. Unzip the docx

2. Transform the docx document.xml to intermediary TEI format

3. Rip out the media directory from the docx (if it exists)

4. Transform the TEI to NLM

5. Merge the contents of the metadataFile into the NLM (see metadata/metadataSample.xml)



