<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:xdh="http://q37.info/ns/xdh"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xpp="http://epeios.q37.info/ns/xpp">
  <xpp:expand href="item.sub.xsl" />
  <xsl:output method="html" indent="yes" />
  <xsl:template match="/TasQ">
    <xsl:apply-templates select="Tasks" />
  </xsl:template>
  <xsl:template match="Tasks">
    <div class="tree">
      <span xdh:onevent="Select" style="font-weight: bolder;" class="item">
        <xsl:attribute name="id">
          <xsl:value-of select="@RootTask" />
        </xsl:attribute>
        <xsl:text>Tasks</xsl:text>
      </span>
      <xsl:apply-templates select="Items" />
    </div>
  </xsl:template>
  <xsl:template match="Items">
    <ul style="margin-top: 0;">
      <xsl:apply-templates select="Item" />
    </ul>
  </xsl:template>
  <xsl:template match="Item">
    <li>
      <xsl:call-template name="Item" />
    </li>
  </xsl:template>
</xsl:stylesheet>