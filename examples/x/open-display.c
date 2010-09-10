#include <stdio.h>
#include <stdlib.h>
#include <X11/Xlib.h>

int main (int argc, char *argv[])
{
	Display *display;
	display = XOpenDisplay(":0");
	if (display == NULL) {
		fprintf(stderr, "Cannot connect to X Server %s\n", ":0");
		exit(-1);
	} else {
		fprintf(stdout, "Connect successfully to X Server %s\n", ":0");
	}

	/* this variable will be used to store the "default" screen of the  */
	/* X server. usually an X server has only one screen, so we're only */
	/* interested in that screen.                                       */
	int screen_num;

	/* these variables will store the size of the screen, in pixels.    */
	int screen_width;
	int screen_height;

	/* this variable will be used to store the ID of the root window of our */
	/* screen. Each screen always has a root window that covers the whole   */
	/* screen, and always exists.                                           */
	Window root_window;

	/* these variables will be used to store the IDs of the black and white */
	/* colors of the given screen. More on this will be explained later.    */
	unsigned long white_pixel;
	unsigned long black_pixel;

	/* check the number of the default screen for our X server. */
	screen_num = DefaultScreen(display);

	/* find the width of the default screen of our X server, in pixels. */
	screen_width = DisplayWidth(display, screen_num);

	/* find the height of the default screen of our X server, in pixels. */
	screen_height = DisplayHeight(display, screen_num);

	/* find the ID of the root window of the screen. */
	root_window = RootWindow(display, screen_num);

	/* find the value of a white pixel on this screen. */
	white_pixel = WhitePixel(display, screen_num);

	/* find the value of a black pixel on this screen. */
	black_pixel = BlackPixel(display, screen_num);

	fprintf(stdout, "The screen_num is %d\nthe screen_width is %d\nthe screen_height is %d\n", screen_num, screen_width, screen_height);

	return 0;
}

