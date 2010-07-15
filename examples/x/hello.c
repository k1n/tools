#include <stdio.h>
#include <stdlib.h>
#include <X11/Xlib.h>

#define WINDOW_SIZE 200

int main (int argc, char *argv[])
{
	Display *dpy;
	XSetWindowAttributes attributes;
	Window win;
	GC gc;
	XKeyEvent event;
	int i;

	dpy = XOpenDisplay(NULL);

	attributes.background_pixel = XWhitePixel(dpy, 0);
	win = XCreateWindow(dpy, XRootWindow(dpy, 0),
			0, 0, WINDOW_SIZE, WINDOW_SIZE, 0, DefaultDepth(dpy, 0), InputOutput,
			DefaultVisual(dpy, 0), CWBackPixel, &attributes);

	XSelectInput(dpy, win, ExposureMask | KeyPressMask);

	gc = XCreateGC(dpy, win, 0, NULL);

	XMapWindow(dpy, win);
	while(1)
	{
		XNextEvent(dpy, (XEvent *)&event);
		switch(event.type)
		{
			case Expose:
				{
					for (i=0;i<WINDOW_SIZE/2;i++)
						XDrawPoint(dpy, win, gc, WINDOW_SIZE/4+i, WINDOW_SIZE/2);
				}break;
			case KeyPress:
				{
					XFreeGC(dpy, gc);
					XCloseDisplay(dpy);
					exit(0);
				}break;
			default:
				{}
				break;
		}
	}
	return 0;
}

