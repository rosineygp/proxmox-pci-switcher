from kivymd.app import MDApp
from kivymd.uix.list import OneLineAvatarListItem, IconLeftWidget
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar

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


class ButtonSwitcher(MDRaisedButton):

    _data = None

    def on_release(self, *args):
        print(self._data)
        Snackbar(text=f"Turn on vm {self._data['name']}").open()
        # proxmox_pci_switcher(px, self._data)


class AvatarIcon(OneLineAvatarListItem):

    _data = None
    _dialog = None

    def on_release(self, *args):
        print(args)
        print(self._data)

        if not self._dialog:

            btn_switcher = ButtonSwitcher(text="OK")
            btn_switcher._data = self._data

            if self._data["status"] == "running":
                btn_switcher.disabled = True

            self._dialog = MDDialog(
                text=f"Turn on vm {self._data['name']} ?",
                buttons=[
                    MDFlatButton(
                        text="CANCEL", on_release=lambda _: self._dialog.dismiss()
                    ),
                    btn_switcher,
                ],
            )
        self._dialog.open()


class MainApp(MDApp):

    _theme_style = "Light"
    _md_list = []
    dialog = None

    def theme_switch(self):
        if self.theme_cls.theme_style == "Dark":
            self.theme_cls.theme_style = "Light"  # "Light"
        else:
            self.theme_cls.theme_style = "Dark"

    def cc(self, *btn):
        print(btn)
        print("hello")

    def refresh(self, *args):
        self.on_start()
        Snackbar(text="Refresh!").open()

    def on_start(self, *args):
        _list_size = len(self._md_list)
        if _list_size > 0:
            for i in range(_list_size):
                self.root.ids.container.remove_widget(self._md_list.pop())

        for i in list_resources(px, config["pools"])[0]:
            li = AvatarIcon(text=i["name"])

            if i["status"] == "running":
                li.add_widget(IconLeftWidget(icon="play-circle-outline"))
            else:
                li.add_widget(IconLeftWidget(icon="stop-circle"))

            li._data = i
            self._md_list.append(li)

            self.root.ids.container.add_widget(li)


MainApp().run()
