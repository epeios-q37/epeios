<?xml version="1.0" encoding="utf-8"?><xsl:stylesheet	version="1.0"                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"                xmlns="http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul">	<xsl:output method="xml"              indent="yes"              encoding="utf-8"              omit-xml-declaration="yes"              standalone="yes"/>  <xsl:include href="shape.xsl"/>	<xsl:template match="/">		<xsl:apply-templates select="States"/>	</xsl:template>	<xsl:template match="States">		<xsl:apply-templates select="Epeios"/>	</xsl:template>	<xsl:template match="Epeios">		<xsl:if test="ProjectInProgress='false'">			<xsl:call-template name="Shape">				<xsl:with-param name="Id">shpCloseProject</xsl:with-param>				<xsl:with-param name="Value">Disable</xsl:with-param>			</xsl:call-template>		</xsl:if>	</xsl:template></xsl:stylesheet>