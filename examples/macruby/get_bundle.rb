#!/usr/local/bin/macruby

framework "Cocoa"

if ARGV.length < 1
    puts "Please input the application path."
    exit 1
end

bundle = NSBundle.bundleWithPath(ARGV[0])

puts bundle.bundleIdentifier
