#!/bin/bash

VMID="$1"
PHASE="$2"

_POOL_NAME="desktop"
_SHUTDOWN_TIMEOUT="300"
_RESET_GPU_FRAMEBUFFER="true"

_reset_gpu_framebuffer() {
	[[ -f "/sys/class/vtconsole/vtcon0/bind" ]] && echo 0 >/sys/class/vtconsole/vtcon0/bind
	[[ -f "/sys/class/vtconsole/vtcon1/bind" ]] && echo 0 >/sys/class/vtconsole/vtcon1/bind
	[[ -f "/sys/bus/platform/drivers/efi-framebuffer/unbind" ]] && echo efi-framebuffer.0 >/sys/bus/platform/drivers/efi-framebuffer/unbind
}

if [ "$(qm list | grep "$VMID" | awk '{ print $3 }')" == "running" ]; then
	exit 0
fi

# main
if [[ "$PHASE" == "pre-start" ]]; then

	for i in $(pvesh get /pools/${_POOL_NAME}/ --output-format yaml | grep -E '(vmid|status)' | paste - - | grep running | awk '{ print $4 }'); do
		if [ "$i" != "$VMID" ]; then
			qm shutdown "$i"
		fi
	done

	for i in $(seq "$_SHUTDOWN_TIMEOUT"); do
		if [ "$(pvesh get /pools/${_POOL_NAME}/ --output-format yaml | grep -E '(vmid|status)' | paste - - | grep -cv stopped)" == "0" ]; then
			break
		fi
		sleep 1
	done

	if [ "$_RESET_GPU_FRAMEBUFFER" == "true" ]; then
		_reset_gpu_framebuffer
	fi

	sleep 1

fi
