<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xdh="http://q37.info/ns/xdh">
  <xsl:import href="item.sub.xsl"/>
  <xsl:output method="html" indent="yes" />
  <xsl:template match="/Tasks">
    <ul>
      <xsl:apply-templates select="Item" />
    </ul>
  </xsl:template>
  <xsl:template match="Item">
    <xsl:call-template name="Item" />
  </xsl:template>
</xsl:stylesheet>