"XSL converters for XML output"

BASIC_CONVERTER="""
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:param name="date" select="'unknown'"/>
<xsl:template match="/">
    <html>
        <head><title>Testoob report</title>
        </head>
        <body>
            <h2>Summeriezed results for tests performed on <xsl:value-of select="$date"/></h2>
            <table border="1" >
                <tr><td>Name</td><td>Time</td><td>Result</td><td>Info</td></tr>
                <xsl:for-each select="testsuites/testcase">
                    <tr>
                        <td><xsl:value-of select="@name"/></td>
                        <td><xsl:value-of select="@time"/></td>
                        <xsl:choose>
                            <xsl:when test="result='success'">
                                <td><font color="green">Success</font></td>
                            </xsl:when>
                            <xsl:otherwise>
                                <td><font color="red"><xsl:value-of select="result"/></font></td>
                                <td>
                                    <pre>
                                        <xsl:value-of select="failure"/><xsl:value-of select="error"/>
                                    </pre>
                                </td>
                            </xsl:otherwise>
                        </xsl:choose>
                        
                    </tr>
                </xsl:for-each>
            </table>
        </body>
    </html>
    
</xsl:template>
</xsl:stylesheet>
"""
