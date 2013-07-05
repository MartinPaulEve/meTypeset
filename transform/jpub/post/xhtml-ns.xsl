<?xml version="1.0" encoding="UTF-8"?>
<!-- ============================================================= -->
<!--  MODULE:    HTML to XHTML conversion                          -->
<!--  VERSION:   1.0                                               -->
<!--  DATE:      January 2009                                      -->
<!--                                                               -->
<!-- ============================================================= -->

<!-- ============================================================= -->
<!--  SYSTEM:    NCBI Archiving and Interchange Journal Articles   -->
<!--                                                               -->
<!--  PURPOSE:   Converts HTML to XHTML, with support for MathML   -->
<!--                                                               -->
<!--  PROCESSOR DEPENDENCIES:                                      -->
<!--             XSLT 1.0. Tested using Saxon 6.5.5 and            -->
<!--             Saxon 9.1.0.3 (B and SA)                          -->
<!--                                                               -->
<!--  COMPONENTS REQUIRED:                                         -->
<!--             none (this stylesheet will run standalone)        -->
<!--                                                               -->
<!--  INPUT:     Any (though HTML tagging is expected)             -->
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

<!-- ============================================================= -->
<!--  Function of this stylesheet:

       This stylesheet accepts arbitrary XML input and casts it
       into the XHTML namespace, with the exception of MathML.
       MathML elements are renamed without a prefix, while they
       remain otherwise unchanged.

       In addition, a processing instruction is added at the top
       of the document to call in a MathML display stylesheet
       from W3C. This will enable MathML display in browsers that
       support MathML using this mechanism.                        -->
      
      

<xsl:stylesheet version="1.0"
  xmlns:mml="http://www.w3.org/1998/Math/MathML"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">


  <xsl:output method="xml" indent="no" encoding="UTF-8"/>

  <xsl:template match="/">
    <xsl:processing-instruction name="xml-stylesheet">type="text/xsl"
      href="http://www.w3.org/Math/XSL/mathml.xsl"</xsl:processing-instruction>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="*">
    <xsl:element name="{local-name()}" namespace="http://www.w3.org/1999/xhtml">
      <xsl:copy-of select="@*"/>
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="mml:*">
    <xsl:element name="{local-name()}" namespace="http://www.w3.org/1998/Math/MathML">
      <xsl:copy-of select="@*"/>
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>


  <xsl:template match="comment() | processing-instruction()">
    <xsl:copy-of select="."/>
  </xsl:template>

</xsl:stylesheet>
