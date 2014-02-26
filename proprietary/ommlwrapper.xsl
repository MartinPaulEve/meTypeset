<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:mml="http://www.w3.org/1998/Math/MathML"
	xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">
  <xsl:output method="xml" encoding="UTF-16" />
 <xsl:include href="omml2mml.xsl"/> 
<xsl:template match="node()|@*">
  <xsl:copy>
     <xsl:apply-templates  select="node()|@*"/>
  </xsl:copy>
</xsl:template>
</xsl:stylesheet>
