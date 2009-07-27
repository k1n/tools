/* vi:set et ai sw=2 sts=2 ts=2: */
/*-
 * Copyright (c) 2009 Jannis Pohlmann <jannis@xfce.org>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor,
 * Boston, MA 02110-1301, USA.
 */

#include <glib.h>
#include <gio/gio.h>
#include <gtk/gtk.h>



static GtkWidget    *execute_button = NULL;
static GtkWidget    *cancel_button = NULL;
static GtkWidget    *label = NULL;
static GCancellable *cancellable = NULL;
static GFile        *file = NULL;
static const gchar  *path = NULL;



typedef void (*GFileCountProgressCallback) (goffset  current_num_files,
                                            goffset  current_num_bytes,
                                            gpointer user_data);
    


typedef struct 
{
  GFile                      *file;
  GFileCountProgressCallback  progress_cb;
  gpointer                    progress_cb_data;
  GIOSchedulerJob            *job;
} DeepCountAsyncData;



static void
deep_count_async_data_free (DeepCountAsyncData *data)
{
  g_object_unref (data->file);
  g_free (data);
}



typedef struct 
{
  DeepCountAsyncData *data;
  goffset             current_num_files;
  goffset             current_num_bytes;
} ProgressData;



static gboolean
g_file_real_deep_count (GFile                     *file,
                        GCancellable              *cancellable,
                        GFileCountProgressCallback progress_callback,
                        gpointer                   progress_callback_data,
                        ProgressData              *progress_data,
                        GError                   **error)
{
  GFileEnumerator *enumerator;
  GFileInfo       *info;
  GFileInfo       *child_info;
  GFile           *child;
  gboolean         success = TRUE;
  
  g_return_val_if_fail (G_IS_FILE (file), FALSE);

  info = g_file_query_info (file, "standard::*", G_FILE_QUERY_INFO_NOFOLLOW_SYMLINKS, cancellable, error);

  if (g_cancellable_is_cancelled (cancellable))
    return FALSE;

  if (info == NULL)
    return FALSE;

  progress_data->current_num_files += 1;
  progress_data->current_num_bytes += g_file_info_get_size (info);

  if (progress_callback != NULL)
    progress_callback (progress_data->current_num_files, progress_data->current_num_bytes, progress_callback_data);

  if (g_file_info_get_file_type (info) == G_FILE_TYPE_DIRECTORY)
    {
      enumerator = g_file_enumerate_children (file, "standard::*", G_FILE_QUERY_INFO_NOFOLLOW_SYMLINKS, cancellable, error);
    
      if (!g_cancellable_is_cancelled (cancellable))
        {
          if (enumerator != NULL)
            {
              while (!g_cancellable_is_cancelled (cancellable) && success)
                {
                  child_info = g_file_enumerator_next_file (enumerator, cancellable, error);

                  if (g_cancellable_is_cancelled (cancellable))
                    break;

                  if (child_info == NULL)
                    {
                      if (*error != NULL)
                        success = FALSE;
                      break;
                    }

                  child = g_file_resolve_relative_path (file, g_file_info_get_name (child_info));
                  success = success && g_file_real_deep_count (child, cancellable, progress_callback, progress_callback_data, progress_data, error);
                  g_object_unref (child);

                  g_object_unref (child_info);
                }

              g_object_unref (enumerator);
            }
        }
    }

  g_object_unref (info);

  return !g_cancellable_is_cancelled (cancellable) && success;
}



static gboolean 
g_file_deep_count (GFile                     *file,
                   GCancellable              *cancellable,
                   GFileCountProgressCallback progress_callback,
                   gpointer                   progress_callback_data,
                   GError                   **error)
{
  ProgressData data = {
    .data = NULL,
    .current_num_files = 0,
    .current_num_bytes = 0,
  };

  g_return_val_if_fail (G_IS_FILE (file), FALSE);

  if (g_cancellable_set_error_if_cancelled (cancellable, error))
    return FALSE;

  return g_file_real_deep_count (file, cancellable, progress_callback, progress_callback_data, &data, error);
}



static gboolean
deep_count_async_progress_in_main (gpointer user_data)
{
  ProgressData       *progress = user_data;
  DeepCountAsyncData *data = progress->data;

  data->progress_cb (progress->current_num_files, progress->current_num_bytes, data->progress_cb_data);

  return FALSE;
}



static void
deep_count_async_progress_callback (goffset  current_num_files,
                                    goffset  current_num_bytes,
                                    gpointer user_data)
{
  DeepCountAsyncData *data = user_data;
  ProgressData       *progress;

  progress = g_new (ProgressData, 1);
  progress->data = data;
  progress->current_num_files = current_num_files;
  progress->current_num_bytes = current_num_bytes;

  g_io_scheduler_job_send_to_mainloop_async (data->job, deep_count_async_progress_in_main, progress, g_free);
}



static gboolean
deep_count_async_thread (GIOSchedulerJob *job,
                         GCancellable    *cancellable,
                         gpointer         user_data)
{
  GSimpleAsyncResult *res;
  DeepCountAsyncData *data;
  gboolean            result;
  GError             *error = NULL;

  res = user_data;
  data = g_simple_async_result_get_op_res_gpointer (res);

  data->job = job;
  result = g_file_deep_count (data->file, cancellable, data->progress_cb != NULL ? deep_count_async_progress_callback : NULL, data, &error);

  if (data->progress_cb != NULL)
    g_io_scheduler_job_send_to_mainloop (job, (GSourceFunc) gtk_false, NULL, NULL);

  if (!result && error != NULL)
    {
      g_simple_async_result_set_from_error (res, error);
      g_error_free (error);
    }

  g_simple_async_result_complete_in_idle (res);

  return FALSE;
}



static void
g_file_deep_count_async (GFile                     *file,
                         int                        io_priority,
                         GCancellable              *cancellable,
                         GFileCountProgressCallback progress_callback,
                         gpointer                   progress_callback_data,
                         GAsyncReadyCallback        callback,
                         gpointer                   callback_data)
{
  GSimpleAsyncResult *result;
  DeepCountAsyncData *data;

  g_return_if_fail (G_IS_FILE (file));

  data = g_new0 (DeepCountAsyncData, 1);
  data->file = g_object_ref (file);
  data->progress_cb = progress_callback;
  data->progress_cb_data = progress_callback_data;

  result = g_simple_async_result_new (G_OBJECT (file), callback, callback_data, g_file_deep_count_async);
  g_simple_async_result_set_op_res_gpointer (result, data, (GDestroyNotify) deep_count_async_data_free);

  g_io_scheduler_push_job (deep_count_async_thread, result, g_object_unref, io_priority, cancellable);
}



static gboolean
g_file_deep_count_finish (GFile        *file,
                          GAsyncResult *res,
                          GError      **error)
{
  g_return_val_if_fail (G_IS_FILE (file), FALSE);
  g_return_val_if_fail (G_IS_ASYNC_RESULT (res), FALSE);

  if (G_IS_SIMPLE_ASYNC_RESULT (res))
    {
      GSimpleAsyncResult *simple_res = G_SIMPLE_ASYNC_RESULT (res);

      if (g_simple_async_result_propagate_error (simple_res, error))
        return FALSE;
    }

  return TRUE;
}



static void
deep_count_progress (goffset  current_num_files,
                     goffset  current_num_bytes,
                     gpointer user_data)
{
  GtkWidget *label = user_data;
  gchar     *str;

  str = g_strdup_printf ("%lld files, %.2f MB", current_num_files, current_num_bytes / 1024.0 / 1024.0);
  gtk_label_set_text (GTK_LABEL (label), str);
  g_free (str);
}



static void
deep_count_finished (GObject      *source_object,
                     GAsyncResult *res,
                     gpointer      user_data)
{
  GError *error = NULL;

  if (g_file_deep_count_finish (G_FILE (source_object), res, &error))
    g_debug ("finished with success");
  else
    {
      if (error != NULL)
        {
          g_debug ("finished with error: %s", error->message);
          g_error_free (error);
        }
      else
        g_debug ("finished with errors");
    }

  gtk_widget_hide (cancel_button);
  gtk_widget_show (execute_button);
}



static void
execute_button_clicked (GtkButton *button,
                        GtkWidget *label)
{
  gtk_widget_hide (execute_button);
  gtk_widget_show (cancel_button);
  
  g_cancellable_reset (cancellable);
  
  file = g_file_new_for_path (path != NULL ? path : g_getenv ("HOME"));
  g_file_deep_count_async (file, 0, cancellable, deep_count_progress, label, deep_count_finished, NULL);
  g_object_unref (file);
}



static void
cancel_button_clicked (GtkButton *button,
                       GtkWidget *label)
{
  g_cancellable_cancel (cancellable);

  gtk_widget_hide (cancel_button);
  gtk_widget_show (execute_button);
}



int
main (int    argc,
      char **argv)
{
  GtkWidget *window;
  GtkWidget *box;

  if (!g_thread_supported ())
    g_thread_init (NULL);

  gtk_init (&argc, &argv);

  if (argc > 1)
    path = argv[1];

  cancellable = g_cancellable_new ();

  window = gtk_window_new (GTK_WINDOW_TOPLEVEL);
  gtk_window_set_position (GTK_WINDOW (window), GTK_WIN_POS_CENTER);
  gtk_window_set_default_size (GTK_WINDOW (window), 500, 50);
  gtk_container_set_border_width (GTK_CONTAINER (window), 8);
  g_signal_connect (window, "delete-event", G_CALLBACK (gtk_main_quit), NULL);
  gtk_widget_show (window);

  box = gtk_hbox_new (FALSE, 12);
  gtk_container_add (GTK_CONTAINER (window), box);
  gtk_widget_show (box);

  label = gtk_label_new (NULL);
  gtk_container_add (GTK_CONTAINER (box), label);
  gtk_widget_show (label);

  execute_button = gtk_button_new_from_stock (GTK_STOCK_EXECUTE);
  gtk_box_pack_start (GTK_BOX (box), execute_button, FALSE, TRUE, 0);
  g_signal_connect (execute_button, "clicked", G_CALLBACK (execute_button_clicked), label);
  gtk_widget_show (execute_button);

  cancel_button = gtk_button_new_from_stock (GTK_STOCK_CANCEL);
  gtk_box_pack_start (GTK_BOX (box), cancel_button, FALSE, TRUE, 0);
  g_signal_connect (cancel_button, "clicked", G_CALLBACK (cancel_button_clicked), label);
  gtk_widget_hide (cancel_button);

  gtk_main ();

  g_object_unref (cancellable);

  return 0;
}
