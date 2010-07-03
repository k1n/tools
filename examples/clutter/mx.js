#!/usr/bin/gjs

const Mx = imports.gi.Mx;
const Clutter = imports.gi.Clutter;

Clutter.init(0, null);

let stage = new Clutter.Stage({title: "Ubuntu Tweak"});

stage.set_size(640, 480);

let pathbar = new Mx.PathBar();
pathbar.set_position(20, 20);
pathbar.push("/");
pathbar.push("home");
pathbar.push("tualatrix");
stage.add_actor(pathbar);

let expander = new Mx.Expander();
stage.add_actor(expander);
expander.set_position(260, 100);

let scroll = new Mx.ScrollView();
expander.add_actor(scroll);
scroll.set_size(320, 240);

let grid = new Mx.Grid();
scroll.add_actor(grid);

for (let i = 1; i <= 50; i++)
{
	grid.add_actor( new Mx.Button({label: "Button "+i,
				       tooltip_text: "Hello World, I'm TualatriX!"}));
}

let sider = new Mx.Slider();
grid.add_actor(sider);

expander.rotation_angle_y = -45;

stage.show()

Clutter.main();
