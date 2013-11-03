<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns="http://www.tei-c.org/ns/1.0"
                xmlns:ve="http://schemas.openxmlformats.org/markup-compatibility/2006"
                xmlns:o="urn:schemas-microsoft-com:office:office"
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
		xmlns:tei="http://www.tei-c.org/ns/1.0"
                xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"
                xmlns:v="urn:schemas-microsoft-com:vml"
                xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
                xmlns:w10="urn:schemas-microsoft-com:office:word"
                xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
                xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml"
                xmlns:mml="http://www.w3.org/1998/Math/MathML"
                xmlns:tbx="http://www.lisa.org/TBX-Specification.33.0.html"
                
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="2.0"
                exclude-result-prefixes="ve o r m v wp w10 w wne mml
					 tei tbx">

  <doc xmlns="http://www.oxygenxml.com/ns/doc/xsl" scope="stylesheet" type="stylesheet">
      <desc>
         <p> TEI Utility stylesheet for making Word docx files from TEI XML (see tei-docx.xsl)</p>
         <p>This software is dual-licensed:

1. Distributed under a Creative Commons Attribution-ShareAlike 3.0
Unported License http://creativecommons.org/licenses/by-sa/3.0/ 

2. http://www.opensource.org/licenses/BSD-2-Clause
		
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

* Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

This software is provided by the copyright holders and contributors
"as is" and any express or implied warranties, including, but not
limited to, the implied warranties of merchantability and fitness for
a particular purpose are disclaimed. In no event shall the copyright
holder or contributors be liable for any direct, indirect, incidental,
special, exemplary, or consequential damages (including, but not
limited to, procurement of substitute goods or services; loss of use,
data, or profits; or business interruption) however caused and on any
theory of liability, whether in contract, strict liability, or tort
(including negligence or otherwise) arising in any way out of the use
of this software, even if advised of the possibility of such damage.
</p>
         <p>Author: See AUTHORS</p>
         <p>Id: $Id: pass0.xsl 11487 2013-01-20 15:46:41Z rahtz $</p>
         <p>Copyright: 2008, TEI Consortium</p>
      </desc>
   </doc>

  <xsl:key name="STYLES" match="w:style" use="@w:styleId"/>
  <xsl:param name="word-directory">..</xsl:param>
  <xsl:param name="debug">false</xsl:param>  
  
  <xsl:template match="@*|text()|comment()|processing-instruction()" mode="pass0">
      <xsl:copy-of select="."/>
  </xsl:template>
  
  <xsl:template match="w:body" mode="pass0">
    <xsl:copy>
      <xsl:choose>
	<xsl:when test="w:p[tei:is-firstlevel-heading(.)]"/>
	<xsl:otherwise>
	  <w:p>
	    <w:pPr>
	      <w:pStyle w:val="heading 1"/>
	    </w:pPr>
	    <w:r>
	      <w:rPr>
		<w:sz w:val="36"/>
	      </w:rPr>
	      <w:t/>
	    </w:r>
	  </w:p>
	</xsl:otherwise>
      </xsl:choose>
      <xsl:apply-templates select="*|@*|processing-instruction()|comment()|text()" mode="pass0"/>
    </xsl:copy>
  </xsl:template>

  
  <xsl:template match="*" mode="pass0">
      <xsl:copy>
         <xsl:apply-templates select="*|@*|processing-instruction()|comment()|text()" mode="pass0"/>
      </xsl:copy>
  </xsl:template>

  <xsl:template match="w:pStyle/@w:val|w:rStyle/@w:val" mode="pass0">
      <xsl:variable name="old" select="."/>
      <xsl:variable name="new">
	<xsl:for-each select="document($styleDoc)">
	  <xsl:value-of select="key('STYLES',$old)/w:name/@w:val"/>
	</xsl:for-each>
      </xsl:variable>
      
      <xsl:variable name="newItalic">
          <xsl:for-each select="document($styleDoc)">
              <xsl:if test="key('STYLES',$old)/w:rPr/w:i">
                  <n> italic</n>
              </xsl:if>          
          </xsl:for-each>
      </xsl:variable>
      
      <xsl:variable name="newBold">
          <xsl:for-each select="document($styleDoc)">
              <xsl:if test="key('STYLES',$old)/w:rPr/w:b">
                  <n> bold</n>
              </xsl:if>          
          </xsl:for-each>
      </xsl:variable>
      
      <xsl:attribute name="w:val">
         <xsl:choose>
	   <xsl:when test="$new=''">
	     <xsl:value-of select="$old"/>
	     <xsl:if test="$debug='true'">
	       <xsl:message>! style <xsl:value-of select="$old"/> ... NOT FOUND    </xsl:message>
	     </xsl:if>
	   </xsl:when>
	   <xsl:when test="not($new=$old)">
	     <xsl:if test="$debug='true'">
	       <xsl:message>! style <xsl:value-of select="$old"/> ... CHANGED ...  <xsl:value-of select="$new"/>
	       </xsl:message>
	     </xsl:if>
	     <xsl:value-of select="$new"/>
	       <xsl:value-of select="$newItalic"/>
	       <xsl:value-of select="$newBold"/>
	   </xsl:when>
	   <xsl:otherwise>
	     <xsl:value-of select="$old"/>
	   </xsl:otherwise>
         </xsl:choose>
      </xsl:attribute>
  </xsl:template>
  

  <xsl:template
      match="w:r[w:instrText][normalize-space(w:instrText)='']" mode="pass0"/>

</xsl:stylesheet>
