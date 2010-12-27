#!/usr/bin/python
# This is pdf watermark, use pdftk to composite
# E.G.
# pdftk main.pdf background test.pdf output out.pdf

from reportlab.pdfgen import canvas
import reportlab.lib.pagesizes as ps

p = canvas.Canvas('test.pdf')
p.setFont("Times-Roman", 60)
p.setStrokeColorRGB(0.74, 0.74, 0.74)
p.setFillColorRGB(0.74, 0.74, 0.74)
p.translate(ps.A4[0]/2, ps.A4[1]/2)
p.rotate(45)
p.drawCentredString(80, 0, "Confidential")
p.drawCentredString(80, 60, "Hannah Hu")
p.drawCentredString(80, 120, "2010/12/21")
p.drawCentredString(80, 180, "Hello!")
p.save()
