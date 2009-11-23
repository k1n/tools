#!/bin/bash

CHROOT_PATH=$PWD/edit


function prepare_network {
	echo "Pareparing the network"
	sudo cp /etc/resolv.conf $CHROOT_PATH/etc/
	sudo cp /etc/hosts $CHROOT_PATH/etc/
}

function mount_chroot {
	echo "Mounting chroot environment."
	sudo mount -t devpts none $CHROOT_PATH/dev/pts
	sudo mount -t proc none $CHROOT_PATH/proc
}

function umount_and_clean {
	echo "Unmounting and cleaning chroot environment."
	sudo rm $CHROOT_PATH/etc/resolv.conf
	sudo rm -rf $CHROOT_PATH/tmp/*
	sudo rm -rf $CHROOT_PATH/root/.bash_history
	sudo rm -f $CHROOT_PATH/var/cache/apt/archives/*.deb

	mount | grep "on $CHROOT_PATH" | awk '{print $3}' \
		| xargs -r -L1 sudo umount
}

prepare_network

mount_chroot

sudo chroot $CHROOT_PATH /bin/bash -c 'su -'

trap umount_and_clean EXIT
