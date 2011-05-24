#!/usr/bin/env ruby

require 'hpricot'

htmls = Dir.glob("*.html")
htmls = htmls.sort { |x,y|
    if /(?<prefix>regex3-CHP-(?<x_chap>\d+))/ =~ x and /regex3-CHP-(?<y_chap>\d+)/ =~ y and not y.include?(prefix)
        puts "compare with #{x} and #{y} for chap"
        Integer(x_chap) <=> Integer(y_chap)
    elsif /(?<prefix>regex3-CHP-\d+-SECT)-(?<x_sect>\d+)\.html/ =~ x and y.include?(prefix + '-')
        puts "compare with #{x} and #{y} for sect"
        /(?<prefix>regex3-CHP-\d+-SECT)-(?<y_sect>\d+)\.html/ =~ y
        Integer(x_sect) <=> Integer(y_sect)
    elsif /(?<prefix>regex3-CHP-\d+)\.html/ =~ x and y.include?(prefix + '-SECT')
        puts "compare with #{x} and #{y}"
        -1
    elsif /(?<prefix>regex3-CHP-\d+)\.html/ =~ y and x.include?(prefix + '-SECT')
        puts "compare with #{y} and #{x}"
        1
    else
        x <=> y
    end
}

htmls.each { |filename|
    puts "Start to parser #{filename}"
    doc = open(filename) { |f| Hpricot(f) }
    contents = doc.search("td")[2].inner_html
    title = doc.search("title").inner_html
    output = %{<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <META http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
    <head>
    <title>#{title}</title>
    </head>
    <body>
    #{contents}
    </body>
    </html>}

    open('output/' + File.basename(filename), 'w') { |f| f.write(output)}
}
