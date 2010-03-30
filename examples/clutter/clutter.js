#!/usr/bin/gjs
/* -*- mode: js2; js2-basic-offset: 4; indent-tabs-mode: nil -*- */

const Clutter = imports.gi.Clutter;

Clutter.init(0, null);

let stage = new Clutter.Stage({color: new Clutter.Color({red: 123,
			                                 blue: 123,
							 green: 123,
							 alpha: 100
							 }),
				use_alpha: true,
				user_resizable: true});

let texture = new Clutter.Texture({ filename: 'test.jpg',
                                    reactive: true });

texture.connect('button-press-event',
                function(o, event) {
                    log('Clicked!');
                    return true;
                });

stage.add_actor(texture);
stage.show();

Clutter.main();
