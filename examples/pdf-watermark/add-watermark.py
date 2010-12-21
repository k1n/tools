#!/usr/bin/python

from pyPdf import PdfFileWriter, PdfFileReader

output = PdfFileWriter()
input1 = PdfFileReader(file("main.pdf", "rb"))

# print the title of document1.pdf
print "title = %s" % (input1.getDocumentInfo().title)

# add page 1 from input1 to output document, unchanged
watermark = PdfFileReader(file("watermark.pdf", "rb"))
#print input1.getPage(1).mergePage(watermark.getPage(0))
watermark.getPage(0).mergePage(input1.getPage(0))
#output.addPage(input1.getPage(1))
output.addPage(watermark.getPage(0))

# print how many pages input1 has:
print "document1.pdf has %s pages." % input1.getNumPages()

# finally, write "output" to document-output.pdf
outputStream = file("document-output.pdf", "wb")
output.write(outputStream)
outputStream.close()
