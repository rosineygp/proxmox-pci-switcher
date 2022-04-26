#!/bin/bash

VMID="$1"
PHASE="$2"

_PVE_CONFIG_FILE="/etc/pve/qemu-server/${VMID}.vars"

_PIN_CPU_IDS="${PIN_CPU_IDS:-false}"
_RENICE_PRIORITY="${RENICE_PRIORITY:-false}"
_SHUTDOWN_TIMEOUT="${SHUTDOWN_TIMEOUT:-300}"
_RESET_GPU_FRAMEBUFFER="${RESET_GPU_FRAMEBUFFER:-true}"

if test -f "$_PVE_CONFIG_FILE"; then
	# shellcheck disable=SC1090
	source "$_PVE_CONFIG_FILE"
fi

_get_pool_by_vmid() {
	for i in $(pvesh get /pools/ --output-format yaml | awk '{ print $3 }'); do
		for j in $(pvesh get /pools/"$i" --output-format yaml | grep vmid | awk '{ print $2 }'); do
			if [ "$j" == "$VMID" ]; then
				echo "$i"
				return
			fi
		done
	done
	echo "resource poll, not found!"
}

_reset_gpu_framebuffer() {
	echo "_reset_gpu_framebuffer"
	[[ -f "/sys/class/vtconsole/vtcon0/bind" ]] && echo 0 >/sys/class/vtconsole/vtcon0/bind
	[[ -f "/sys/class/vtconsole/vtcon1/bind" ]] && echo 0 >/sys/class/vtconsole/vtcon1/bind
	[[ -f "/sys/bus/platform/drivers/efi-framebuffer/unbind" ]] && echo efi-framebuffer.0 >/sys/bus/platform/drivers/efi-framebuffer/unbind
}

_pin_cpu(){
	echo "_pin_cpu"
	if  [[ -x $(command -v taskset) ]]; then
		taskset --cpu-list --all-tasks --pid $_PIN_CPU_IDS  $_VM_PID
	else
		echo "command taskset not found, skipping..."
	fi
}

_renice() {
	echo "_renice"
	if  [[ -x $(command -v renice) ]]; then
		renice $_RENICE_PRIORITY $_VM_PID
	else
		echo "command renice not found, skipping..."
	fi	
}

if [ "$(qm list | grep "$VMID" | awk '{ print $3 }')" == "running" ] &&
   [ "$PHASE" != "post-start" ] ; then
	exit 0
fi

_POOL_NAME="$(_get_pool_by_vmid)"

if [ "$_POOL_NAME" == "resource poll, not found!" ]; then
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

if  [[ "$PHASE" == "post-start" ]]; then

	_VM_PID="$(< /run/qemu-server/$VMID.pid)"

	if [[ "$_PIN_CPU_IDS" != "false" ]]; then
		_pin_cpu
	fi

	if [[ "$_RENICE_PRIORITY" != "false" ]]; then
		_renice
	fi

fi
