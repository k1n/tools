#include <gtk/gtk.h>
#include <canberra-gtk.h>

static void play_button_clicked(GtkWidget *widget, gpointer data)
{
	ca_gtk_play_for_widget (widget, 0,
			    CA_PROP_EVENT_ID, "camera-shutter",
			    CA_PROP_MEDIA_ROLE, "event",
			    CA_PROP_EVENT_DESCRIPTION, "Shutter sound",
			    NULL);
}

int main(int argc, char **argv)
{
	gtk_init(&argc, &argv);

	GtkWidget *window, *button;

	window = gtk_window_new(GTK_WINDOW_TOPLEVEL);

	button = gtk_button_new_with_label ("Play");
	g_signal_connect(button, "clicked", G_CALLBACK (play_button_clicked), NULL);
	gtk_container_add (GTK_CONTAINER(window), button);

	gtk_widget_show_all(window);
	gtk_main();

	return 0;
}
