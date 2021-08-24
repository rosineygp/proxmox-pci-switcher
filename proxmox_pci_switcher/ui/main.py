from kivymd.app import MDApp
from kivymd.uix.list import OneLineAvatarListItem, IconLeftWidget

from proxmox_pci_switcher import (
    DEFAULT_LINUX_PATH,
    DEFAULT_WINDOWS_PATH,
    expand_config_path,
    load_config_file,
    connection_proxmox,
    list_resources,
    proxmox_pci_switcher,
)

config = load_config_file(expand_config_path(DEFAULT_LINUX_PATH))
px = connection_proxmox(config["proxmox"])


def click():
    print("click")


class AvatarIcon(OneLineAvatarListItem):
    def on_release(self, *args):
        print(args)
        print("hello2")
        print(self.item)
        proxmox_pci_switcher(px, self.item)

    def data(self, item):
        self.item = item


class MainApp(MDApp):
    def cc(self, *btn):
        print(btn)
        print("hello")

    def on_start(self):
        l, _ = list_resources(px, config["pools"])

        for i in l:
            li = AvatarIcon(text=i["name"])

            li.data(i)

            if i["status"] == "running":
                li.add_widget(IconLeftWidget(icon="play-circle-outline"))
            else:
                li.add_widget(IconLeftWidget(icon="stop-circle"))

            self.root.ids.container.add_widget(li)


MainApp().run()
