<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet	version="1.0"
				xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
				xmlns:xpp="http://q37.info/ns/xpp/draft"
				>
	<xsl:output method="html" encoding="UTF-8"/>
	<xsl:template match="/">
		<head>
			<xpp:expand href="styles" />
		</head>
		<body data-xdh-onevent="keypress|About|SC+a">
			<xsl:apply-templates select="*/Content"/>
		</body>
	</xsl:template>
	<xsl:template match="Content">
		<xsl:variable name="BackendType">
			<xsl:choose>
				<xsl:when test="Backend/@Type">
					<xsl:value-of select="Backend/@Type"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:value-of select="DefaultBackendType"/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:variable>
		<span class="vcenter-out">
			<span class="vcenter-in">
				<fieldset title="#lgnBackendToUse#">
					<legend>#lgnBackend#</legend>
					<div>
						<span>
							<fieldset data-xdh-cast="NoneBackendCast">
								<select id="BackendType" title="#lgnBackendType#" data-xdh-onevent="SwitchBackendType">
									<option value="Remote">
										<xsl:if test="$BackendType='Remote'">
											<xsl:attribute name="selected">selected</xsl:attribute>
										</xsl:if>
										<xsl:text>#lgnRemoteBackendOption#</xsl:text>
									</option>
									<option value="Embedded">
										<xsl:if test="$BackendType='Embedded'">
											<xsl:attribute name="selected">selected</xsl:attribute>
										</xsl:if>
										<xsl:text>#lgnEmbeddedBackendOption#</xsl:text>
									</option>
									<option value="Predefined">
										<xsl:if test="$BackendType='Predefined'">
											<xsl:attribute name="selected">selected</xsl:attribute>
										</xsl:if>
										<xsl:text>#lgnPredefinedBackendOption#</xsl:text>
									</option>
									<option value="None">
										<xsl:if test="$BackendType='None'">
											<xsl:attribute name="selected">selected</xsl:attribute>
										</xsl:if>
										<xsl:text>#lgnNoBackendOption#</xsl:text>
									</option>
								</select>
								<xsl:apply-templates select="Backends"/>
								<span style="display: inline-block;">
									<!-- if the 'style' attribute is set in the child element, the 'hidden' attribute doesn't work anymore on this child element...-->
									<fieldset title="#lgnEmbeddedBackendToUse#" data-xdh-cast="EmbeddedBackendCast">
										<legend>#lgnEmbeddedBackend#</legend>
										<xsl:variable name="OS" select="../@OS"/>
										<xsl:variable name="DynamicLibraryExtension">
											<xsl:choose>
												<xsl:when test="contains($OS,'Win')">
													<xsl:text>.dll</xsl:text>
												</xsl:when>
												<xsl:when test="contains($OS,'Darwin')">
													<xsl:text>.dylib</xsl:text>
												</xsl:when>
												<xsl:when test="contains($OS,'POSIX')">
													<xsl:text>.so</xsl:text>
												</xsl:when>
											</xsl:choose>
										</xsl:variable>
										<button	title="#lgnBrowseEmbeddedBackends#">
											<xsl:attribute name="data-xdh-onevent">
												<xsl:text>(OpenFile|DisplayEmbeddedBackendFilename|(#lgnSelectEmbeddedBackend#|</xsl:text>
												<xsl:value-of select="$DynamicLibraryExtension"/>
												<xsl:text>|</xsl:text>
												<xsl:text>xmple</xsl:text>
												<xsl:value-of select="$DynamicLibraryExtension"/>
												<xsl:text>))</xsl:text>
											</xsl:attribute>#lgnBrowse#
										</button>
										<input id="EmbeddedBackend" type="text" size="50">
											<xsl:if test="Backend/@Type='Embedded'">
												<xsl:attribute name="value">
													<xsl:value-of select="Backend"/>
												</xsl:attribute>
											</xsl:if>
										</input>
									</fieldset>
								</span>
								<input id="RemoteBackend" title="#lgnRemoteBackendToUse#" placeholder="#lgnAddressPort#" type="text" data-xdh-cast="RemoteBackendCast">
									<xsl:if test="Backend/@Type='Remote'">
										<xsl:attribute name="value">
											<xsl:value-of select="Backend"/>
										</xsl:attribute>
									</xsl:if>
								</input>
							</fieldset>
						</span>
						<span class="hcenter">
							<button title="#lgnConnectToBackend#" data-xdh-onevent="Connect">#lgnOK#</button>
							<button title="#lgnCancelConnection#" data-xdh-onevent="Dismiss">#lgnCancel#</button>
						</span>
					</div>
				</fieldset>
			</span>
		</span>
	</xsl:template>
	<xsl:template match="Backends">
		<select title="#lgnPredefinedBackends#" id="PredefinedBackend"  data-xdh-cast="PredefinedBackendCast">
			<xsl:apply-templates select="Backend"/>
		</select>
	</xsl:template>
	<xsl:template match="Backend">
		<option>
			<xsl:if test="@Selected='true'">
				<xsl:attribute name="selected">selected</xsl:attribute>
			</xsl:if>
			<xsl:attribute name="value">
				<xsl:value-of select="@id"/>
			</xsl:attribute>
			<xsl:value-of select="@Alias"/>
		</option>
	</xsl:template>
</xsl:stylesheet>