#!/usr/local/bin/macruby

framework "ScriptingBridge"

chrome = SBApplication.applicationWithBundleIdentifier("com.google.Chrome")
chrome.windows[0].tabs.each {|tab| puts tab.title}  
