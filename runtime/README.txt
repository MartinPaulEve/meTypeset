README FOR THE NISO JATS COMMITTEE DRAFT JOURNAL PUBLISHING DTD

(Publishing (Blue) Version DRAFT NISO JATS 1.1d1 November 2013)

                                           November 2013
                                               
======================================================

This README describes:

   1.0 The Four Publishing DTDs
   2.0 Sample files for testing
   3.0 Modules Needed for each DTD
       3.1 Modules Used in Publishing XHTML MathML 2.0 DTD
       3.2 Modules Used in Publishing XHTML MathML 3.0 DTD
       3.3 Modules Used in Publishing XHTML and OASIS CALS
             Tables with MathML 2.0 DTD
       3.4 Modules Used in Publishing XHTML and OASIS CALS
             Tables with MathML 3.0 DTD
       3.5 JATS Base Modules (used by all the Publishing DTDs)
   4.0 Descriptions of the Modules
       4.1  Modules Specific to the Publishing DTDs
       4.2  JATS Base Modules: Base Modules
       4.3  JATS Base Modules: Element Class Modules
       4.4  JATS Base Modules: Notations and Special Characters
       4.5  JATS Base Modules: Math Modules 
       4.6  JATS Base Modules: Table Modules
    5.0 Catalog files


======================================================

1.0 THE FOUR PUBLISHING DTDS

There are four versions of the Publishing DTD:

 - One using XHTML tables with MathML 2.0

 - An identical version using XHTML tables but with MathML 3.0
 
 - A version using both XHTML and OASIS CALS table models
     with MathML 2.0 

 - An identical version using both XHTML and OASIS CALS
     table models but with MathML 3.0 

All 4 files represent different versions of the Main DTD for the 
ANSI/NISO JATS Journal Publishing DTD. This is the DOCTYPE that 
covers a journal article and various other non-article journal 
content such as book and product reviews. These DTDs invoke almost 
all the modules in the JATS Archiving and Interchange DTD Suite. 
An institution should choose a DTD based on table and MathML
requirements. 

======================================================

2.0 SAMPLE FILES FOR TESTING Blue (Publishing)

samplesmall-pub1.xml 
             - Minimal journal article document 
               used to test the Publishing DTD (Blue)
               with XHTML tables and MathML 2.0.

samplesmall-pub1-mathml3.xml
             - Minimal journal article document 
               used to test the Publishing DTD (Blue)
               with XHTML tables and MathML 3.0.
                 Two sample equations are provided,
               one of which is valid in MathML 2.0
               and MathML 3.0, and one of which is
               valid only in MathML 3.0.

samplepub-oasis-and-html1.xml
             - Minimal journal article document 
               used to test the Publishing DTD when
               the OASIS CALS Exchange table model
               and the XHTML model are both used
               with MathML 2.0. 
                  The OASIS table is namespaced with a 
               hard-coded namespace prefix of "oasis".

samplepub-oasis-and-html1-mathml3.xml
             - Minimal journal article document 
               used to test the Publishing DTD when
               the OASIS CALS Exchange table model
               and the XHTML model are both used
               with MathML 3.0.
                  The OASIS table is namespaced with a 
               hard-coded namespace prefix of "oasis".
                 Two sample equations are provided,
               one of which is valid in MathML 2.0
               and MathML 3.0, and one of which is
               valid only in MathML 3.0.

samplepub-oasis-table1.xml
             - Minimal journal article document used 
               to test the Publishing DTD when the
               OASIS CALS Exchange table model is
               used instead of the XHTML model. 
                  The OASIS table is namespaced with a 
               namespace prefix of "oasis". 
                  Uses MathML 2.0, but samples are also 
               valid MathML 3.0 samples.
 
======================================================

3.0 MODULES NEEDED FOR EACH DTD
 
------------------------------------------------------

3.1 Modules Used in the Publishing XHTML MathML 2.0 DTD

 - JATS-journalpublishing1.dtd (XHTML tables with MathML 2.0)
      - The Publishing DTD using the XHTML table model
        with MathML 2.0

 - JATS-journalpubcustom-modules1.ent 
 - JATS-journalpubcustom-classes1.ent
 - JATS-journalpubcustom-mixes1.ent
 - JATS-journalpubcustom-models1.ent
 - JATS-nlmcitation1.ent

 - JATS-XHTMLtablesetup1.ent 
 - xhtml-table-1.mod    - XHTML v1.1 DTD module
 - xhtml-inlstyle-1.mod - XHTML v1.1 style attribute module

 - JATS-mathmlsetup1.ent
 - mathml2.dtd
 - mathml2-qname-1.mod
   And inside the mathml subdirectory:
    - mmlalias.ent
    - mmlextra.ent
    
 - and all of the JATS base modules listed in Section 3.5

 
------------------------------------------------------

3.2  Modules Used in the Publishing XHTML MathML 3.0 DTD

 - JATS-journalpublishing1-mathml3.dtd (XHTML tables with 
      MathML 3.0)
      - The Publishing DTD using the XHTML table model
        with MathML 3.0

 - JATS-journalpubcustom-modules1.ent 
 - JATS-journalpubcustom-classes1.ent
 - JATS-journalpubcustom-mixes1.ent
 - JATS-journalpubcustom-models1.ent
 - JATS-nlmcitation1.ent

 - JATS-XHTMLtablesetup1.ent 
 - xhtml-table-1.mod    - XHTML v1.1 DTD module
 - xhtml-inlstyle-1.mod - XHTML v1.1 style attribute module

 - JATS-mathml3-mathmlsetup1.ent
 - mathml3.dtd
 - mathml3-qname-1.mod
   And inside the mathml subdirectory:
    - mmlalias.ent
    - mmlextra.ent
    
 - and all of the JATS base modules listed in Section 3.5
 
 
------------------------------------------------------

3.3  Modules Used in the Publishing XHTML and OASIS CALS
      Tables with MathML 2.0 DTD

 - JATS-journalpublishing-oasis-article1.dtd
       - An alternative Publishing DTD with one addition: 
         the OASIS table model is defined in addition to 
         the XHTML table model. (Both table models are
         used in this DTD, with the OASIS CALS model given 
         a hard-coded namespace prefix of "oasis".) This
         DTD uses MathML 2.0.

 - JATS-journalpub-oasis-custom-modules1.ent
 - JATS-journalpub-oasis-custom-classes1.ent
 - JATS-journalpubcustom-mixes1.ent
 - JATS-journalpubcustom-models1.ent
 - JATS-nlmcitation1.ent

 - JATS-XHTMLtablesetup1.ent 
 - xhtml-table-1.mod    - XHTML v1.1 DTD module
 - xhtml-inlstyle-1.mod - XHTML v1.1 style attribute module

 - JATS-oasis-tablesetup1.ent 
 - JATS-oasis-namespace1.ent 
 - oasis-exchange.ent   - Basic OASIS CALS table model

 - JATS-mathmlsetup1.ent
 - mathml2.dtd
 - mathml2-qname-1.mod
   And inside the mathml subdirectory:
    - mmlalias.ent
    - mmlextra.ent
    
 - and all of the JATS base modules listed in Section 3.5

 
------------------------------------------------------

3.4  Modules Used in the Publishing XHTML and OASIS CALS
      Tables with MathML 3.0 DTD

 - JATS-journalpublishing-oasis-article1-mathml3.dtd
       - An alternative Publishing DTD with one addition: 
         the OASIS table model is defined in addition to 
         the XHTML table model. (Both table models are
         used in this DTD, with the OASIS CALS model given 
         a hard-coded namespace prefix of "oasis".) This
         DTD uses MathML 3.0.
         
 - JATS-journalpub-oasis-custom-modules1.ent
 - JATS-journalpub-oasis-custom-classes1.ent
 - JATS-journalpubcustom-mixes1.ent
 - JATS-journalpubcustom-models1.ent
 - JATS-nlmcitation1.ent

 - JATS-XHTMLtablesetup1.ent 
 - xhtml-table-1.mod    - XHTML v1.1 DTD module
 - xhtml-inlstyle-1.mod - XHTML v1.1 style attribute module

 - JATS-oasis-tablesetup1.ent 
 - JATS-oasis-namespace1.ent 
 - oasis-exchange.ent   - Basic OASIS CALS table model

 - JATS-mathml3-mathmlsetup1.ent
 - mathml3.dtd
 - mathml3-qname-1.mod
   And inside the mathml subdirectory:
    - mmlalias.ent
    - mmlextra.ent
    
 - and all of the JATS base modules listed in Section 3.5

 
------------------------------------------------------

3.5 JATS Base Modules (used by all the Publishing DTDs)

3.5.1 Base Modules

 - JATS-modules1.ent
 - JATS-common-atts1.ent
 - JATS-default-classes1.ent
 - JATS-default-mixes1.ent
 - JATS-common1.ent

3.5.2 Element Class Modules

 - JATS-articlemeta1.ent
 - JATS-backmatter1.ent 
 - JATS-display1.ent   
 - JATS-format1.ent    
 - JATS-funding1.ent      
 - JATS-journalmeta1.ent 
 - JATS-link1.ent
 - JATS-list1.ent
 - JATS-math1.ent
 - JATS-para1.ent
 - JATS-phrase1.ent
 - JATS-references1.ent
 - JATS-related-object1.ent
 - JATS-section1.ent 

3.5.3 Notations and Special Characters

 - JATS-notat1.ent   
 - JATS-chars1.ent   
 - JATS-xmlspecchars1.ent

 - All the MathML special character entity sets:

     (inside the iso8879 subdirectory)
       isobox.ent
       isocyr1.ent
       isocyr2.ent
       isodia.ent
       isolat1.ent
       isolat2.ent
       isonum.ent
       isopub.ent

     (inside the iso9573-13 subdirectory)
       isoamsa.ent
       isoamsb.ent
       isoamsc.ent
       isoamsn.ent
       isoamso.ent
       isoamsr.ent
       isogrk3.ent
       isomfrk.ent
       isomopf.ent
       isomscr.ent
       isotech.ent

     (inside the xmlchars subdirectory)
       isogrk1.ent
       isogrk2.ent
       isogrk4.ent
 

======================================================

4. DESCRIPTIONS of the MODULES

------------------------------------------------------
4.1 Modules Specific to the Publishing DTDs

JATS-journalpubcustom-modules1.ent 
             - Customization module for the Publishing XHTML 
               DTDs. Names all new modules created specifically
               for the Publishing DTDs (therefore not part of 
               the base JATS DTD Suite).
               
               This module must be called as the first 
               module in the DTD, just before the Suite 
               Module of Modules %modules.ent;, which it
               supplements.

JATS-journalpub-oasis-custom-modules1.ent
             - Alternate customization module for the
               DTDS that include OASIS CALS. Names all new 
               modules created specifically for the Publishing 
               OASIS-included DTDs (therefore not part of 
               the base JATS DTD Suite). This module names
               all the specific modules needed to invoke
               both the Publishing customizations and the
               OASIS CALS table modules.
               
               This module must be called as the first 
               module in the DTD, just before the Suite 
               Module of Modules %modules.ent;, which it
               supplements.

JATS-journalpubcustom-classes1.ent
             - Class customizations for the Publishing XHTML 
               DTDs. Provides the DTD-specific class definitions 
               for the for the Publishing DTDs. Used to over-ride 
               the Suite default classes.
               
               Declared in %journalpubcustom-modules.ent;. 
               It must be invoked before the default classes
               module.

JATS-journalpub-oasis-custom-classes1.ent
             - Class customizations for the Publishing XHTML 
               and OASIS CALS DTDs. This custom classes module
               replaces the regular journal Publishing custom
               classes. This modules adds the parameter entities 
               needed by the OASIS table model to enable OASIS 
               Exchange CALS table processing.
               
               Declared in %journalpub-oasis-custom-modules.ent;. 
               It must be invoked before the default classes
               module.

JATS-journalpubcustom-mixes1.ent
             - The Publishing-DTD-specific mix definitions for  
               these DTDs. Used to over-ride the Suite
               default mixes.
               
               Declared in %journalpubcustom-modules.ent; 
               and %journalpub-oasis-custom-modules.ent; 
               for their respective DTDs.
               Must be invoked before the default mixes
               module.

JATS-journalpubcustom-models1.ent
             - The Publishing-DTD-specific content model 
               definitions for this DTD. Used to over-ride 
               the Suite default models.
               
               Declared in %journalpubcustom-modules.ent; 
               and %journalpub-oasis-custom-modules.ent; 
               for their respective DTDs.
               Must be invoked before all of the DTD Suite
               modules since it is used to over-ride them.
            
               There are two types of such over-rides. Those 
               that replace a complete content model are
               named with a suffix "-model". Those that are 
               OR-groups of elements (intended to be mixed 
               with #PCDATA inside a particular model) are 
               named with an "-elements" suffix.

JATS-nlmcitation1.ent (deprecated)
             - Defines the highly structured NLM citation model,
               which was used (historically) to enforce a 
               slightly loose version of an NLM-structured 
               bibliographic reference. Sequence is enforced 
               and interior punctuation is expected to be 
               generated.
               
               This element is now deprecated and should not be
               used; substitute <element-citation>.


------------------------------------------------------
4.2 JATS Base Modules: Critical Base Modules
    (Used by all of the DTDs)

JATS-modules1.ent
               Names all the modules in the NISO JATS 
               DTD Suite.
                                      
               Must be called as the second module
               by any DTD, after the DTD-specific module
               of modules (if any) and before all other 
               modules.
                 
               NOTE: May name modules (such as the 
               OASIS-Exchange module) that are not called 
               by a particular DTD.

JATS-common-atts1.ent
               Defines attributes intended to be used on 
               ALL elements defined in the NISO JATS, 
               including table elements for both the 
               XHTML-inspired and OASIS-inspired table 
               models, with the exception of <mml:math> 
               and <xi:include> whose namespaces JATS 
               does not control. 
                                       
               Must be called after all module-of-modules 
               modules but before all customization 
               (over-ride) modules.

JATS-default-classes1.ent
               The class definitions that are common to the
               NISO JATS DTD Suite. These may be overridden
               by DTD-specific class declarations.

               Must be invoked before any element-defining
               modules such as common or the element
               modules.

JATS-default-mixes1.ent
               The mix definitions that are common to the
               NISO JATS DTD Suite. These may be overridden
               by DTD-specific mix declarations.

               Must be invoked before any element-defining
               modules such as common or the element
               modules.

JATS-common1.ent 
               Defines all elements, attributes, entities
               used by more than one module.
                   
               Called after all module-of-modules modules
               and all customization (over-ride) modules
               but before all the class modules. 

These modules need to be invoked before all other modules 
in a DTD. Other modules can usually be invoked in any order.
They are listed below alphabetically.


------------------------------------------------------
4.3 JATS Base Modules: Element Class Modules 
    (Define the elements and attributes for one class)
    (Used by all of the DTDs)

JATS-articlemeta1.ent  - Article-level metadata elements 
JATS-backmatter1.ent   - Article-level back matter elements
JATS-display1.ent      - Display elements such as Table, Figure, Graphic
JATS-format1.ent       - Format-related elements such as Bold
JATS-funding1.ent      - Award, sponsor, and other funding-related metadata
JATS-journalmeta1.ent  - Journal-level metadata elements
JATS-link1.ent         - Linking elements such as X(Cross)-Reference
JATS-list1.ent         - List elements
JATS-math1.ent         - JATS-defined math elements such as Display Equation
JATS-para1.ent         - Paragraph-level elements such as Paragraph,
                         Statement, and Block Quote
JATS-phrase1.ent       - Phrase-level content-related elements
JATS-references1.ent   - Bibliographic reference list and the elements
                         that can be used inside a citation
JATS-related-object1.ent
                       - <related-object> is similar to  but broader 
                         than <related-article> for databases, books, 
                         chapter in books, etc.
JATS-section1.ent      - Section-level elements

 
------------------------------------------------------
4.4 JATS Base Modules: Notations and Special Characters
    (Used by all of the DTDs)

JATS-notat1.ent   
             - Names all Notations used

JATS-chars1.ent   
             - Defines JATS-specific and custom special
               characters (as general entities defined
               as hexadecimal or decimal character
               entities [Unicode numbers] or by using
               the <private-char> element).

JATS-xmlspecchars1.ent
             - Names all the standard special character
               entity sets to be used by the DTD. The
               MathML characters sets were used,
               unchanged, in the same directory
               structure used for MathML.

All the MathML special character entity sets:

(inside the iso8879 subdirectory)
  isobox.ent
  isocyr1.ent
  isocyr2.ent
  isodia.ent
  isolat1.ent
  isolat2.ent
  isonum.ent
  isopub.ent

(inside the iso9573-13 subdirectory)
  isoamsa.ent
  isoamsb.ent
  isoamsc.ent
  isoamsn.ent
  isoamso.ent
  isoamsr.ent
  isogrk3.ent
  isomfrk.ent
  isomopf.ent
  isomscr.ent
  isotech.ent

Special character entity sets NOT used in MathML
(included as part of the DTD for backwards compatibility)  

(inside the xmlchars subdirectory)
  isogrk1.ent
  isogrk2.ent
  isogrk4.ent


------------------------------------------------------
4.5 JATS Base Modules: Modules for MathML 2.0 and MathML 3.0 
    (Define MathML tagging, used in %math.ent;)

4.5.1 Modules for MathML 2.0

JATS-mathmlsetup1.ent  - DTD Suite module that sets the parameter
                         entities for the MathML 2.0 modules

The top-level MathML 2.0 modules:
  mathml2.dtd
  mathml2-qname-1.mod

And inside the mathml subdirectory:
  mmlalias.ent
  mmlextra.ent

4.5.2 Modules for MathML 3.0

JATS-mathml3-mathmlsetup1.ent - DTD Suite module that sets 
                                the parameter entities for the 
                                MathML 3.0 modules

The top-level MathML 3.0 modules:
  mathml3.dtd
  mathml3-qname-1.mod

And inside the mathml subdirectory:
  mmlalias.ent
  mmlextra.ent

 
------------------------------------------------------
4.6 JATS Base Modules: Table Modules 

4.6.1  XHTML Table Model (Define XHTML Table Model)

These modules are defined in the Suite and should be invoked
from the DTD if XHTML table tagging is desired. The XHTML
table model is the default table model for the JATS Suite.

  JATS-XHTMLtablesetup1.ent 
                       - JATS module to set up parameter
                         entities and attributes for
                         XHTML table processing

  xhtml-table-1.mod    - XHTML v1.1 DTD module
  xhtml-inlstyle-1.mod - XHTML v1.1 style attribute module

4.6.2  OASIS Exchange CALS Table Model

If an organization wishes to use the OASIS Exchange CALS table 
model instead of OR IN ADDITION TO the XHTML model, the following
modules are included as well as the XHTML ones:

  JATS-oasis-tablesetup1.ent 
                       - JATS module to set up parameter
                         entities and attributes for
                         OASIS Exchange CALS table processing
  JATS-oasis-namespace1.ent 
                       - JATS module that sets up the OASIS 
                         namespace, by default with the namespace 
                         prefix of "oasis".

  oasis-exchange.ent   - Basic OASIS CALS table model


======================================================

5.0 CATALOG FILES

These files are not part of the JATS Base Modules proper, but 
are provided as a convenience to implementors.

catalog-jats-v1-1d1-no-base.xml
               - XML catalog made according to the
                 OASIS DTD Entity Resolution XML Catalog V2.1
"http://www.oasis-open.org/committees/entity/release/1.0/catalog.dtd"
                 with no @xml:base attribute provided
                 on the group level.

catalog-jats-v1-1d1-with-base.xml
               - XML catalog made according to the
                 OASIS DTD Entity Resolution XML Catalog V2.1
"http://www.oasis-open.org/committees/entity/release/1.0/catalog.dtd"
                 with a place-holder @xml:base attribute
                 provided on each group level, for the convenience
                 of implementors, who will change the @xml:base
                 to point to their locations.

=============== document end =========================






















