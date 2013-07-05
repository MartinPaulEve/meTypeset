<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:xlink="http://www.w3.org/1999/xlink"
                version="1.0">

<!-- ============================================================= -->
<!--  MODULE:    Journal Publishing 3.0 NLM/Pubmed Citation        -->
<!--             Preprocessor                                      -->
<!--  VERSION:   1.0                                               -->
<!--  DATE:      November 2008                                     -->
<!--                                                               -->
<!-- ============================================================= -->

<!-- ============================================================= -->
<!--  SYSTEM:    NCBI Archiving and Interchange Journal Articles   -->
<!--                                                               -->
<!--  PURPOSE:   Punctuate and format unpunctuated citation        -->
<!--             elements according to NLM/Pubmed formatting       -->
<!--             rules.                                            -->
<!--                                                               -->
<!--             Apart from its handling of citations, this is     -->
<!--             an identity transform.                            -->
<!--                                                               -->
<!--  CONTAINS:  Documentation:                                    -->
<!--               D1) Change history                              -->
<!--               D2) Structure of this transform                 -->
<!--               D3) Design of the transform                     -->
<!--               D4) Constraints on the transform                -->
<!--                                                               -->
<!--  PROCESSOR DEPENDENCIES:                                      -->
<!--             None: standard XSLT 1.0                           -->
<!--             Tested using Saxon 6.5.5                          -->
<!--                                                               -->
<!--  COMPONENTS REQUIRED:                                         -->
<!--             1) This stylesheet                                -->
<!--                                                               -->
<!--  INPUT:     An XML document valid to the                      -->
<!--             Journal Publishing 3.0 DTD.                       -->
<!--                                                               -->
<!--  OUTPUT:    The same, except all citations appear as          -->
<!--             punctuated and formatted 'mixed-citation'         -->
<!--             elements                                          -->
<!--                                                               -->
<!--  ORIGINAL CREATION DATE:                                      -->
<!--             November 2008                                     -->
<!--                                                               -->
<!--  CREATED FOR:                                                 -->
<!--             Digital Archive of Journal Articles               -->
<!--             National Center for Biotechnology Information     -->
<!--                (NCBI)                                         -->
<!--             National Library of Medicine (NLM)                -->
<!--                                                               -->
<!--  CREATED BY:                                                  -->
<!--             Mulberry Technologies, Inc.                       -->
<!--             (But the hard parts were all done in NCBI's       -->
<!--              cit-render.xsl, on which this stylesheet is      -->
<!--              based)                                           -->
<!--                                                               -->
<!-- ============================================================= -->

<!-- ============================================================= -->
<!--  D1) STYLESHEET VERSION / CHANGE HISTORY                      -->
<!-- =============================================================

  1.  v. 1.00                                         2008-11-10

      This is the inital preprocessing transform for formatting
      structured citations.

      This code was modified from an earlier NCBI transform,
      cit-render.xsl, which does an analogous job with Journal
      Publishing v2.3 input data. Changes to the basic logic were
      minimized in order to facilitate maintenance and avoid 
      introducing errors.
                                                                   -->
<!-- ============================================================= -->

<!-- ============================================================= -->
<!--  D2) STRUCTURE OF THIS TRANSFORM                              -->
<!-- ============================================================= -->

<!--  Citation elements include 'element-citation', 'nlm-citation',
         'mixed-citation' and its relatives, 'product',
         'related-article' and 'related-object'.
       
      The purpose of this transform is to provide formatting,
      including punctuation, for unpunctuated citations. This
      includes 'element-citation' and 'nlm-citation' elements
      (which are permitted only element content by the DTD) and
      other citation elements when they are unpunctuated in the
      source.
      
      The transform consists of the following parts:
      1) A top-level root template that initiates processing in
         mode="as-is".  Everything outside of citations is
         processed in mode="as-is".

      2) The mode="as-is" template that copies all non-citation
         elements as they appear in the input.

      3) Mode="as-is" templates matching citation elements that
         have no punctuation in the source data (construed as no 
         non-whitespace text outside child elements). They rewrite
         'element-citation' and 'nlm-citation' as 'mixed-citation'
         copy 'mixed-citation' and other citation elements, and
         initiate processing of their contents.

      4) Templates for those "citation" offspring that are the
         subject of general processing: copying "as-is",
         suppressing, and just processing their children.

      5) Templates for those "citation" offspring that have
         case-by-case processing: typically addition of
         punctuation, although in some cases elements are mapped
         into others.
         
      6) A "format" mode whose role is to map elements allowed
         inside all citation elements to formatted equivalents.
         For this stylesheet, these only perform some whitespace
         munging, while in principle, they could be used to
         render elements into italics, etc.

     The following two named templates are defined and used:
  
     pgt-number-agreement
     ends-w-punct
  -->

<!-- The following elements are mapped to something else (or
     suppressed):

     abbrev
     access-date
     annotation
     article-title
     collab
     comment
     conf-date
     conf-loc
     conf-name
     conf-sponsor
     day
     edition
     elocation-id
     etal
     fpage
     gov
     inline-formula
     institution
     isbn
     issn
     issue
     issue-id
     issue-title
     lpage
     milestone-end
     milestone-start
     month
     name
     named-content
     object-id
     page-count
     page-range
     patent
     person-group
     private-char
     pub-id
     publisher-loc
     publisher-name
     role
     season
     series
     source
     std
     supplement
     time-stamp
     trans-source
     trans-title
     volume
     volume-id
     year

     The following elements and content are copied "as-is":

     #PCDATA
     bold
     italic
     monospace
     overline
     sans-serif
     sc
     strike
     underline
     inline-graphic
     label
     email
     ext-link
     uri
     sub
     sup
     roman
     styled-content

  -->

<!-- ============================================================= -->
<!--  D3) DESIGN OF THE TRANSFORM                                  -->
<!-- ============================================================= -->

<!-- Each template in the transform is annotated with its
     "Authority".  This is a record of the source of the logic
     used to map the identified element.  The sources are:

     1) The earlier cit-render.xsl module.

     2) The NLM/NCBI ViewNLM-v2.3.xsl module.

     3) The text of the Portico "Blue" (Journal Article) DTD
        Tag Library.

     The above is the preference order in which they were used.
     Logic was taken from the "Blue" spec only if the element
     was not processed by either cit-render.xsl or
     ViewNLM-v2.3.xsl.

     The two named templates were adapted from those found
     in the cit-render.xsl.
   -->

<!-- ============================================================= -->
<!--  D4) CONSTRAINTS ON THE TRANSFORM                             -->
<!-- ============================================================= -->

<!-- Even when not punctuated, contents of citation elements are
     expected to be in the correct order, appropriate to NLM/PMC
     guidelines.                                                   -->
<!-- The following elements can have @id atttributes in the input
     but there's no straightforward place to put the @id in the
     rewritten (or suppressed) output, and they are so suppressed:

     abbrev
     article-title
     collab
     inline-formula
     institution
     milestone-end
     milestone-start
     named-content
     person-group
     source
     trans-source
     trans-title

     There is a note with each template with an @id limitation.

  -->

  <xsl:output
        method="xml"
        indent="yes"
        doctype-public="-//NLM//DTD Journal Publishing DTD v3.0 20080202//EN"
        doctype-system="journalpublishing3.dtd"
   />

  <xsl:strip-space elements="element-citation nlm-citation"/>


<!-- =============================================================== -->
<!-- THE MAIN TRANSFORM                                              -->
<!-- =============================================================== -->

<!-- =============================================================== -->
<!-- At the top level, processing is initiated into "pass-through"   -->
<!-- mode, which is what we want for everything outside of           -->
<!-- "citation" elements.                                            -->
<!-- =============================================================== -->

  <xsl:template match="/">
    <xsl:apply-templates select="node()" mode="as-is"/>
  </xsl:template>


  <!-- =============================================================== -->
<!-- Content outside of "citation" elements, and therefore just      -->
<!-- copied through, complete with attributes, comments and PIs.     -->
<!-- =============================================================== -->

  <xsl:template match="@*|node()" mode="as-is">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()" mode="as-is"/>
    </xsl:copy>
  </xsl:template>


<!-- =============================================================== -->
<!-- The top nodes to be rewritten: 
       nlm-citation, element-citation, mixed-citation,
       product, related-article, related-object                      -->
<!-- =============================================================== -->

  <!-- When they have non-whitespace content, mixed-citation and 
       family members are taken to be formatted, and processed 
       in 'format' mode, which maps inline markup but does not punctuate. -->
  <xsl:template mode="as-is"
    match="mixed-citation[text()[normalize-space()]] |
           product[text()[normalize-space()]] |
           related-article[text()[normalize-space()]] |
           related-object[text()[normalize-space()]]">
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <!-- The 'format' mode maps elements into formatted equivalents,
           without altering punctuation -->
      <xsl:apply-templates mode="format"/>
    </xsl:copy>
  </xsl:template>


  <!-- If it fails to match the foregoing template, mixed-citation is
       treated like element-citation -->
  <xsl:template mode="as-is"
    match="nlm-citation |
           element-citation |
           mixed-citation">
    <mixed-citation>
      <xsl:apply-templates select="@*" mode="as-is"/>
      <xsl:apply-templates select="*"/>
    </mixed-citation>
  </xsl:template>


  <!-- Similarly, the other citation elements are copied, while their
       children are processed like element-citation -->
  <xsl:template mode="as-is"
    match="product | related-article | related-object">
    <xsl:copy>
      <xsl:apply-templates select="@*" mode="as-is"/>
      <xsl:apply-templates select="*"/>
    </xsl:copy>
  </xsl:template>


<!-- The following templates are all for nodes that are rewritten 
     when they occur as a descendant of a citation element.          -->

<!-- =============================================================== -->
<!-- Elements that are copied through "as-is".                       -->
<!-- =============================================================== -->

<!-- Note that these elements could contain elements that need 
     rewriting.  But that's okay, because the children are processed
     in no-mode, so they will be.                                    -->

  <xsl:template match="bold | italic | monospace | overline |
                       sans-serif | sc | strike | underline |
                       inline-graphic |  label | email | ext-link |
                       uri | sub | sup | roman | styled-content">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>


<!-- =============================================================== -->
<!-- Elements that are suppressed.                                   -->
<!-- =============================================================== -->

  <!-- Authority: These elements have no content to be rendered, and
       would be suppressed by the main Preview transform in any 
       case. -->

  <xsl:template match="milestone-end | milestone-start | object-id"/>
  <!-- Note: (milestone-start|milestone-end)/@id suppressed. -->


<!-- =============================================================== -->
<!-- Elements that map to their content.                             -->
<!-- =============================================================== -->

  <!-- Note: named-content/@id suppressed. -->

  <xsl:template match="named-content">
    <xsl:apply-templates/>
  </xsl:template>


<!-- =============================================================== -->
<!-- Elements that are rewritten.                                    -->
<!-- =============================================================== -->
<!-- Mostly this code follows the logic of cit-render.xsl            -->

  
  <xsl:template match="abbrev">
    <!-- Authority: ViewNLM-v2.3, no mode -->
    <!-- Note: @id suppressed. -->
    <xsl:choose>
      <xsl:when test="@xlink:href">
        <ext-link xlink:href="{@xlink:href}">
          <xsl:apply-templates/>
        </ext-link>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


  <xsl:template match="access-date">
    <!-- Authority: ViewNLM, mode="none"
         Note that this element also occurs in mode="nscitation"
         and mode="book". -->
    <xsl:text> [</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>];</xsl:text>
  </xsl:template>


  <xsl:template match="annotation">
    <!-- Authority: ViewNLM, no mode
         Note that this element also occurs in mode="nscitation"
         and is invoked in mode="citation". -->
    <xsl:text> [</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>]</xsl:text>
  </xsl:template>


  <xsl:template match="article-title">
    <!-- Authority: cit-render, mode="add-punct" -->
    <!-- Note: @id suppressed. -->
    <xsl:apply-templates/>
    <xsl:variable name="lastchar-punct">
      <xsl:call-template name="ends-w-punct">
        <xsl:with-param name="str" select="string(.)"/>
      </xsl:call-template>
    </xsl:variable>
    <xsl:choose>
      <xsl:when test="following-sibling::*[1]/self::article-title">
        <xsl:text> = </xsl:text>
      </xsl:when>
      <xsl:when test="following-sibling::*[1]/self::trans-title">
        <xsl:text> </xsl:text>
      </xsl:when>
      <xsl:when test="$lastchar-punct='yes'">
        <xsl:text> </xsl:text>
        <xsl:if test="parent::node()[@publication-type='confproc']
                   or parent::node()[@publication-type='discussion' and
                                     @publication-format='list']">
          <xsl:text>In: </xsl:text>
        </xsl:if>
      </xsl:when>
      <xsl:when test="parent::node()[@publication-type='confproc']
                   or parent::node()[@publication-type='discussion' and
                                     @publication-format='list']">
        <xsl:text>. In: </xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>. </xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


  <xsl:template match="collab">
    <!-- Authority: cit-render, mode="add-punct" -->
    <!-- Note: @id suppressed. -->
    <xsl:apply-templates select="." mode="back-ref"/>
    <xsl:if test="@collab-type">
      <xsl:text>, </xsl:text>
      <xsl:call-template name="pgt-number-agreement">
        <xsl:with-param name="pgt" select="@collab-type"/>
      </xsl:call-template>
    </xsl:if>
    <xsl:choose>
      <xsl:when test="following-sibling::*[1]/self::name
                   or following-sibling::*[1]/self::string-name
                   or following-sibling::*[1]/self::etal
                   or following-sibling::*[1]/self::collab">
        <xsl:text>; </xsl:text>
      </xsl:when>
      <xsl:when test="parent::person-group"/>
      <xsl:otherwise>
        <xsl:text>. </xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


  <xsl:template match="comment">
    <!-- Authority: cit-render, mode="add-punct" -->
    <xsl:variable name="lastchar-punct">
      <xsl:call-template name="ends-w-punct">
        <xsl:with-param name="str" select="string(.)"/>
      </xsl:call-template>
    </xsl:variable>
    <xsl:apply-templates/>
    <xsl:if test="$lastchar-punct='no'">
      <xsl:choose>
        <xsl:when test="parent::node()[@publication-type='book'] and
                        following-sibling::*[1]/self::fpage">
          <xsl:text>; </xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>. </xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </xsl:template>


  <xsl:template match="conf-date">
    <!-- Authority: cit-render, mode="add-punct" -->
    <xsl:apply-templates/>
    <xsl:text>; </xsl:text>
  </xsl:template>


  <xsl:template match="conf-loc">
    <!-- Authority: cit-render, mode="add-punct" -->
    <xsl:apply-templates/>
    <xsl:if test="following-sibling::*">
      <xsl:text>. </xsl:text>
    </xsl:if>
  </xsl:template>


  <xsl:template match="conf-name">
    <!-- Authority: cit-render, mode="add-punct" -->
    <xsl:if test="parent::node()[@publication-type='paper']">
      <xsl:text>Paper presented at: </xsl:text>
    </xsl:if>
    <xsl:if test="parent::node()[@publication-type='poster-session' ]">
      <xsl:text>Poster session presented at: </xsl:text>
    </xsl:if>
    <xsl:apply-templates/>
    <xsl:text>; </xsl:text>
  </xsl:template>


  <xsl:template match="conf-sponsor">
    <!-- Authority: cit-render, mode="add-punct" -->
    <xsl:apply-templates/>
    <xsl:if test="following-sibling::*">
      <xsl:text>. </xsl:text>
    </xsl:if>
  </xsl:template>


  <xsl:template match="day">
    <!-- Authority: cit-render, mode="add-punct" -->
    <xsl:apply-templates/>
    <xsl:choose>
      <xsl:when
        test="following-sibling::*[1]/self::month or
              following-sibling::*[1]/self::day or
              following-sibling::*[1]/self::year">
        <xsl:text>&#x2013;</xsl:text>
      </xsl:when>
      <xsl:when test="following-sibling::*[1]/self::date-in-citation">
        <xsl:text> </xsl:text>
      </xsl:when>
      <xsl:when test="parent::node()[@publication-type='journal' or
                                     @publication-type='newspaper']">
        <xsl:text>;</xsl:text>
      </xsl:when>
      <xsl:when test="following-sibling::*">
        <xsl:text>. </xsl:text>
      </xsl:when>
    </xsl:choose>
  </xsl:template>


  <xsl:template match="edition">
    <!-- Authority: cit-render, mode="add-punct" -->
    <xsl:choose>
      <xsl:when test="parent::node()[@publication-type='journal' or
                                     @publication-type='newspaper']">
        <xsl:text>(</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>). </xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:variable name="lastchar-punct">
          <xsl:call-template name="ends-w-punct">
            <xsl:with-param name="str" select="string(.)"/>
          </xsl:call-template>
        </xsl:variable>
        <xsl:apply-templates/>
        <xsl:if test="$lastchar-punct!='yes'">
          <xsl:text>.</xsl:text>
        </xsl:if>
        <xsl:text> </xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


  <xsl:template match="elocation-id">
    <!-- Authority: cit-render, mode="add-punct" -->
    <xsl:apply-templates select="." mode="back-ref"/>
    <xsl:if test="following-sibling::*">
      <xsl:choose>
        <xsl:when test="following-sibling::*[1]/self::comment and
                        parent::node()[@publication-type='newspaper']">
          <xsl:text> </xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>. </xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </xsl:template>


  <xsl:template match="etal">
    <!-- Authority: cit-render, mode="add-punct" -->
    <xsl:text>et al.</xsl:text>
    <xsl:if test="following-sibling::*">
      <xsl:text> </xsl:text>
    </xsl:if>
 </xsl:template>


  <xsl:template match="fpage">
    <!-- Authority: cit-render, mode="add-punct" -->
    <xsl:if test="not(following-sibling::page-range)">
      <xsl:if test="not(parent::node()[@publication-type='journal' or
                                       @publication-type='newspaper'])">
        <xsl:text>p. </xsl:text>
      </xsl:if>
      <xsl:apply-templates/>
    </xsl:if>
  </xsl:template>


  <xsl:template match="gov">
    <!-- Authority: ViewNLM, no mode -->
    <xsl:apply-templates/>
    <xsl:if test="not(../trans-title)">
      <xsl:text>. </xsl:text>
    </xsl:if>
  </xsl:template>


  <xsl:template match="inline-formula">
    <!-- Authority: ViewNLM, no mode -->
    <!-- Note: @id suppressed. -->
    <xsl:apply-templates/>
  </xsl:template>


  <xsl:template match="institution">
    <!-- Authority: ViewNLM, mode="front" -->
    <!-- Note: @id suppressed. -->
    <xsl:choose>
      <xsl:when test="@xlink:href">
        <ext-link xlink:href="{@xlink:href}">
          <xsl:apply-templates/>
        </ext-link>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates/>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:if test="following-sibling::*">
      <xsl:text> </xsl:text>
    </xsl:if>
  </xsl:template>

  
  <xsl:template match="isbn">
    <!-- Authority: cit-render, mode="add-punct" -->
    <xsl:text> ISBN: </xsl:text>
    <xsl:apply-templates/>
  </xsl:template>


  <xsl:template match="issn">
    <!-- Authority: cit-render, mode="add-punct" -->
    <xsl:text> ISSN: </xsl:text>
    <xsl:apply-templates/>
  </xsl:template>


  <xsl:template match="issue | issue-id">
    <!-- Authority for "issue": cit-render, mode="add-punct" -->
    <!-- Authority for "issue-id": the "Blue" spec. -->
    <!-- Note: These two elements differ in the following ways:
         1. "issue-id" has an associated "type", specified by
            @pub-id-type.  "issue" has no @pub-id-type.
         2. An "issue" may have an associated following "issue-title".
      -->
    <xsl:choose>
      <xsl:when test="parent::node()[@publication-type='newspaper']">
        <xsl:text>(</xsl:text>
        <xsl:apply-templates select="@pub-id-type"/>
        <xsl:apply-templates/>
        <xsl:text>)</xsl:text>
        <xsl:if test="following-sibling::*">
          <xsl:text>:</xsl:text>
        </xsl:if>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>(</xsl:text>
        <xsl:apply-templates select="@pub-id-type"/>
        <xsl:apply-templates/>
        <xsl:if test="self::issue and following-sibling::issue-title">
          <xsl:text> </xsl:text>
          <xsl:apply-templates select="following-sibling::issue-title/node()"/>
        </xsl:if>
        <xsl:text>)</xsl:text>
        <xsl:variable name="next-sibling" select="following-sibling::*[1]"/>
        <xsl:choose>
          <xsl:when test="$next-sibling/self::elocation-id
                       or $next-sibling/self::fpage
                       or $next-sibling/self::size
                       or $next-sibling/self::supplement">
            <!-- when supplement follows issue, supp value preceded by : -->
            <xsl:text>:</xsl:text>
          </xsl:when>
          <xsl:when test="$next-sibling/self::issue-title/
                          following-sibling::*[1]/self::fpage
                       or $next-sibling/self::issue-title/
                          following-sibling::*[1]/self::supplement
                       or $next-sibling/self::issue-title/
                          following-sibling::*[1]/self::elocation-id">
            <!-- when the matched element is followed directly by issue-title
                 and then directly by fpage, supplement or elocation-id -->
            <xsl:text>:</xsl:text>
          </xsl:when>
          <xsl:when test="starts-with($next-sibling/self::comment,'[')">
            <!-- the next sibling is a comment starting with '[';
                 this is likely an indication of size -->
            <xsl:text>:</xsl:text>
          </xsl:when>
          <xsl:when test="$next-sibling/self::comment
                      and not(parent::node()/@publication-format = 'print')">
            <!-- physical description of publication format -->
            <xsl:text>:</xsl:text>
          </xsl:when>
          <xsl:when test="$next-sibling/self::comment">
            <xsl:text>. </xsl:text>
          </xsl:when>
        </xsl:choose>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


  <xsl:template match="issue-title">
    <!-- Authority: cit-render, mode="add-punct" -->
    <xsl:if test="not(preceding-sibling::issue)">
      <xsl:text>(</xsl:text>
      <xsl:apply-templates/>
      <xsl:text>)</xsl:text>
      <xsl:if test="following-sibling::*[1]/self::fpage">
        <xsl:text>:</xsl:text>
      </xsl:if>
    </xsl:if>
  </xsl:template>


  <xsl:template match="lpage">
    <!-- Authority: cit-render, mode="add-punct" -->
    <xsl:if test="not(following-sibling::page-range)">
      <xsl:if test="string(.) != string(preceding-sibling::fpage[1])">
        <xsl:text>&#x2013;</xsl:text>
        <xsl:apply-templates/>
      </xsl:if>
      <xsl:if test="following-sibling::*">
        <xsl:choose>
          <xsl:when test="following-sibling::*[1]/self::comment">
            <xsl:choose>
              <xsl:when
                test="starts-with(following-sibling::comment[1],'author reply')
                   or starts-with(following-sibling::comment[1],'quiz')
                   or starts-with(following-sibling::comment[1],'discussion')">
                <xsl:text>; </xsl:text>
              </xsl:when>
              <xsl:when test="parent::node()[@publication-type='newspaper']">
                <xsl:text> </xsl:text>
              </xsl:when>
              <xsl:otherwise>
                <xsl:text>. </xsl:text>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:when>
          <xsl:otherwise>
            <xsl:text>. </xsl:text>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:if>
    </xsl:if>
  </xsl:template>


  <xsl:template match="month | season">
    <!-- Authority: cit-render, mode="add-punct" -->
    <xsl:apply-templates/>
    <xsl:choose>
      <xsl:when test="following-sibling::*[1]/self::day
               or following-sibling::*[1]/self::date-in-citation">
        <xsl:text> </xsl:text>
      </xsl:when>
      <xsl:when test="parent::node()[@publication-type='journal' or
                                     @publication-type='newspaper']">
        <xsl:text>;</xsl:text>
      </xsl:when>
      <xsl:when test="following-sibling::*">
        <xsl:text>. </xsl:text>
      </xsl:when>
    </xsl:choose>
  </xsl:template>


  <xsl:template match="name">
    <!-- Authority: cit-render, mode="add-punct" -->
    <xsl:variable name="lastchar-punct">
      <xsl:call-template name="ends-w-punct">
        <xsl:with-param name="str"
                        select="string(node()[position() = last()])"/>
      </xsl:call-template>
    </xsl:variable>
    <xsl:if test="prefix">
      <xsl:apply-templates select="prefix/node()"/>
      <xsl:text> </xsl:text>
    </xsl:if>
    <xsl:apply-templates select="surname/node()"/>
    <xsl:if test="surname/following-sibling::*">
      <xsl:text> </xsl:text>
    </xsl:if>
    <xsl:apply-templates select="given-names/node()"/>
    <xsl:if test="given-names/following-sibling::*">
      <xsl:text> </xsl:text>
    </xsl:if>
    <xsl:apply-templates select="suffix/node()"/>
    <xsl:choose>
      <xsl:when test="following-sibling::*[1]/self::name
                   or following-sibling::*[1]/self::etal">
        <xsl:choose>
          <xsl:when test="$lastchar-punct='yes'">
            <xsl:text>; </xsl:text>
          </xsl:when>
          <xsl:otherwise>
            <xsl:text>, </xsl:text>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:when test="following-sibling::*[1]/self::collab">
        <xsl:text>; </xsl:text>
      </xsl:when>
      <xsl:when test="normalize-space(parent::person-group/@person-group-type)"/>
      <xsl:otherwise>
        <xsl:text>. </xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


  <xsl:template match="page-count">
    <!-- Authority: the "Blue" spec. and analogy with the
           "page-range" element. -->
    <xsl:apply-templates/>
    <xsl:if test="parent::node()[@publication-type='book' or
                                 @publication-type='confproc']">
      <xsl:text> page</xsl:text>
      <xsl:if test=".!='1'">
        <xsl:text>s</xsl:text>
      </xsl:if>
    </xsl:if>
    <xsl:if test="following-sibling::*">
      <xsl:text>. </xsl:text>
    </xsl:if>
  </xsl:template>


  <xsl:template match="page-range">
    <!-- Authority: cit-render, mode="add-punct" -->
    <xsl:if test="parent::node()[@publication-type='book' or
                                 @publication-type='confproc']">
      <xsl:text>p. </xsl:text>
    </xsl:if>
    <xsl:apply-templates/>
    <xsl:if test="following-sibling::*">
      <xsl:text>. </xsl:text>
    </xsl:if>
  </xsl:template>


  <xsl:template match="patent">
    <!-- Authority: cit-render, mode="add-punct" -->
    <xsl:apply-templates/>
    <xsl:if test="following-sibling::*">
      <xsl:text>. </xsl:text>
    </xsl:if>
  </xsl:template>


  <xsl:template match="person-group">
    <!-- Authority: cit-render, mode="add-punct" -->
    <!-- Note: @id suppressed. -->
    <xsl:apply-templates/>
    <xsl:if test="@person-group-type">
      <xsl:text>, </xsl:text>
      <xsl:call-template name="pgt-number-agreement">
        <xsl:with-param name="pgt" select="@person-group-type"/>
        <xsl:with-param name="num">
          <xsl:choose>
            <xsl:when test="etal">
              <xsl:value-of select="2"/>
            </xsl:when>
            <xsl:otherwise>
              <xsl:value-of select="count(name|collab|string-name)"/>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:with-param>
      </xsl:call-template>
      <xsl:choose>
        <xsl:when test="following-sibling::*[1]/self::person-group
                     or following-sibling::*[1]/self::collab">
          <xsl:text>; </xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>. </xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
    </xsl:template>


  <xsl:template match="private-char">
    <!-- Authority: none; content "inline-graphic" is allowed
         within Smoothy format. -->
    <xsl:apply-templates select="inline-graphic"/>
  </xsl:template>


  <xsl:template match="pub-id[@pub-id-type='pmid']">
    <!-- Authority: cit-render, mode="add-punct", plus
           using "ext-link" to create a live link. -->
    <xsl:text>[</xsl:text>
    <ext-link ext-link-type="pmid"
              xlink:href="{concat('http://www.ncbi.nlm.nih.gov/pubmed/',
                                  string(.))}">
      <xsl:apply-templates/>
    </ext-link>
    <xsl:text>]</xsl:text>
  </xsl:template>


  <xsl:template match="pub-id[@pub-id-type!='pmid']">
    <!-- Authority: cit-render, mode="add-punct" -->
    <xsl:if test="@pub-id-type='doi'">
      <xsl:text>DOI: </xsl:text>
    </xsl:if>
    <xsl:apply-templates/>
    <xsl:if test="following-sibling::*">
      <xsl:variable name="lastchar-punct">
        <xsl:call-template name="ends-w-punct">
          <xsl:with-param name="str" select="string(.)"/>
        </xsl:call-template>
      </xsl:variable>
      <xsl:if test="$lastchar-punct='no'">
        <xsl:text>.</xsl:text>
      </xsl:if>
      <xsl:text> </xsl:text>
    </xsl:if>
  </xsl:template>


  <xsl:template match="publisher-loc">
    <!-- Authority: cit-render, mode="add-punct" -->
    <xsl:choose>
      <xsl:when test="parent::*[@publication-type='journal' or
                                @publication-type='newspaper'] and
                     preceding-sibling::article-title">
        <xsl:text>(</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>). </xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates/>
        <xsl:text>: </xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


  <xsl:template match="publisher-name">
    <!-- Authority: cit-render, mode="add-punct" -->
    <xsl:apply-templates/>
    <xsl:choose>
      <xsl:when test="parent::node()[@publication-type='journal' or
                                     @publication-type='newspaper' or
                                     @publication-type='database' or
                                     @publication-type='blog' or
                                     @publication-type='wiki'] or
                     following-sibling::*[1]/self::comment">
        <xsl:variable name="lastchar-punct">
          <xsl:call-template name="ends-w-punct">
            <xsl:with-param name="str" select="string(.)"/>
          </xsl:call-template>
        </xsl:variable>
        <xsl:if test="$lastchar-punct!='yes'">
          <xsl:text>.</xsl:text>
        </xsl:if>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>;</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:text> </xsl:text>
  </xsl:template>


  <xsl:template match="role">
    <!-- Authority: ViewNLM, mode="front" -->
    <xsl:text>Role: </xsl:text>
    <xsl:apply-templates/>
  </xsl:template>


  <!-- For "season", see "month". -->


  <xsl:template match="series">
    <!-- Authority: cit-render, mode="add-punct" -->
    <xsl:text>(</xsl:text>
    <xsl:apply-templates select="." mode="back-ref"/>
    <xsl:text>)</xsl:text>
    <xsl:if test="following-sibling::*">
      <xsl:text>. </xsl:text>
    </xsl:if>
  </xsl:template>


  <xsl:template match="source">
    <!-- Authority: cit-render, mode="add-punct" -->
    <!-- Note: @id suppressed. -->
    <xsl:if test="parent::node()[@publication-type='database'] and
                  preceding-sibling::article-title
               or parent::node()[@publication-type='wiki'] and
                  preceding-sibling::article-title">
      <xsl:text>In: </xsl:text>
    </xsl:if>
    <xsl:apply-templates/>
      <xsl:choose>
        <xsl:when test="following-sibling::*[1]/self::source">
          <xsl:text> = </xsl:text>
        </xsl:when>
        <xsl:when test="following-sibling::*[1]/self::trans-source">
          <xsl:text> </xsl:text>
        </xsl:when>
        <xsl:when test="parent::node()[@publication-type='journal' or
                                       @publication-type='newspaper']
                    and following-sibling::*[1]/self::edition">
          <xsl:text> </xsl:text>
        </xsl:when>
        <xsl:when test="parent::node()[@publication-type='discussion' and
                                      @publication-format='list']">
          <xsl:if test="following-sibling::*">
            <xsl:text>. </xsl:text>
          </xsl:if>
        </xsl:when>
        <xsl:when test="parent::node()[@publication-type='wiki']">
          <xsl:if test="following-sibling::*">
            <xsl:text>. </xsl:text>
          </xsl:if>
        </xsl:when>
        <xsl:when test="following-sibling::*[1]/self::publisher-loc and
                        preceding-sibling::article-title">
          <xsl:text> </xsl:text>
        </xsl:when>
        <xsl:when test="parent::node()[@publication-type='confproc'] and
                        following-sibling::*[1]/self::conf-date">
          <xsl:text>; </xsl:text>
        </xsl:when>
        <xsl:when test="parent::node()[@publication-type='patent'] and
                        following-sibling::*[1]/self::patent">
          <xsl:text> </xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:variable name="lastchar-punct">
            <xsl:call-template name="ends-w-punct">
              <xsl:with-param name="str" select="string(.)"/>
            </xsl:call-template>
          </xsl:variable>
          <xsl:if test="$lastchar-punct!='yes'">
            <xsl:text>.</xsl:text>
          </xsl:if>
          <xsl:text> </xsl:text>
        </xsl:otherwise>
      </xsl:choose>
  </xsl:template>


  <xsl:template match="std">
    <!-- Authority: the "Blue" spec. and by analogy with
           the "article-title" element. -->
    <xsl:apply-templates/>
    <xsl:variable name="lastchar-punct">
      <xsl:call-template name="ends-w-punct">
        <xsl:with-param name="str" select="string(.)"/>
      </xsl:call-template>
    </xsl:variable>
    <xsl:if test="$lastchar-punct!='yes'">
      <xsl:text>.</xsl:text>
    </xsl:if>
    <xsl:text> </xsl:text>
  </xsl:template>


  <xsl:template match="supplement">
    <!-- Authority: cit-render, mode="add-punct" -->
    <xsl:apply-templates/>
    <xsl:if test="following-sibling::*">
      <xsl:text>:</xsl:text>
    </xsl:if>
  </xsl:template>


  <xsl:template match="time-stamp">
    <!-- Authority ViewNLM, mode="nscitation"
         Note that this element also occurs in mode="book",
         where it's suppressed. -->
    <xsl:apply-templates/>
    <xsl:text> </xsl:text>
  </xsl:template>


  <xsl:template match="trans-source">
    <!-- Authority: cit-render, mode="add-punct" -->
    <!-- Note: @id suppressed. -->
    <xsl:text>[</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>]. </xsl:text>
  </xsl:template>


  <xsl:template match="trans-title">
    <!-- Authority: cit-render, mode="add-punct" -->
    <!-- Note: @id suppressed. -->
    <xsl:text>[</xsl:text>
    <xsl:apply-templates/>
    <xsl:choose>
      <xsl:when test="parent::node()[@publication-type='confproc']
                   or parent::node()[@publication-type='discussion' and
                                     @publication-format='list']">
        <xsl:text>]. In: </xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>]. </xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


  <xsl:template match="volume">
    <!-- Authority: cit-render, mode="add-punct" -->
    <xsl:apply-templates/>
    <xsl:choose>
      <xsl:when test="following-sibling::*[1]/self::supplement">
        <xsl:text> </xsl:text>
      </xsl:when>
      <xsl:when test="following-sibling::issue"/>
      <xsl:when test="parent::node()[@publication-type='book' or
                                     @publication-type='confproc']">
        <xsl:text>. </xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>:</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


  <xsl:template match="volume-id">
    <!-- Authority: the "Blue" spec. plus analogy with the
           "pub-id" element. -->
    <xsl:apply-templates select="@pub-id-type"/>
    <xsl:apply-templates/>
    <xsl:if test="following-sibling::*">
      <xsl:variable name="lastchar-punct">
        <xsl:call-template name="ends-w-punct">
          <xsl:with-param name="str" select="string(.)"/>
        </xsl:call-template>
      </xsl:variable>
      <xsl:if test="$lastchar-punct='no'">
        <xsl:text>.</xsl:text>
      </xsl:if>
      <xsl:text> </xsl:text>
    </xsl:if>
  </xsl:template>


  <xsl:template match="year">
    <!-- Authority: cit-render, mode="add-punct" -->
    <xsl:apply-templates/>
    <xsl:choose>
      <xsl:when test="parent::*[@publication-type='journal' or
                                @publication-type='newspaper']">
        <xsl:choose>
          <xsl:when test="following-sibling::month
                  or following-sibling::season
                  or following-sibling::*[1]/self::date-in-citation">
            <xsl:text> </xsl:text>
          </xsl:when>
          <xsl:otherwise>
            <xsl:text>;</xsl:text>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:when test="following-sibling::month
                   or following-sibling::season
                   or following-sibling::*[1]/self::date-in-citation">
        <xsl:text> </xsl:text>
      </xsl:when>
      <xsl:when test="following-sibling::*">
        <xsl:text>. </xsl:text>
      </xsl:when>
    </xsl:choose>
  </xsl:template>


<!-- =============================================================== -->
<!-- "format" mode: maps arbitrary citation element contents into
     formatted equivalents in the "simple citation" element subset   -->
<!-- =============================================================== -->

  <xsl:template match="*" mode="format">
    <xsl:apply-templates mode="format"/>
  </xsl:template>


  <xsl:template mode="format"
    match="mixed-citation/text()[not(normalize-space())] |
           product/text()[not(normalize-space())] |
           related-article/text()[not(normalize-space())] |
           related-object/text()[not(normalize-space())] |
           string-name/text()[not(normalize-space())]">
    <!-- we strip leading and trailing whitespace from these
         elements just in case -->
    <xsl:if test="preceding-sibling::* and following-sibling::*">
      <xsl:value-of select="."/>
    </xsl:if>
  </xsl:template>

  
  <xsl:template match="person-group" mode="format">
    <xsl:apply-templates select="*"/>
  </xsl:template>


  <xsl:template match="name | date" mode="format">
    <xsl:for-each select="*">
      <xsl:apply-templates/>
      <xsl:if test="not(position() = last())">
        <xsl:text> </xsl:text>
      </xsl:if>
    </xsl:for-each>
  </xsl:template>


  <xsl:template mode="format"
    match="bold | italic | monospace | overline | roman |
                sans-serif | sc | strike | underline | inline-graphic |
                label | email | ext-link | uri | sub | sup | styled-content">
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <xsl:apply-templates mode="format"/>
    </xsl:copy>
  </xsl:template>


<!-- =============================================================== -->
<!-- General mapping of the @pub-id-type attribute to a string.      -->
<!-- =============================================================== -->

<xsl:template match="@pub-id-type">
  <xsl:choose>
    <xsl:when test=".='doi'">
      <xsl:text>DOI: </xsl:text>
    </xsl:when>
    <xsl:when test=".='medline'">
      <xsl:text>Medline: </xsl:text>
    </xsl:when>
    <xsl:when test=".='pii'">
      <xsl:text>PII: </xsl:text>
    </xsl:when>
    <xsl:when test=".='pmid'">
      <xsl:text>PUBMED ID: </xsl:text>
    </xsl:when>
    <xsl:when test=".='sici'">
      <xsl:text>SICI: </xsl:text>
    </xsl:when>
    <xsl:when test=".='coden'">
      <xsl:text>PDB/CCDC ID: </xsl:text>
    </xsl:when>
    <xsl:when test=".='doaj'">
      <xsl:text>DOAJ: </xsl:text>
    </xsl:when>
    <xsl:when test=".='manuscript'">
      <xsl:text>Manuscript: </xsl:text>
    </xsl:when>
    <xsl:when test=".='pmcid'">
      <xsl:text>PUBMED Central: </xsl:text>
    </xsl:when>
    <!-- Other cases for which the text is empty:
         art-access-id
         other
         publisher-id
      -->
  </xsl:choose>
</xsl:template>


<!-- =============================================================== -->
<!-- Person group type, pluralized if needed.                        -->
<!-- =============================================================== -->

  <xsl:template name="pgt-number-agreement">
    <xsl:param name="pgt"/>
    <xsl:param name="num" select="1"/>
    <xsl:choose>
      <xsl:when test="$pgt='transed'">
        <xsl:choose>
          <xsl:when test="$num > 1">
            <xsl:text>editors and translators</xsl:text>
          </xsl:when>
          <xsl:otherwise>
            <xsl:text>editor and translator</xsl:text>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$pgt"/>
        <xsl:if test="$num > 1">
          <xsl:text>s</xsl:text>
        </xsl:if>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


<!-- =============================================================== -->
<!-- Test for ending punctuation in a string.                        -->
<!-- =============================================================== -->

  <xsl:template name="ends-w-punct">
    <xsl:param name="str"/>
    <xsl:choose>
      <xsl:when test="contains('.!?',
                               substring($str,string-length($str),1))">
        <xsl:text>yes</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>no</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


</xsl:stylesheet>
