cd `dirname $0`
webgen && rm -fr ~/public_html/testoob && cp -R output ~/public_html/testoob && chmod -R og+rX ~/public_html/testoob && echo SUCCESS
