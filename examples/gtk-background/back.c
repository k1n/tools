#include <gtk/gtk.h>

static void
on_destroy (GtkWidget * widget, gpointer data)
{
  gtk_main_quit ();
}

int
main (int argc, char *argv[])
{
  GtkWidget *window;
  GtkWidget *button;
  GtkRcStyle *style;

  gtk_init (&argc, &argv);

  window = gtk_window_new (GTK_WINDOW_TOPLEVEL);
  g_signal_connect(G_OBJECT(window), "destroy", G_CALLBACK (on_destroy), NULL);

  gtk_container_set_border_width(GTK_CONTAINER(window), 100);
  gtk_window_set_default_size(GTK_WINDOW(window), 320, 240);

  style = gtk_widget_get_modifier_style (window);
  style->bg_pixmap_name[GTK_STATE_NORMAL] = g_strdup("/usr/share/pixmaps/ubuntu-tweak.png");
  gtk_widget_modify_style (window, style);

  button = gtk_button_new();
  gtk_button_set_label(GTK_BUTTON(button), "Hello");
  gtk_container_add(GTK_CONTAINER(window), button);

  gtk_widget_show_all (window);
  gtk_main ();

  return 0;
}
