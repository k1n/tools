set theImages to choose file with prompt "Please select an image file:" with multiple selections allowed
repeat with image in theImages
	tell application "Adobe Photoshop CS4"
		activate
		open image
		
		set docHeight to height of current document
		set docWidth to width of current document
		set display dialogs to never
		set thisdoc to current document
		tell thisdoc
			if docWidth * 3 / 4 > docHeight then
				set docHeight to docWidth * 3 / 4
				resize canvas height docHeight anchor position middle center
			else
				set docWidth to docHeight * 4 / 3
				resize canvas width docWidth anchor position middle center
			end if
		end tell
		save current document
		close current document
	end tell
end repeat