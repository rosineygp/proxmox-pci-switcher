#!/bin/bash

set -e

# shellcheck disable=SC2034
VMID="$1"
PHASE="$2"

_VM_NAME_PREFIX=""
_VM_NAME_SUFFIX="desktop"

_RESET_GPU_FRAMEBUFFER="true"

_reset_gpu_framebuffer () {
	echo 0 >/sys/class/vtconsole/vtcon0/bind
	echo 0 >/sys/class/vtconsole/vtcon1/bind
	echo efi-framebuffer.0 >/sys/bus/platform/drivers/efi-framebuffer/unbind
}

# main
if [[ "$PHASE" == "pre-start" ]]; then

	for i in $(qm list --full | grep -E "${_VM_NAME_PREFIX}.*${_VM_NAME_SUFFIX}.*running" | awk '{ print $1 }'); do
		qm shutdown "$i"
	done

	for i in $(seq 300); do
		if [ "$(qm list --full | grep -cE "${_VM_NAME_PREFIX}.*${_VM_NAME_SUFFIX}.*running")" == "0" ]; then
			break
		fi
		sleep 1
	done

	if [ "$_RESET_GPU_FRAMEBUFFER" == "true" ]; then
		_reset_gpu_framebuffer
	fi

	sleep 1

fi
