#!/usr/bin/env python

from proxmoxer import ProxmoxAPI
import yaml
import argh
import os


@argh.arg('name', help='machine name')
@argh.arg('-c', '--config', help='yaml file path, otherwise .config.yaml')
def proxmox_pci_switcher(name, config='~/.config/proxmox-pci-switcher/config.yaml'):
    """Switcher virtual machine to use one pci resource like GPU"""

    with open(os.path.expanduser(config)) as file:
        pconfig = yaml.load(file, Loader=yaml.FullLoader)

    proxmox = ProxmoxAPI(pconfig['proxmox']['host'],
                         user=pconfig['proxmox']['user'],
                         password=pconfig['proxmox']['password'],
                         verify_ssl=pconfig['proxmox']['verify_ssl'])

    # use first node
    node = proxmox.nodes.get()[0]

    target = False
    for t in pconfig['targets']:
        if name == t['name']:
            target = t
            break

    if target:
        if proxmox.nodes(node['node']).qemu(target['vmid']).status('current').get()['status'] == "stopped":
            print(f"power on vm '{name}', see you later!")
            proxmox.nodes(node['node']).qemu(
                target['vmid']).status('start').post()
        else:
            print(f"target vm '{name}' is running.")
    else:
        print(f"vm '{name}', not found in '{config}' file.")


if __name__ == '__main__':
    argh.dispatch_command(proxmox_pci_switcher)
