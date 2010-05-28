#!/usr/bin/gjs

const Mx = imports.gi.Mx;
const Clutter = imports.gi.Clutter;

Clutter.init(0, null);

let stage = new Clutter.Stage();

stage.set_size(640, 480);

let expander = new Mx.Expander();
stage.add_actor(expander);
expander.set_position(10, 10);

let scroll = new Mx.ScrollView();
expander.add_actor(scroll);
scroll.set_size(320, 240);

let grid = new Mx.Grid();
scroll.add_actor(grid);

for (let i = 1; i <= 50; i++)
{
	grid.add_actor( new Mx.Button({label: "Button "+i}));
}

stage.show()

Clutter.main();
