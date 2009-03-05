#!/usr/bin/env python

import math
import cairo
import pango
import pangocairo

def str_to_rgba(str):
    '''
    Convert a color string to a rgba tuple.
    '''

    # Strip optional leading # character
    if str.startswith('#'):
        str = str[1:]

    # Handle shorthand notation, e.g. #f00
    if len(str) == 3:
        str = str[0] + str[0] + str[1] + str[1] + str[2] + str[2]

    # Handle shorthand notation with alpha, e.g. #f00c
    if len(str) == 4:
        str = str[0] + str[0] + str[1] + str[1] + str[2] + str[2] + str[3] + str[3]

    # Add alpha value if none was specified
    if len(str) == 6:
        str = str + 'ff'

    # From here on we should really have 8 characters to work with
    if len(str) != 8:
        raise ValueError()

    value = int(str, 16)

    red =   (float((value >> 24) % 256) + 1) / 256
    green = (float((value >> 16) % 256) + 1) / 256
    blue =  (float((value >>  8) % 256) + 1) / 256
    alpha = (float((value      ) % 256) + 1) / 256

    return red, green, blue, alpha

def str_to_margins(str):
    '''
    Convert a margin string into a 4-number tuple.
    The conversion is based on the margin specification from CSS.
    '''

    assert isinstance(str, basestring)

    mt = mr = mb = ml = 1

    tokens = str.split()

    if len(tokens) == 1:
        mt = mr = mb = ml = int(tokens[0])
    elif len(tokens) == 2:
        mt = mb = int(tokens[0])
        mr = ml = int(tokens[1])
    elif len(tokens) == 3:
        mt = int(tokens[0])
        mr = ml = int(tokens[1])
        mb = int(tokens[2])
    elif len(tokens) == 4:
        mt = int(tokens[0])
        mr = int(tokens[1])
        mb = int(tokens[2])
        ml = int(tokens[3])
    else:
        raise ValueError()

    return mt, mr, mb, ml


def render_text_to_image(font, size, text, outfile, margins, fgcolor, bgcolor, pango_markup=False):
    '''
    Render a single-line string to an image, based on the specified options.
    '''

    # Sanity checks

    assert isinstance(font, basestring)
    assert isinstance(size, int)
    assert isinstance(text, basestring)
    assert len(margins) == 4
    assert len(fgcolor) == 4
    assert len(bgcolor) == 4
    assert isinstance(pango_markup, bool)

    margin_top, margin_right, margin_bottom, margin_left = margins

    # Create a 1x1 surface to use for the text extents calculations. The real
    # surface will be created at the right size afterwards.
    
    mini_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1, 1)
    mini_ctx = pangocairo.CairoContext(cairo.Context(mini_surface))
    layout = mini_ctx.create_layout()
    fd = pango.FontDescription(font)
    fd.set_size(size * pango.SCALE)
    layout.set_font_description(fd)
    if pango_markup:
        layout.set_markup(text)
    else:
        layout.set_text(text)
    text_width, text_height = layout.get_pixel_extents()[1][2:]

    # Create the real surface which will be used for text rendering

    image_width = text_width + margin_left + margin_right
    image_height = text_height + margin_top + margin_bottom
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, image_width, image_height)
    ctx = pangocairo.CairoContext(cairo.Context(surface))

    # Fill the background

    ctx.set_source_rgba(*bgcolor)
    ctx.move_to(0, 0)
    ctx.rectangle(0, 0, image_width, image_height)
    ctx.fill()

    # Draw the text in the specified color, font face and size

    ctx.set_source_rgba(*fgcolor)
    ctx.move_to(margin_left, margin_top)
    ctx.show_layout(layout)

    # Save output

    surface.write_to_png(outfile)



# Script execution starts here

if __name__ == '__main__':

    # Setup the option parser

    from optparse import OptionParser
    parser = OptionParser(usage='%prog --font=FONT --size=SIZE --text=TEXT --output=OUTFILE', version='%prog 0.1')
    parser.add_option('-f', '--font', dest='font',
                      help='The font family to use. Pango descriptions such as "Sans Bold" work.', metavar='FONT')
    parser.add_option('-s', '--size', type='int', dest='size', 
                      help='The font size to use (in pixels).', metavar='SIZE')
    parser.add_option('-t', '--text', dest='text',
                      help='The text string to render. Use \\n for line breaks.', metavar='TEXT')
    parser.add_option('-p', '--pango-markup', dest='pango_markup', action='store_true', default=False,
                      help='If passed, Pango markup tags are recognized in the provided text')
    parser.add_option('-o', '--output', dest='outfile',
                      help='The filename to save the resulting PNG image to.', metavar='FILE')
    parser.add_option('-m', '--margin', dest='margin',
                      help='Margins in CSS-like syntax (top, right, bottom, left). Defaults to 1.',
                      metavar='MARGINSPEC')
    parser.add_option('-c', '--text-color', dest='fgcolor',
                      help='Text color, e.g. #ff00ac33.', metavar='COLOR')
    parser.add_option('-b', '--background-color', dest='bgcolor',
                      help='Background color to use, e.g. #333.', metavar='COLOR')


    # Parse command-line parameters

    (options, args) = parser.parse_args()

    if (args): parser.error('No positional arguments allowed')

    if options.text:
        text = options.text.replace(r'\n', '\n')
    else:
        parser.error('No text specified')

    if not options.font: parser.error('No font family specified')
    if not options.size: parser.error('No font size specified')
    if not options.outfile: parser.error('No output file specified')

    margins = 1, 1, 1, 1
    if options.margin:
        try:
            margins = str_to_margins(options.margin)
        except (IndexError, ValueError):
            parser.error('Illegal margin specification.\nYou can specify up to 4 integer values, just like CSS.')

    # Colors

    fgcolor = 0, 0, 0, 0.8
    bgcolor = 0, 0, 0, 0
    if options.fgcolor:
        try: fgcolor = str_to_rgba(options.fgcolor)
        except (ValueError): parser.error('Invalid foreground color')
    if options.bgcolor:
        try: bgcolor = str_to_rgba(options.bgcolor)
        except (ValueError): parser.error('Invalid background color')

    # Go!

    render_text_to_image(options.font, options.size, text, options.outfile, margins, fgcolor, bgcolor, options.pango_markup)
