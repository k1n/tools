CLUTTER_FLAGS=`pkg-config --libs --cflags clutter-1.0`

default:
	gcc hello-clutter.c -o hello-clutter $(CLUTTER_FLAGS)
	gcc depth.c -o depth $(CLUTTER_FLAGS)
