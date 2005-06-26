<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:date="http://exslt.org/dates-and-times"
                exclude-result-prefixes="date"
                version='1.0'>

<xsl:import href="http://docbook.sourceforge.net/release/website/current/xsl/tabular.xsl"/>

<xsl:param name="suppress.navigation">1</xsl:param>

<xsl:template name="user.footer.content">
  <meta name="date">
    <xsl:attribute name="content">
      <xsl:call-template name="datetime.format">
        <xsl:with-param name="date" select="date:date-time()"/>
        <xsl:with-param name="format" select="'d B, Y'"/>
      </xsl:call-template>
    </xsl:attribute>
  </meta>
</xsl:template>

<!-- Replace the text in these templates with whatever you want -->
<!-- to appear in the respective location on the home page. -->

<xsl:template name="home.navhead">
<xsl:text></xsl:text>
</xsl:template>

<xsl:template name="home.navhead.upperright">
<xsl:text></xsl:text>
</xsl:template>

<!-- put your customizations here -->
</xsl:stylesheet>
