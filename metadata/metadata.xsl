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
    <xsl:param name="metadata" select="document($metadataFile)" />
    
    <xsl:output method="xml" doctype-public="-//NLM//DTD Journal Publishing DTD v3.0 20080202//EN" doctype-system="http://dtd.nlm.nih.gov/publishing/3.0/journalpublishing3.dtd" xpath-default-namespace="" indent="yes"></xsl:output>
    
    <xsl:param name="verbose">False</xsl:param>

    
    <xsl:template match="/">
        <xsl:if test="$verbose='true'">
            <xsl:message>Beginning metadata process</xsl:message>
        </xsl:if>
        
        <xsl:element name="article">
            <xsl:call-template name="header"/>
            
            <xsl:if test="$verbose='true'">
                <xsl:message>Copying other elements</xsl:message>
            </xsl:if>
            
            <xsl:apply-templates select="/*"/>
            
        </xsl:element>
    </xsl:template>
    
    <!--
        Here we re-write the header in its entirety from the metadata values.
        -->
    <xsl:template name="header">
        <xsl:if test="$verbose='true'">
            <xsl:message>Beginning metadata transform</xsl:message>
        </xsl:if>
        
        <xsl:element name="front">
            <xsl:copy-of select="$metadata/*/*"/>
        </xsl:element>
    </xsl:template>
    
    <xsl:template name="copy-all" match="/*">
        <xsl:for-each select="/*/*[not(name()='front')]">
            <xsl:if test="$verbose='true'">
                <xsl:message>Copying element <xsl:value-of select="name()"/></xsl:message>
            </xsl:if>
            <xsl:copy-of select="self::node()[not(/*/front/*[name()=name(current())])]"/>
        </xsl:for-each>
    </xsl:template>
    
</xsl:stylesheet>