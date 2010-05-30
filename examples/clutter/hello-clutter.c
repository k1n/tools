/* hello-clutter.c
 *
 * Copyright (C) 2009  Intel Corp.
 *
 * Author: Emmanuele Bassi <ebassi@linux.intel.com>
 *
 * Compile with:
 * 
 *   gcc -Wall \
 *      `pkg-config --cflags clutter-1.0` -o hello-clutter \
 *      hello-clutter.c \
 *      `pkg-config --libs clutter-1.0`
 */

#include <stdlib.h>
#include <math.h>

#include <glib.h>

#include <clutter/clutter.h>
#include <clutter/clutter-keysyms.h>

#define FONT_DESC       "Sans 96px"
#define PATH_DESC       "M %d,%d L %d,%d L %d,%d L %d,%d"

static gboolean
on_button_press (ClutterActor *stage,
                 ClutterEvent *event)
{
  clutter_actor_destroy (stage);  

  return TRUE;
}

static gboolean
on_key_press (ClutterActor *stage,
              ClutterEvent *event)
{
  /* quit the main loop if the key pressed is 'Esc' */
  if (clutter_event_get_key_symbol (event) == CLUTTER_Escape)
    clutter_actor_destroy (stage);

  return TRUE;
}

static gdouble
sine_wave (ClutterAlpha *alpha,
           gpointer      unused)
{
  ClutterTimeline *timeline = clutter_alpha_get_timeline (alpha);
  gdouble progress = clutter_timeline_get_progress (timeline);

  return sin(progress * G_PI);
}

int
main (int argc, char *argv[])
{
  ClutterActor *stage;
  ClutterColor stage_color = { 255, };
  ClutterTimeline *timeline;
  ClutterAlpha *alpha;
  gchar *hello_str, *chr;
  gdouble x_offset, y_offset;
  gint idx;

  /* initialize Clutter */
  clutter_init (&argc, &argv);

  if (argc > 1)
    hello_str = g_strdup (argv[1]);
  else
    hello_str = g_strdup ("Hello, Clutter!");

  /* create a Stage */
  stage = clutter_stage_new ();

  /* set the title of the Stage window */
  clutter_stage_set_title (CLUTTER_STAGE (stage), "Hello, Clutter");

  /* set the background color of the Stage */
  clutter_color_from_string (&stage_color, "DarkSlateGray");
  clutter_stage_set_color (CLUTTER_STAGE (stage), &stage_color);

  /* connect the pointer button press and key press event signals */
  g_signal_connect (stage, "button-press-event", G_CALLBACK (on_button_press), NULL);
  g_signal_connect (stage, "key-press-event", G_CALLBACK (on_key_press), NULL);
  g_signal_connect (stage, "destroy", G_CALLBACK (clutter_main_quit), NULL);

  /* set the size of the Stage */
  clutter_actor_set_size (stage, 800, 600);

  /* then show the Stage */
  clutter_actor_show (stage);

  /* create a Timeline and an Alpha to drive the animation */

  /* the Timeline is 3 seconds long, and will loop */
  timeline = clutter_timeline_new (3000);
  clutter_timeline_set_loop (timeline, TRUE);

  /* the Alpha uses the Timeline with a custom sine wave function */
  alpha = clutter_alpha_new ();
  clutter_alpha_set_timeline (alpha, timeline);
  clutter_alpha_set_func (alpha, sine_wave, NULL, NULL);
  g_object_unref (timeline);

  x_offset = 64.0;
  y_offset = clutter_actor_get_height (stage) / 2.0;

  for (chr = hello_str, idx = 0; *chr != '\0'; chr++, idx++)
    {
      ClutterColor *color;
      ClutterActor *text;
      ClutterBehaviour *behaviour;
      gchar str[2] = { *chr, '\0' };

      /* create a new random Color */
      color = clutter_color_new (g_random_int_range (0, 255),
                                 g_random_int_range (0, 255),
                                 g_random_int_range (0, 255),
                                 255);

      /* create a new Text Actor to display a single character */
      text = clutter_text_new_full (FONT_DESC, str, color);
      clutter_actor_set_position (text, x_offset, y_offset);

      /* add the Actor to the Stage */
      clutter_container_add_actor (CLUTTER_CONTAINER (stage), text);

      /* select the Behaviour depending on the position in the string;
       * the Behaviour is used to create an animation
       */
      if (idx % 7 == 0)
        {
          /* animate the Actor's opacity */
          behaviour = clutter_behaviour_opacity_new (alpha, 255, g_random_int_range (0, 64));
        }
      else if (idx % 3 == 0)
        {
          /* rotate the Actor around the Z axis */
          behaviour = clutter_behaviour_rotate_new (alpha, CLUTTER_Z_AXIS,
                                                    (idx % 2) ? CLUTTER_ROTATE_CW
                                                              : CLUTTER_ROTATE_CCW,
                                                    0.0, 0.0);
          clutter_behaviour_rotate_set_center (CLUTTER_BEHAVIOUR_ROTATE (behaviour),
                                               clutter_actor_get_width (text) / 2,
                                               clutter_actor_get_height (text) / 2,
                                               0);
        }
      else if (idx % 2 == 0)
        {
          gdouble final = (idx % 5) ? 1.0 + g_random_double ()
                                    : g_random_double_range (0.0, 0.8);

          /* scale the Actor around its center */
          behaviour = clutter_behaviour_scale_new (alpha, 1.0, 1.0, final, final);
          clutter_actor_move_anchor_point_from_gravity (text, CLUTTER_GRAVITY_CENTER);
        }
      else
        {
          gdouble x, y;
          ClutterPath *path;
          gchar *description;

          x = g_random_int_range (0, 50);
          y = g_random_int_range (0, 50);

          description = g_strdup_printf (PATH_DESC,
                                         (int) x_offset, (int) y_offset,
                                         (int) (x_offset + x), (int) (y_offset - y),
                                         (int) (x_offset + x), (int) (y_offset + y),
                                         (int) (x_offset - x), (int) (y_offset + y));

          path = clutter_path_new_with_description (description);

          /* move the Actor on a Path described using a SVG-like syntax */
          behaviour = clutter_behaviour_path_new (alpha, path);

          g_free (description);
        }

      /* apply the Behaviour to the Actor */
      clutter_behaviour_apply (behaviour, text);

      /* make the Behaviour go away when the Actor is destroyed */
      g_object_set_data_full (G_OBJECT (text),
                              "behaviour", behaviour,
                              (GDestroyNotify) g_object_unref);

      x_offset += clutter_actor_get_width (text) - 5;

      clutter_color_free (color);
    }

  /* start the animation */
  clutter_timeline_start (timeline);

  /* finally, start the main loop */
  clutter_main ();

  /* clean up */
  g_free (hello_str);

  return EXIT_SUCCESS;
}
