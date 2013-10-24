#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
The MIT License (MIT)

Copyright (c) 2013 Nicolò Tambone

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

import os
import re
import sys
import getopt
import zipfile
from bs4 import BeautifulSoup


class OdtDocument():

    def __init__(self, fin=""):
        # document metadata
        self.meta_title = unicode("")
        self.meta_initial_creator = unicode("")
        self.meta_date = unicode("")

        # document language (change with param -l <lang>
        self.language = unicode("en")

        #style sheet name
        self.stylesheet_name = "style.css"

        self.filename_in = fin
        self.style_fontstyle = {}
        self.style_fontweight = {}
        self.style_textunderline = {}
        self.style_textalignment = {}
        self.style_break_before = {}
        # counter of the h<n> elements
        self.heading_id_count = 0
        # contains h<n> element values (titles)
        # index is by position starting from 1 (self.heading_list[0] = ["-", "-"])
        # each item is a list so formed [<"heading element">, <"heading level">]
        self.heading_list = [[unicode("-"), unicode("-")]]

        __fname = re.split(r"\.", self.filename_in)

        if __fname:
           self.filename_out = __fname[0] + ".html"
           self.xml_doc = __fname[0] + ".xml"


    def dumpxml(self):
        src = zipfile.ZipFile(self.filename_in)
        lst = src.infolist()
        try:
            for l in lst:
                # extract the document in xml format
                if l.orig_filename == 'content.xml':
                    fw = open(self.xml_doc, 'w')
                    content = src.read(l.orig_filename)
                    fw.write(content)
                    fw.close()
                # extract the metadata xml
                elif l.orig_filename == 'meta.xml':
                    fw = open('meta.xml', 'w')
                    meta = src.read(l.orig_filename)
                    fw.write(meta)
                    fw.close()
                else:
                    pass


        except:
            print "Error processing input file!"


    def outliner(self, str=unicode(""), outline_level=unicode(""), style_name=unicode("")):
        """
         Encloses the unicode str between <p> or <h[n]> tags,
         according to the given outline_level

        """

        paragraph_style = unicode("p-style-left")

        break_before = unicode("")

        class_tag = unicode("")

        try:
            paragraph_style = unicode("p-style-%s" % self.style_textalignment[style_name])

        except:
            pass

        try:
                break_before = unicode("p-style-%s-break-before" % self.style_break_before[style_name])

        except:
            pass

        # make up the class tag for styling the paragraph
        class_tag = unicode("class=\"%s %s\"" % (paragraph_style, break_before))

        if outline_level == "paragraph":
            if str:
                sret = unicode('<p %s>%s</p>' % (class_tag, str)) + os.linesep
            else:
                sret = unicode('<p %s></p>' % class_tag) + os.linesep

        else:
                self.heading_id_count = self.heading_id_count + 1
                s_id_cnt = unicode(self.heading_id_count)
                sret = unicode('<h%s id="heading_id_%s" %s>%s</h%s>' % (outline_level, s_id_cnt, class_tag, str, outline_level)) + os.linesep
                self.heading_list.append([unicode(str), unicode(outline_level)])

        return sret


    def stylizer(self, str=unicode(""), style_name=unicode("")):
      """
       Place <i> or <b> ora <span style="..."> tags according to the current style_name
      """
      sret = str

      try:

        if self.style_fontstyle[style_name] == "italic":
            sret = unicode("<i>%s</i>" % sret)

      finally:

        try:

          if self.style_fontweight[style_name] == "bold":
            sret = unicode("<b>%s</b>" % sret)

        finally:

          try:

            if self.style_textunderline[style_name] == "underlined":
              sret = unicode('<span style="text-decoration: underline;">%s</span>' % sret)

          finally:
                return sret


    def load_metadata(self):
        """

         Loads metadata info from meta.xml
         Those data include: title, author name, last save date

        """
        handler = open('meta.xml').read()
        soup = BeautifulSoup(handler, 'xml')

        for meta in soup.find_all(re.compile("^title")):
            if meta.string:
                self.meta_title = unicode(meta.string)

        for meta in soup.find_all(re.compile("^initial.creator")):
            if meta.string:
                self.meta_initial_creator = unicode(meta.string)

        for meta in soup.find_all(re.compile("^date")):
            if meta.string:
                self.meta_date = unicode(meta.string)


    def xml2html(self):
        """
        Converts self.xml_doc to html (self.filename_out)

        """
        handler = open(self.xml_doc).read()
        soup = BeautifulSoup(handler, 'xml')

        fw = open(self.filename_out, 'w')

        fw.write("<!DOCTYPE html>" + os.linesep)
        fw.write("<html>" + os.linesep)
        fw.write("<head>" + os.linesep)
        fw.write('<meta http-equiv="Content-Type" content="text/html; charset=utf-8">' + os.linesep)
        fw.write("<link rel=\"stylesheet\" href=\"%s\" type=\"text/css\" />" % self.stylesheet_name + os.linesep)
        fw.write("<title></title>" + os.linesep)
        fw.write("</head>" + os.linesep)
        fw.write("<body>" + os.linesep)

        # Load styles in dictionaries
        for style in soup.find_all("style"):
            style_name = style.get("style:name")
            #print "style: %s children: %s descendants: %s" % (str(style_name), str(len(list(style.children))), len(list(style.descendants)))
            for style_child in style.children:
                fs = style_child.get("fo:font-style")
                if fs:
                    self.style_fontstyle[style_name] = fs
                fontw = style_child.get("fo:font-weight")
                if fontw:
                    self.style_fontweight[style_name] = fontw
                # read alignment
                txta = style_child.get("fo:text-align")
                if txta:
                    self.style_textalignment[style_name] = txta
                # !!!
                tu = style_child.get("style:text-underline-type")
                if tu:
                    self.style_textunderline[style_name] = "underlined"
                # page break
                break_before = style_child.get("fo:break-before")
                if break_before:
                    self.style_break_before[style_name] = break_before


        # Navigate down the document through h and p tags
        #
        for text in soup.find_all(re.compile("^h|^p")):

                   # From bs4 docs: If a tag has only one child, and that child is a NavigableString, the child is made available as .string:
                   # This covers the following case (e.g.):
                   #
                   # <text:p text:style-name="P9">- Any text here!</text:p>
                   #
                   # To do:
                   #
                   # Beware of this case:
                   # - <text:p text:style-name="P8">
                   #     <text:span text:style-name="T4">
                   #

                   # Get the attributes so the styles and the outlines
                   text_attrs = dict(text.attrs)

                   # Get the styles, if any
                   try:
                       t_style = text_attrs["text:style-name"]
                   except:
                       t_style = "nostyle"

                   # Get the outline-levels, if any
                   try:
                       t_outline_level = text_attrs["text:outline-level"]
                   except:
                       t_outline_level = "paragraph"

                   if text.string:
                       t = unicode(text.string)
                       if t:
                           fw.write(self.outliner(self.stylizer(t, t_style), t_outline_level, t_style).encode('utf-8'))

                   # e.g. page breaks come as a node with no children whose style contains fo:break-before:"page"
                   elif len(list(text.children)) == 0:
                        fw.write(self.outliner(unicode(""), t_outline_level, t_style).encode('utf-8'))

                   # This covers the following case (e.g.):
                   #
                   # <text:p text:style-name="Textbody">
                   #  jkjksk skjkjkjs dhh
                   #  <text:s />
                   #  <text:span text:style-name="T3">Bold</text:span>
                   #  <text:s />
                   # </text:p>
                   #
                   # else drill down one level
                   else:
                       buffer = unicode("")
                       t = buffer
                       u = buffer
                       t_outline_level = "paragraph"
                       t_style = ""
                       for i in text.children:
                           # Get the attributes so the styles
                           try:
                               text_attrs = dict(i.attrs)
                               t_style = text_attrs["text:style-name"]
                           except:
                               # whenever the element has no style
                               # take the parent's one
                               try:
                                   text_attrs = dict(i.parent.attrs)
                                   t_style = text_attrs["text:style-name"]
                               except:
                                   t_style = "nostyle"

                           # Get the outline-levels, if any
                           try:
                               t_outline_level = text_attrs["text:outline-level"]
                           except:
                               t_outline_level = "paragraph"

                           # if the current tag has only one child, and that child is a NavigableString
                           if i.string:
                               t = unicode(i.string)

                           # space
                           elif i.name == "s":
                               t = unicode("&nbsp;")

                           # else drill down another level
                           else:
                               t = unicode("")
                               for j in i.children:
                                   if j.string:
                                       u = unicode(j.string)
                                   elif j.name == "s":
                                       u = unicode("&nbsp;")
                                   else:
                                       u = unicode("")
                                   if u:
                                       t = t + self.stylizer(u, t_style)

                           # build up a unicode string containing the whole paragraph
                           if t:
                               buffer = buffer + self.stylizer(t, t_style)

                       # outline the buffered unicode string and write it to the output file
                       fw.write(self.outliner(buffer, t_outline_level, t_style).encode('utf-8'))

        fw.write("</body>" + os.linesep)
        fw.write("</html>" + os.linesep)
        fw.close()


    def content_opf(self):
        """
         Writes content.opf
        """

        fw = open("content.opf", 'w')
        fw.write('<?xml version="1.0" encoding="UTF-8"?>' + os.linesep)
        fw.write('  <package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookID" version="2.0">' + os.linesep)
        fw.write('    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">' + os.linesep)
        fw.write('      <dc:identifier id="BookID" opf:scheme="UUID"></dc:identifier>' + os.linesep)
        fw.write('      <dc:contributor opf:role="bkp"></dc:contributor>' + os.linesep)
        fw.write('        <dc:date opf:event="creation">%s</dc:date>' % self.meta_date + os.linesep)
        fw.write("        <dc:creator opf:role=\"aut\">%s</dc:creator>" % self.meta_initial_creator + os.linesep)
        fw.write('        <dc:language>%s</dc:language>' % self.language + os.linesep)
        fw.write('        <dc:publisher></dc:publisher>' + os.linesep)
        fw.write('        <dc:title>%s</dc:title>' % self.meta_title + os.linesep)
        fw.write('        <meta name="alivetree" content="beta 0.1"/>' + os.linesep)
        fw.write('        <meta name="cover" content="cover.jpg"/>' + os.linesep)
        fw.write('    </metadata>' + os.linesep)
        fw.write('    <manifest>' + os.linesep)
        fw.write('        <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>' + os.linesep)
        fw.write('        <item id="cover.jpg" href="images/cover.jpg" media-type="image/jpeg"/>' + os.linesep)
        fw.write('        <item id="%s" href="%s" media-type="text/html"/>' % (self.filename_out, self.filename_out) + os.linesep)
        fw.write('        <item id="toc.html" href="toc.html" media-type="text/html"/>' + os.linesep)
        fw.write('    </manifest>' + os.linesep)
        fw.write('    <spine toc="ncx">' + os.linesep)
        fw.write('        <itemref idref="toc.html"/>' + os.linesep)
        fw.write('        <itemref idref="%s"/>' % self.filename_out + os.linesep)
        fw.write('    </spine>' + os.linesep)
        fw.write('    <guide>' + os.linesep)
        fw.write('       <reference type="toc" title="Table of contents" href="toc.html"/>' + os.linesep)
        fw.write('    </guide>' + os.linesep)
        fw.write('  </package>' + os.linesep)
        fw.close()


    def toc_ncx(self):
        """
         Writes toc.ncx
        """

        fw = open("toc.ncx", "w")
        fw.write('<?xml version="1.0"?>' + os.linesep)
        fw.write('<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"' + os.linesep)
        fw.write('    "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">' + os.linesep)
        fw.write('<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">' + os.linesep)
        fw.write('    <head>' + os.linesep)
        fw.write('        <meta name="dtb:uid" content=""/>' + os.linesep)
        fw.write('        <meta name="dtb:depth" content=""/>' + os.linesep)
        fw.write('        <meta name="dtb:totalPageCount" content="0"/>' + os.linesep)
        fw.write('        <meta name="dtb:maxPageNumber" content="0"/>' + os.linesep)
        fw.write('    </head>' + os.linesep)
        fw.write('    <docTitle>' + os.linesep)
        fw.write('        <text></text>' + os.linesep)
        fw.write('    </docTitle>' + os.linesep)
        fw.write('    <navMap>' + os.linesep)


        for i in range(1, len(self.heading_list)):
            fw.write('      <navPoint id="navPoint-%s" playOrder="%s">' % (unicode(i), unicode(i)) + os.linesep)
            fw.write('        <navLabel>' + os.linesep)
            fw.write('          <text>%s</text>' % self.heading_list[i][0] + os.linesep)
            fw.write('        </navLabel>' + os.linesep)
            fw.write('        <content src="%s#heading_id_%s"/>' % (self.filename_out, unicode(i)) + os.linesep)
            fw.write('      </navPoint>' + os.linesep)

        fw.write('  </navMap>' + os.linesep)
        fw.write('</ncx>' + os.linesep)
        fw.close()


    def toc_html(self):
        """
         Writes toc.html
        """
        fw = open("toc.html", 'w')

        fw.write("<!DOCTYPE html>" + os.linesep)
        fw.write("<html>" + os.linesep)
        fw.write("<head>" + os.linesep)
        fw.write('<meta http-equiv="Content-Type" content="text/html; charset=utf-8">' + os.linesep)
        fw.write("<link rel=\"stylesheet\" href=\"%s\" type=\"text/css\" />" % self.stylesheet_name + os.linesep)
        fw.write("<title>Table of contents</title>" + os.linesep)
        fw.write("</head>" + os.linesep)
        fw.write("<body>" + os.linesep)
        fw.write("<h1 class=\"p-style-center\">%s</h1>" % self.meta_title + os.linesep)
        fw.write("<div>" + os.linesep)

        for i in range(1, len(self.heading_list)):
            # to do: different styles according to heading level self.heading_list[i[1]]
            fw.write("<p class=\"toc-level-%s\"><a href=\"%s#heading_id_%s\">%s</a></p>" % (self.heading_list[i][1], self.filename_out, unicode(i), self.heading_list[i][0]) + os.linesep)

        fw.write("</div>" + os.linesep)
        fw.write("</body>" + os.linesep)
        fw.write("</html>" + os.linesep)
        fw.close()


    def style_css(self):
        """
         Writes style.css
        """
        fw = open(self.stylesheet_name, 'w')

        fw.write("h1, h2 {" + os.linesep)
        fw.write("    page-break-after: avoid;" + os.linesep)
        fw.write("    margin-top: 0;" + os.linesep)
        fw.write("    margin-bottom: 1em;" + os.linesep)
        fw.write("}" + os.linesep)
        fw.write("h3, h4, h5, h6 {" + os.linesep)
        fw.write("    page-break-after: avoid;" + os.linesep)
        fw.write("    margin-top: 1em;" + os.linesep)
        fw.write("    margin-bottom: 2em;" + os.linesep)
        fw.write("}" + os.linesep)

        fw.write(".p-style-center {" + os.linesep)
        fw.write("    text-align: center;" + os.linesep)
        fw.write("}" + os.linesep)

        fw.write(".p-style-left {" + os.linesep)
        fw.write("    text-align: left;" + os.linesep)
        fw.write("}" + os.linesep)

        fw.write(".p-style-end {" + os.linesep)
        fw.write("    text-align: right;" + os.linesep)
        fw.write("}" + os.linesep)

        fw.write(".p-style-justify {" + os.linesep)
        fw.write("    text-align: justify;" + os.linesep)
        fw.write("}" + os.linesep)

        fw.write(".p-style-page-break-before { page-break-before: always; }" + os.linesep)

        fw.write(".toc-level-1 {" + os.linesep)
        fw.write("    text-indent: 0;" + os.linesep)
        fw.write("}" + os.linesep)
        fw.write(".toc-level-2 {" + os.linesep)
        fw.write("    text-indent: 2%;" + os.linesep)
        fw.write("}" + os.linesep)
        fw.write(".toc-level-3 {" + os.linesep)
        fw.write("    text-indent: 4%;" + os.linesep)
        fw.write("}" + os.linesep)
        fw.write(".toc-level-4 {" + os.linesep)
        fw.write("    text-indent: 6%;" + os.linesep)
        fw.write("}" + os.linesep)
        fw.write(".toc-level-5 {" + os.linesep)
        fw.write("    text-indent: 8%;" + os.linesep)
        fw.write("}" + os.linesep)
        fw.write(".toc-level-6 {" + os.linesep)
        fw.write("    text-indent: 10%;" + os.linesep)
        fw.write("}" + os.linesep)
        fw.close()

def noparam():
    print "No parameters were given. At least you should tell me which one is the input file"

def usage():
    print "usage: to do, sorry :-)"

def main(argv):
    try:
        for args in sys.argv:
                opts, args = getopt.getopt(argv, "l:i:", ["lang=", "input="])

    except getopt.GetoptError:
        usage()
        sys.exit(2)

    lang = unicode("")
    odt_document = unicode("")

    for opt, arg in opts:
        if opt in ("-l", "--lang"):
            lang = arg

        elif opt in ("-i", "--input"):
            odt_document = arg

        else:
            pass

    if not odt_document:
        noparam()
        sys.exit()

    try:
        print "Processing %s..." % odt_document
        odt = OdtDocument(odt_document)
        if lang:
            odt.language = lang
            print "Document language=%s" % lang
        else:
            print "WARNING: lang not specified; using default EN"
        odt.dumpxml()
        odt.load_metadata()
        odt.xml2html()
        odt.content_opf()
        odt.toc_ncx()
        odt.toc_html()
        odt.style_css()
        print "Done."
    except:
        print "ERROR processing %s. Bad file or file corrupted" % odt_document


if __name__ == "__main__":
    main(sys.argv[1:])


