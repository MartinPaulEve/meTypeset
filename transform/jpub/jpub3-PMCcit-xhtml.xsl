<?xml version="1.0" encoding="UTF-8"?>
<!-- ============================================================= -->
<!--  MODULE:    Saxon shell (pipelining) stylesheet               -->
<!--             XHTML Preview with NLM/Pubmed citations           -->
<!--  VERSION:   1.0                                               -->
<!--  DATE:      January 2009                                      -->
<!--                                                               -->
<!-- ============================================================= -->

<!-- ============================================================= -->
<!--  SYSTEM:    NCBI Archiving and Interchange Journal Articles   -->
<!--                                                               -->
<!--  PURPOSE:   Pipelines stylesheets to convert                  -->
<!--             Journal Publishing 3.0 XML as follows:            -->
<!--             1. format citations in NLM/Pubmed style           -->
<!--             2. convert to HTML for preview display            -->
<!--             3. convert to XHTML                               -->
<!--                                                               -->
<!--  PROCESSOR DEPENDENCIES:                                      -->
<!--             Saxon, from Saxonica (www.saxonica.com)           -->
<!--             Tested using Saxon 9.1.0.3 (B and SA)             -->
<!--                                                               -->
<!--  COMPONENTS REQUIRED:                                         -->
<!--             main/shell-utility.xsl, plus all the stylesheets  -->
<!--             named in the $processes variable declaration      -->
<!--                                                               -->
<!--  INPUT:     Journal Publishing 3.0 XML with citations         -->
<!--             in NLM/Pubmed format                              -->
<!--                                                               -->
<!--  OUTPUT:    XHTML                                             -->
<!--                                                               -->
<!--  CREATED FOR:                                                 -->
<!--             Digital Archive of Journal Articles               -->
<!--             National Center for Biotechnology Information     -->
<!--                (NCBI)                                         -->
<!--             National Library of Medicine (NLM)                -->
<!--                                                               -->
<!--  CREATED BY:                                                  -->
<!--             Wendell Piez, Mulberry Technologies, Inc.         -->
<!--                                                               -->
<!-- ============================================================= -->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:saxon="http://saxon.sf.net/"
  version="2.0"
  extension-element-prefixes="saxon">

  <!--<xsl:output method="html" omit-xml-declaration="yes"
    encoding="utf-8" indent="no"/>-->

  <xsl:output method="xhtml" omit-xml-declaration="no"
    encoding="utf-8" indent="no"
    doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN"
    doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"/>
  
  <xsl:variable name="processes">
    <!-- format citations in NLM/PMC format -->
    <step>citations-prep/jpub3-PMCcit.xsl</step>
    <!-- convert into HTML for display -->
    <step>main/jpub3-html.xsl</step>
    
    <!-- cast into XHTML namespace
           (for example, if MathML is included)
         if this step is run, the output file should be
           named with suffix .xml or .xhtml, and served
           with MIME type application/xhtml+xml -->
    <step>post/xhtml-ns.xsl</step>
  </xsl:variable>


  <xsl:include href="main/shell-utility.xsl"/>
  

</xsl:stylesheet>
