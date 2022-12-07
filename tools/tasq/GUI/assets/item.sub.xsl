<?xml version="1.0" encoding="UTF-8"?>
<xpp:bloc xmlns="http://www.w3.org/1999/xhtml"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xdh="http://q37.info/ns/xdh"
  xmlns:xpp="http://epeios.q37.info/ns/xpp">
  <xsl:attribute-set name="ItemEvents">
    <xsl:attribute name="xdh:onevent">Select</xsl:attribute>
  </xsl:attribute-set>
  <xsl:attribute-set name="ItemWithChildren" use-attribute-sets="ItemEvents">
    <xsl:attribute name="class">item</xsl:attribute>
  </xsl:attribute-set>
  <xsl:attribute-set name="ItemWithoutChildren" use-attribute-sets="ItemEvents">
    <xsl:attribute name="class">tree_label item</xsl:attribute>
  </xsl:attribute-set>
  <xsl:template name="Item">
    <xsl:param name="Id" select="@id" />
    <xsl:param name="Label" select="@Title" />
    <xsl:param name="Style" />
      <xsl:choose>
        <xsl:when test="Items">
          <input type="checkbox" id="{generate-id()}" />
          <label style="color: transparent; width: 0px;" class="tree_label" for="{generate-id()}">i</label>
          <span xsl:use-attribute-sets="ItemWithChildren" id="{$Id}" style="{$Style}">
            <xsl:value-of select="$Label" />
          </span>
          <xsl:apply-templates select="Items" />
        </xsl:when>
        <xsl:otherwise>
          <span xsl:use-attribute-sets="ItemWithoutChildren" id="{$Id}" style="{$Style}">
            <xsl:value-of select="$Label" />
          </span>
        </xsl:otherwise>
      </xsl:choose>
  </xsl:template>
</xpp:bloc>