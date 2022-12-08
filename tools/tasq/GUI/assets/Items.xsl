<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xdh="http://q37.info/ns/xdh"
  xmlns:xpp="http://epeios.q37.info/ns/xpp">
  <xpp:expand href="item.sub.xsl" />
  <xsl:output method="html" indent="yes" />
  <xsl:template match="/Tasks">
    <ul class="tree">
      <li>
        <xsl:call-template name="Item">
          <xsl:with-param name="Id" select="@RootId" />
          <xsl:with-param name="Label">Tasks</xsl:with-param>
          <xsl:with-param name="Style">border: double; padding: 0 5px 0 5px;</xsl:with-param>
        </xsl:call-template>
      </li>
    </ul>
  </xsl:template>
  <xsl:template match="Items">
    <ul>
      <xsl:apply-templates select="Item" />
    </ul>
  </xsl:template>
  <xsl:template match="Item">
    <li>
      <xsl:call-template name="Item" />
    </li>
  </xsl:template>
</xsl:stylesheet>