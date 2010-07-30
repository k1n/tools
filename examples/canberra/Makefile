GLIB_FLAGS=`pkg-config --cflags --libs glib-2.0`
GTK_FLAGS=`pkg-config --cflags --libs gtk+-2.0`
GIO_FLAGS=`pkg-config --cflags --libs gio-2.0`
GTHREAD_FLAGS=`pkg-config --cflags --libs gthread-2.0`
CANBERRA=`pkg-config --cflags --libs libcanberra-gtk`

default: 
	gcc -o canberra canberra.c \
		$(GLIB_FLAGS) \
		$(GIO_FLAGS) \
		$(GTK_FLAGS) \
		$(GTHREAD_FLAGS) \
		$(CANBERRA)

test: default
	./canberra
