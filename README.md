meTypeset
=========

A docx/odt to TEI to NLM-XML typesetter.

Running
=========

First off, ensure you have the correct stack installed for your environment. meTypeset needs a valid Java environment, the command line tool "unzip"  and a shell interpreter (eg Bash). It has been shown to work correctly on *Nix derivatives and Mac OS X.

To run the typesetter use:

./tools/gennlm.sh <path_to_docx>

Dev
=========
Most of the heavy lifting for the transforms is done in docx/from, all of which are derived from OxGarage (albeit subject to modification).

The process is as follows (for currently supported docx):

Unzip the docx
Transform the docx document.xml to intermediary TEI format
Rip out the media directory from the docx if it exists
Transform the TEI to NLM



