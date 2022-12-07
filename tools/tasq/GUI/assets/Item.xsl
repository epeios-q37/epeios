<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xdh="http://q37.info/ns/xdh"
  xmlns:xpp="http://epeios.q37.info/ns/xpp">
  <xpp:expand href="item.sub.xsl" />
  <xsl:output method="html" indent="yes" />
  <xsl:template match="/Tasks">
    <xsl:apply-templates select="Item" />
  </xsl:template>
  <xsl:template match="Item">
    <xsl:choose>
      <xsl:when test="Items">
        <xsl:call-template name="Item" />
      </xsl:when>
      <xsl:otherwise>
        <li>
          <xsl:call-template name="Item" />
        </li>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  <xsl:template match="Items">
    <ul>
      <xsl:apply-templates select="Item" />
    </ul>
  </xsl:template>
</xsl:stylesheet>