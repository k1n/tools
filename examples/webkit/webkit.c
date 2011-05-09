#include <gtk/gtk.h>
#include <webkit/webkit.h>

enum
{
  TARGET_STRING,
  TARGET_TEXT,
};

static void
on_destroy (GtkWidget* widget, gpointer data)
{
      gtk_main_quit ();
}

int
main (int argc, char* argv[])
{
    gtk_init (&argc, &argv);

    GtkWidget *window, *web_view;

    GtkTargetEntry *targets;
    GtkTargetList *target_list;
    int n_targets;
    const GtkTargetEntry target_table[] = {
      { "STRING", GTK_TARGET_SAME_APP, TARGET_STRING},
      { "text/plain", 0, TARGET_TEXT},
    };

    target_list = gtk_target_list_new (NULL, 0);
    gtk_target_list_add_uri_targets (target_list, 0);
    gtk_target_list_add_text_targets (target_list, 0);
    gtk_target_list_add_table (target_list, target_table, G_N_ELEMENTS (target_table));

    targets = gtk_target_table_new_from_list (target_list, &n_targets);


    window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_default_size (GTK_WINDOW (window), 800, 600);
    gtk_widget_set_name (window, "GtkLauncher");
    g_signal_connect (G_OBJECT (window), "destroy", G_CALLBACK (on_destroy), NULL);

    web_view = webkit_web_view_new();
    gtk_drag_dest_set(web_view,
                      GTK_DEST_DEFAULT_MOTION | GTK_DEST_DEFAULT_HIGHLIGHT | GTK_DEST_DEFAULT_DROP,
                      targets, n_targets,
                      GDK_ACTION_COPY | GDK_ACTION_MOVE);
    gtk_target_table_free (targets, n_targets);
    gtk_target_list_unref (target_list);


    gtk_container_add(GTK_CONTAINER(window), web_view);

    gchar* uri = (gchar*) (argc > 1 ? argv[1] : "http://www.google.com/");
    webkit_web_view_open (web_view, uri);

    gtk_widget_show_all (window);
    gtk_main ();

    return 0;
}
