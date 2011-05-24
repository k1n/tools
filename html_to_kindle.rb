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

html_dict = {}

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

    if /(?<prefix>regex3-CHP-\d+)\.html/ =~ filename and not html_dict.has_key?(filename)
        html_dict[filename] = []
    end

    if /(?<prefix>regex3-CHP-\d+)-SECT-\d+\.html/ =~ filename
        html_dict["#{prefix}.html"].push(filename)
    end

    open('output/' + File.basename(filename), 'w') { |f| f.write(output)}
}

ncx_text = %{<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"
	"http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">

<!--
	For a detailed description of NCX usage please refer to:
	http://www.idpf.org/2007/opf/OPF_2.0_final_spec.html#Section2.4.1
-->

<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="en-US">
<head>
<meta name="dtb:uid" content="BookId"/>
<meta name="dtb:depth" content="2"/>
<meta name="dtb:totalPageCount" content="0"/>
<meta name="dtb:maxPageNumber" content="0"/>
</head>
<docTitle><text>Mastering Regular Expressions 3rd</text></docTitle>
<docAuthor><text>Amazon.com</text></docAuthor>
  <navMap>
    <navPoint class="toc" id="toc" playOrder="1">
      <navLabel>
        <text>Table of Contents</text>
      </navLabel>
      <content src="toc.html"/>
    </navPoint>
}

toc_text = %{<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Table of Contents</title></head>
<body>

<div>
 <h1><b>TABLE OF CONTENTS</b></h1>
 <br />}

play_order_count = 1

html_dict.each_with_index {|(filename, sect_array), index|
    doc = open(filename) { |f| Hpricot(f) }
    title = doc.search("title").inner_html

    play_order_count += 1
    ncx_text += %{
    <navPoint class="chapter" id="chapter_#{index+1}" playOrder="#{play_order_count}">
      <navLabel>
        <text>#{title}</text>
      </navLabel>
      <content src="#{filename}"/>}

    toc_text += %{
 <h3><b>Chapter #{index+1}<br />
 <a href="#{filename}">#{title}</a></b></h3><br />
 <div><ul>}

    sect_array.each_with_index {|sect_filename, inner_index|
        doc = open(sect_filename) { |f| Hpricot(f) }
        sect_title = doc.search("title").inner_html
        play_order_count += 1
        ncx_text += %{
      <navPoint class="section" id="_#{index+1}.#{inner_index+1}" playOrder="#{play_order_count}">
        <navLabel>
          <text>#{sect_title}</text>
        </navLabel>
        <content src="#{sect_filename}"/>
      </navPoint>}

    toc_text += %{
 <li><a href="#{sect_filename}">#{sect_title}</a></li>
    }

    }
    toc_text += %{
 </ul></div><br />}
    ncx_text += %{
    </navPoint>}
}

ncx_text += %{
  </navMap>
</ncx>}
toc_text += %{
 <h1 class="centered">* * *</h1>
</div>
</body>
</html>}

open('output/MRE3.ncx', 'w') { |f| f.write(ncx_text)}
open('output/toc.html', 'w') { |f| f.write(toc_text)}
