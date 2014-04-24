<?xml version="1.0"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:tei="http://www.tei-c.org/ns/1.0" xmlns:exist="http://exist.sourceforge.net/NS/exist" xmlns="" xpath-default-namespace="http://www.tei-c.org/ns/1.0" xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" exclude-result-prefixes="#all">
    <!--
    Copyright 2013 Martin Paul Eve (https://www.martineve.com)
    
    This file is released under the Mozilla Public Licence version 1.1 (MPL 1.1).
    
    This transformation is designed to rewrite a blank NLM/JATS XML header with valid data.
    
    It requires one parameter: metadataFile
    This should point to a metdata-only XML file with a root element "metadata" that is otherwise
    identical to the desired NLM "front" element.
    
    For an example, see the enclosed metadataSample.xml.
    
    This process is not particularly schema aware, so ensure that your metadata is well-formed.    
    -->
    
    <xsl:param name="metadataFile">metadata.xml</xsl:param>
    <xsl:param name="metadata" select="document(concat('file:////', $metadataFile))" />
    
    <xsl:output method="xml" doctype-public="-//NLM//DTD Journal Publishing DTD v3.0 20080202//EN" doctype-system="http://dtd.nlm.nih.gov/publishing/3.0/journalpublishing3.dtd" xpath-default-namespace="" indent="yes"></xsl:output>
       
    <xsl:template match="/">
        <xsl:element name="article">
            <xsl:apply-templates />
        </xsl:element>
    </xsl:template>
        
    <xsl:template match="/*/*">
        <xsl:choose>
            <xsl:when test="not(local-name() = 'front')">
                <xsl:copy-of select="." copy-namespaces="no"/>                
            </xsl:when>
            <xsl:otherwise>
                <xsl:element name="front">
                    <xsl:copy-of select="$metadata/*/*" copy-namespaces="no"/>
                </xsl:element>
            </xsl:otherwise>
        </xsl:choose>

    </xsl:template>
      
</xsl:stylesheet>