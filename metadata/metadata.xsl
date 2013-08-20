<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns="http://www.tei-c.org/ns/1.0" xmlns:tei="http://www.tei-c.org/ns/1.0" xmlns:exist="http://exist.sourceforge.net/NS/exist" xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    version="1.0">
    <!--
    Copyright 2013 Martin Paul Eve (https://www.martineve.com)
    
    This file is released under the Mozilla Public Licence version 1.1 (MPL 1.1).
    
    This transformation is designed to populate the intermediary TEI metadata with output from
    a journal publishing platform, such as OJS.
    
    -->
    
    <!--
        TODOs:
        
        1.) Need to work out how to handle multiple elements here; param may not be best approach
        -->
    
    <xsl:output method="xml" doctype-public="http://www.tei-c.org/ns/1.0" xmlns="http://www.tei-c.org/ns/1.0" indent="yes"></xsl:output>
    
    <xsl:param name="verbose">False</xsl:param>
    
    <xsl:param name="article-title">Article Title</xsl:param>
    <xsl:param name="article-id">Article ID (DOI or PMID etc)</xsl:param>
    <xsl:param name="article-id-type">Article ID type (DOI or PMID etc)</xsl:param>
    
    <xsl:param name="author-forename">Author Forename</xsl:param>
    <xsl:param name="author-surname">Article Surname</xsl:param>
    
    <xsl:template match="/">
        <xsl:if test="$verbose='true'">
            <xsl:message>Beginning metadata process</xsl:message>
        </xsl:if>
        <xsl:element name="TEI">
            <xsl:attribute xmlns="xml" name="id"><xsl:value-of select="$article-id"/></xsl:attribute>
            <xsl:call-template name="header"/>
            
            <xsl:if test="$verbose='true'">
                <xsl:message>Copying other elements</xsl:message>
            </xsl:if>
            <xsl:element name="text">
                <xsl:apply-templates select="tei:TEI/tei:text/*"/>
            </xsl:element>
        </xsl:element>
    </xsl:template>
    
    <!--
        Here we re-write the header in its entirety from the metadata values.
        -->
    <xsl:template name="header">
        <xsl:if test="$verbose='true'">
            <xsl:message>Beginning metadata transform</xsl:message>
        </xsl:if>
        <xsl:element name="teiHeader">
            <xsl:element name="fileDesc">
                <xsl:element name="titleStmt">
                    <xsl:element name="title">
                        <xsl:attribute name="type">main</xsl:attribute>
                        <xsl:copy-of select="$article-title"/>
                    </xsl:element>
                    <!-- TODO: figure out how to handle multiple authors-->
                    <xsl:element name="author">
                        <xsl:element name="name">
                            <xsl:attribute name="type">person</xsl:attribute>
                            <xsl:element name="forename">
                                <xsl:copy-of select="$author-forename"/>
                            </xsl:element>
                            <xsl:element name="surname">
                                <xsl:copy-of select="$author-surname"/>
                            </xsl:element>
                        </xsl:element>
                    </xsl:element>
                </xsl:element>
                <xsl:element name="sourceDesc">
                    <p>Converted from a Microsoft Word document</p>
                </xsl:element>
            </xsl:element>
            
            <xsl:element name="articleIDs">
                <xsl:element name="id">
                    <xsl:attribute name="type"><xsl:value-of select="$article-id-type"/></xsl:attribute>
                    <xsl:value-of select="$article-id"/>
                </xsl:element>
            </xsl:element>
            
        </xsl:element>

    </xsl:template>
    
    <xsl:template name="copy-all" match="tei:TEI/tei:text/*">
        <xsl:if test="$verbose='true'">
            <!-- TODO: change to display element name, not value (I'm writing this on a plane and can't remember the xpath syntax!) -->
            <xsl:message>Copying element <xsl:value-of select="."/></xsl:message>
        </xsl:if>
        <xsl:copy-of select="."/>
    </xsl:template>
    
</xsl:stylesheet>