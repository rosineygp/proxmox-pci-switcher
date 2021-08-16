from proxmoxer import ProxmoxAPI
import yaml
from argh import named, aliases, arg, dispatch_commands
import os
from tabulate import tabulate
import sys

DEFAULT_LINUX_PATH = "~/.config/proxmox-pci-switcher/config.yaml"
DEFAULT_WINDOWS_PATH = "~\\AppData\\Local\\proxmox-pci-switcher\\config.yaml"


def expand_config_path(path):
    """
    Expand config file path and switch default path if OS is windows.

    Parameters:
    path (str): file path (yaml)

    Returns:
    str: path expanded
    """
    if path == DEFAULT_LINUX_PATH and os.name == "nt":
        path = DEFAULT_WINDOWS_PATH
    return os.path.expanduser(path)


def load_config_file(path):
    """
    Load and parser yaml file.

    Parameters:
    path (str): full yaml path location

    Returns:
    dict: yaml file in parsed into a dict
    """
    with open(path) as file:
        return yaml.load(file, Loader=yaml.FullLoader)


def connection_proxmox(config):
    """
    Create a instance of proxmox API.

    Parameters:
    config (dict): parsed yaml config

    Returns:
    ProxmoxAPI: instance of proxmox API
    """
    return ProxmoxAPI(
        config["host"],
        user=config["user"],
        password=config["password"],
        verify_ssl=config["verify_ssl"],
    )


def proxmox_pci_switcher(px, item):
    """
    Start a VM

    Parameters:
    px (ProxmoxAPI): instance of proxmox API
    item (dict): ['vmid', 'name'] a dict with following data

    Returns:
    None
    """
    node = px.nodes.get()[0]

    if (
        px.nodes(node["node"]).qemu(item["vmid"]).status("current").get()["status"]
        == "stopped"
    ):
        print(f"power on vm '{item['name']}'")
        px.nodes(node["node"]).qemu(item["vmid"]).status("start").post()
    else:
        print(f"vm '{item['name']}' is running.")


def list_resources(px, pools):
    """
    List resources by pools

    Parameters:
    px (ProxmoxAPI): instance of proxmox API
    pools (array): list of pools names

    Returns:
    tuple: Resource pools list;
           Dict with items headers.
    """
    result = []
    for pool in pools:
        for i in px.pools.get(pool)["members"]:
            result.append(
                {
                    "pool": pool,
                    "vmid": i["vmid"],
                    "name": i["name"],
                    "status": i["status"],
                    "type": i["type"],
                }
            )
    return result, {
        "pool": "pool(s)",
        "vmid": "vmid",
        "name": "name",
        "status": "status",
        "type": "type",
    }


@named("list")
@aliases("l")
@arg(
    "-c",
    "--config",
    help="config file path",
    default=DEFAULT_LINUX_PATH,
)
def cmd_list_resources(config=DEFAULT_LINUX_PATH):
    """
    List resources by pool(s).
    """
    config = load_config_file(expand_config_path(config))
    px = connection_proxmox(config["proxmox"])
    try:
        if config["pools"]:
            l, h = list_resources(px, config["pools"])
            return tabulate(l, h)
        else:
            print("Dict 'pools' is empty")
    except KeyError:
        print("Missing 'pools' dict in config file")
        sys.exit(1)


@named("switch")
@aliases("s")
@arg("name", help="proxmox vmid or name")
@arg(
    "-c",
    "--config",
    help="config file path",
    default=DEFAULT_LINUX_PATH,
)
def cmd_switch_vm(name, config=DEFAULT_LINUX_PATH):
    """
    Switcher virtual machine to use one pci resource like GPU
    """
    config = load_config_file(expand_config_path(config))
    px = connection_proxmox(config["proxmox"])
    resources, _ = list_resources(px, config["pools"])

    name_int = -1
    try:
        name_int = int(name)
    except Exception as e:
        print(e)

    item = list(filter(lambda i: i["vmid"] == name_int or i["name"] == name, resources))

    if item:
        proxmox_pci_switcher(px, item[0])
    else:
        print(f"resource: '{name}' not found.")
        sys.exit(1)


def __main():
    dispatch_commands([cmd_list_resources, cmd_switch_vm])


if __name__ == "__main__":
    __main()
