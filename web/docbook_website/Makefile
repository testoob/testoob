DOCBOOK_WEBSITE=http://docbook.sourceforge.net/release/website/current

CUSTOM_STYLESHEET=testoob_website.xsl

# generate non-tabular output instead of tabular? 1=Yes 0=No
MAKENONTAB=0

# use HTML Tidy to pretty-print HTML? 1=Yes 0=No
USETIDY=0
# specifies how to call tidy
TIDY=tidy
# specifies options to feed to tidy
TIDYOPTS=-iq -latin1 -mn

XSLT=xsltproc

# XMLPARSER specifies command for calling your preferred XML
# parser for validating the DocBook XML sources for your site
XMLPARSER=xmllint --valid --noout

# the following is empty by default; put any custom DocBook
# stylesheet params you want here; they will be applied globally
# to all HTML transformations from your DocBook XML sources
STYLEOPT=

# name of directory to use if chunking output with "make chunk"
DESTPATH=.

# what prefix to use on non-tabular versions HTML files?
NONTABPREFIX=n-

TABSTYLE      =  $(DOCBOOK_WEBSITE)/xsl/tabular.xsl
WEBSTYLE      =  $(DOCBOOK_WEBSITE)/xsl/website.xsl
TABCHUNK      =  $(DOCBOOK_WEBSITE)/xsl/chunk-tabular.xsl
WEBCHUNK      =  $(DOCBOOK_WEBSITE)/xsl/chunk-website.xsl
AUTOLAYOUT    =  $(DOCBOOK_WEBSITE)/xsl/autolayout.xsl 
MAKEDEPENDS   =  $(DOCBOOK_WEBSITE)/xsl/makefile-dep.xsl
MAKETARGETSDB =  $(DOCBOOK_WEBSITE)/xsl/website-targets.xsl

XMLDEPENDS    = autolayout.xml website.database.xml

.PHONY : clean

all: news.rss
	$(MAKE) website
	#$(MAKE) MAKENONTAB=1 website

news.rss:
	wget 'http://sourceforge.net/export/rss2_projnews.php?group_id=138557' -O news.rss

ifeq ($(MAKENONTAB),0)
#STYLESHEET=$(TABSTYLE)
STYLESHEET=$(CUSTOM_STYLESHEET)
STYLECHUNK=$(TABCHUNK)
NONTAB_OPT=
-include depends.tabular
else
STYLESHEET=$(WEBSTYLE)
STYLECHUNK=$(WEBCHUNK)
ifeq ($(basename $(XSLT)),xsltproc)
NONTAB_OPT= --stringparam filename-prefix $(NONTABPREFIX)
else
NONTAB_OPT= filename-prefix=$(NONTABPREFIX)
endif
-include depends.nontabular
endif

autolayout.xml: layout.xml
	$(XMLPARSER) $(filter-out $(XMLDEPENDS),$^)
ifeq ($(basename $(XSLT)),xsltproc)
	$(XSLT) $(AUTOLAYOUT) $< > $@
else
	$(XSLT) $< $(AUTOLAYOUT) use.extensions=1 > $@
endif

chunk: autolayout.xml
ifeq ($(basename $(XSLT)),xsltproc)
	$(XSLT) --param output-root $(DESTPATH) $(STYLECHUNK) autolayout.xml
else
	$(XSLT) autolayout.xml $(STYLECHUNK) use.extensions=1 output-root=$(DESTPATH)
endif

%.html: autolayout.xml website.database.xml
	$(XMLPARSER) $(filter-out $(XMLDEPENDS),$^)
ifeq ($(basename $(XSLT)),xsltproc)
	$(XSLT) $(NONTAB_OPT) $(STYLEOPT) $(STYLESHEET) $(filter-out $(XMLDEPENDS),$^) > $@
else
	$(XSLT) $(filter-out $(XMLDEPENDS),$^) $(STYLESHEET) $(NONTAB_OPT) $(STYLEOPT) use.extensions=1 > $@ 
endif
ifeq ($(USETIDY),1)
	-$(TIDY) -iq -latin1 -mn $@
endif

# RDDL gets its own rule because we never want to call tidy on it
ifeq ($(MAKENONTAB),0)
rddl.html: autolayout.xml
else
$(NONTABPREFIX)rddl.html: autolayout.xml
endif
	$(XMLPARSER) $(filter-out $(XMLDEPENDS),$^)
ifeq ($(basename $(XSLT)),xsltproc)
	$(XSLT) $(NONTAB_OPT) $(STYLEOPT) $(STYLESHEET) $(filter-out $(XMLDEPENDS),$^) > $@
else
	$(XSLT) $(filter-out $(XMLDEPENDS),$^) $(STYLESHEET) $(NONTAB_OPT) $(STYLEOPT) use.extensions=1 > $@
endif

depends.tabular depends.nontabular: autolayout.xml
ifeq ($(basename $(XSLT)),xsltproc)
	$(XSLT) --stringparam depends-file $@ $(NONTAB_OPT) $(MAKEDEPENDS) $< > $@
else
	$(XSLT) $< $(MAKEDEPENDS) depends-file=$@ $(NONTAB_OPT) use.extensions=1 > $@
endif

website.database.xml: autolayout.xml
ifeq ($(basename $(XSLT)),xsltproc)
	$(XSLT) $(MAKETARGETSDB) $< > $@
else
	$(XSLT) $< $(MAKETARGETSDB) use.extensions=1 > $@
endif

ifeq ($(MAKENONTAB),0)
depends: autolayout.xml website.database.xml depends.tabular
else
depends: autolayout.xml website.database.xml depends.nontabular
endif

realclean: clean
	#rm -f news.rss
ifeq ($(MAKENONTAB),0)
	rm -f autolayout.xml depends.tabular website.database.xml
else
	rm -f autolayout.xml depends.nontabular website.database.xml
endif

SITE_TARGET_DIR=~/public_html/docbook
.PHONY: deploy
deploy:
	rm -fr $(SITE_TARGET_DIR)
	cp -Rf . $(SITE_TARGET_DIR)
	rm -f $(SITE_TARGET_DIR)/example.css
	ln ~/t/website/example.css $(SITE_TARGET_DIR)
	chmod -R og+rX $(SITE_TARGET_DIR)

.PHONY: redo
redo: realclean all deploy

