#!/usr/bin/env python
"""nlmprocessor.py: a tool to run the NLM portions of meTypeset

Usage:
    nlmprocessor.py process <input> [options]

Options:
    -a, --aggression <aggression_level>             Parser aggression level 0-10 [default: 10]
    --chain <xslt>                                  Specify a subsequent XSL transform to pass the NLM to
    -c, --clean                                     Produce final XML, not intermediate markup with additional metadata
    -d, --debug                                     Enable debug output
    -h, --help                                      Show this screen.
    -i, --identifiers                               Generate unique identifiers for all supported NLM elements
    --interactive                                   Enable step-by-step interactive mode
    --nogit                                         Disable git debug filesystem (only of use with --debug)
    -s, --settings <settings_file>                  Settings file
    -v, --version                                   Show version.
"""

from teitonlm import TeiToNlm
from docopt import docopt
from bare_globals import GV
from referencelinker import ReferenceLinker
from captionclassifier import CaptionClassifier
from metadata import Metadata
from bibliographyclassifier import BibliographyClassifier
from bibliographydatabase import BibliographyDatabase
from idgenerator import IdGenerator
from xslchainer import XslChain
from complianceenforcer import ComplianceEnforcer
from nlmmanipulate import NlmManipulate

__author__ = "Martin Paul Eve"
__email__ = "martin@martineve.com"

"""
A class that runs the NLM portions of meTypeset

"""

def main():
    args = docopt(__doc__, version='meTypeset 0.1')
    bare_gv = GV(args)

    if args['--debug']:
        bare_gv.debug.enable_debug(args['--nogit'])

    nlm_instance = TeiToNlm(bare_gv)

    if args['process']:
            # run non-transform portions of teitonlm
            TeiToNlm(bare_gv).run(True, False)
            # run reference linker
            rl = ReferenceLinker(bare_gv)
            rl.run(args['--interactive'])
            rl.cleanup()

            bibliography_classifier = BibliographyClassifier(bare_gv)

            # run table classifier
            cc = CaptionClassifier(bare_gv)
            if int(args['--aggression']) > int(bare_gv.settings.get_setting('tablecaptions',
                                                                            None, domain='aggression')):
                cc.run_tables()

            if int(args['--aggression']) > int(bare_gv.settings.get_setting('graphiccaptions',
                                                                            None, domain='aggression')):
                cc.run_graphics()

            if args['--interactive']:
                bibliography_classifier.run_prompt(True)

            # process any bibliography entries that are possible
            BibliographyDatabase(bare_gv).run()

            # remove stranded titles
            manipulate = NlmManipulate(bare_gv)
            manipulate.final_clean()

            if args['--identifiers']:
                IdGenerator(bare_gv).run()

            if args['--chain']:
                # construct and run an XSLT chainer
                XslChain(bare_gv).run()

            if args['--clean']:
                ComplianceEnforcer(bare_gv).run()

if __name__ == '__main__':
    main()