import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from toga.widgets.base import Widget
import travertino.constants as constants
import os
import json
import hashlib

class UIHandler:
    def __init__(self) -> None:
        self._main_box = toga.Box(style=Pack(direction=COLUMN))

    def add_ui_element(self, *element : Widget):
        self._main_box.add(*element)
        self._main_box.refresh()

    def remove_ui_element(self, *element : Widget):
        for e in element:
            self._main_box.remove(e)
    
    def clear_ui(self):
        self._main_box.remove(*self._main_box.children)

    def get_main_box(self):
        return self._main_box
    
    def switch_page(self, *element : Widget):
        self.clear_ui()
        self.add_ui_element(*element)
        

class HomePage(toga.Box):
    def __init__(self, app_fld, ui, app):
        super().__init__()

        def start_callback():
            def on_press(button):
                self.status_label.style.update(color = constants.GREEN)
                self.status_label.text = "ONLINE"
                self.status = True
                app.lr_factory.start_lr()
            return on_press
        
        def stop_callback():
            def on_press(button):
                self.status_label.style.update(color = constants.RED)
                self.status_label.text = "OFFLINE"
                self.status = False
                app.lr_factory.stop_lr()
            return on_press

        self.style = Pack(direction=COLUMN, alignment=CENTER)

        logo = toga.Image(os.path.join(app_fld, 'resources', 's4t_logo.png'))
        logo_show = toga.ImageView(image=logo, style=Pack(width=256, height=256, padding_top=20, padding_bottom=10))
        self.add(logo_show)

        status_box = toga.Box(style=Pack(direction=ROW, padding_top=5, padding_bottom=10))
        status_box.add(toga.Box(style=Pack(flex=1/2)))
        status_box.add(toga.Label("Lightning-rod status: ", style=Pack(font_size=18)))
        self.status_label = toga.Label("", style=Pack(font_size=18))
        self.status = app.lr_factory.should_run

        if (self.status):
            self.status_label.style.update(color = constants.GREEN)
            self.status_label.text = "ONLINE"
        else:
            self.status_label.style.update(color = constants.RED)
            self.status_label.text = "OFFLINE"
        status_box.add(self.status_label)
        status_box.add(toga.Box(style=Pack(flex=1/2)))
        self.add(status_box)

        btn_box = toga.Box(style=Pack(direction=ROW, padding_top=10, padding_bottom=10))
        btn_box.add(toga.Box(style=Pack(flex=0.5)))
        self.start_button = toga.Button(text="Start Lighting-rod", style=Pack(padding_left=10, padding_right=10),
                                        on_press=start_callback())
        btn_box.add(self.start_button)
        self.stop_button = toga.Button(text="Stop Lighting-rod", style=Pack(padding_left=10, padding_right=10),
                                       on_press=stop_callback())
        btn_box.add(self.stop_button)
        btn_box.add(toga.Box(style=Pack(flex=0.5)))

        self.add(btn_box)


class Toolbar(toga.Box):
    def __init__(self, app_fld, ui, app):
        super().__init__()

        def toolbar_callback(*pages):
            def on_press(button):
                ui.switch_page(*pages)
            return on_press

        self.style = Pack(direction=ROW)
        self.home_btn = toga.Button("Home 🏠", style=Pack(flex=1/3, padding_right=5),
                                    on_press=toolbar_callback(*[HomePage(app_fld, ui, app), Filler(app_fld, ui, app), self]))
        self.log_btn = toga.Button("Logs 📜", style=Pack(flex=1/3, padding_right=5),
                                   on_press=toolbar_callback(*[LogViewer(app_fld, ui, app), self]))
        self.settings_btn = toga.Button("Settings ⚙️", style=Pack(flex=1/3),
                                        on_press=toolbar_callback(*[SettingsPage(app_fld, ui, app), Filler(app_fld, ui, app), self]))
        
        self.add(self.home_btn)
        self.add(self.log_btn)
        self.add(self.settings_btn)


class Filler(toga.Box):
    def __init__(self, app_fld, ui, app):
        super().__init__()
        self.style = Pack(flex=1)
        

class LogViewer(toga.Box):
    def __init__(self, app_fld, ui, app):
        super().__init__()

        def update_logs_callback():
            def on_press(button):
                self.log_viewer.clear()
                self.log_viewer.value = app.log_handler.get_logs()
                self.log_viewer.refresh()
                self.log_viewer.scroll_to_bottom()
                
                
            return on_press
    
        self.style = Pack(direction=COLUMN, flex=1)
        self.log_viewer = toga.MultilineTextInput(
            readonly=True,
            style=Pack(padding_top=20, padding_left=20, padding_right=20, flex=1)
        )

        self.log_updater = toga.Button(text="Update Logs", style=Pack(padding_bottom=20, padding_left=20, padding_right=20), 
                                       on_press=update_logs_callback())
        self.add(self.log_viewer)
        self.add(self.log_updater)


class SettingsPage(toga.Box):
    def __init__(self, app_fld, ui, app):
        super().__init__()

        def settings_callback(*pages):
            def on_press(button):
                ui.switch_page(*pages)
            return on_press

        self.style = Pack(direction=COLUMN, padding=20)
        self.plugins_btn = toga.Button("✏️   Edit plugins.json", style=Pack(padding_bottom=15),
                                       on_press=settings_callback(*[FileEditor(app_fld, ui, app, os.path.join(app_fld, 'data', 'iotronic', 'plugins.json'))]))
        self.services_btn = toga.Button("✏️   Edit services.json", style=Pack(padding_bottom=15),
                                        on_press=settings_callback(*[FileEditor(app_fld, ui, app, os.path.join(app_fld, 'data', 'iotronic', 'services.json'))]))
        self.settings_btn = toga.Button("✏️   Edit settings.json", style=Pack(padding_bottom=15),
                                        on_press=settings_callback(*[FileEditor(app_fld, ui, app, os.path.join(app_fld, 'data', 'iotronic', 'settings.json'))]))
        self.auth_btn = toga.Button("🔒   Change password",
                                        on_press=settings_callback(*[PasswordEditor(app_fld, ui, app)]))

        self.add(*[self.plugins_btn, self.services_btn, self.settings_btn, self.auth_btn])


class FileEditor(toga.Box):
    def __init__(self, app_fld, ui, app, file_path):
        super().__init__()

        def save_callback():
            def on_press(button):
                # Save document here
                try:
                    content = json.loads(self.text_editor.value)
                    with open (file_path, 'w') as f:
                        json.dump(content, f, indent=2)
                    self.result_label.style.update(color = constants.GREEN)
                    self.result_label.text = "Changes saved successfully"
                except json.JSONDecodeError as e:
                    self.result_label.style.update(color = constants.RED)
                    self.result_label.text = f"Could not save changes: {str(e)}"

            return on_press
        
        def cancel_callback():
            def on_press(button):
                # Cancel operations here
                ui.switch_page(*[SettingsPage(app_fld, ui, app), Filler(app_fld, ui, app), Toolbar(app_fld, ui, app)])
            return on_press

        self.style = Pack(direction=COLUMN, flex=1, padding=10)

        self.text_editor = toga.MultilineTextInput(
            style=Pack(flex=1)
        )

        with open(file_path, 'r') as f:
            try:
                self.text_editor.value = f.read()
            except FileNotFoundError:
                self.text_editor.value = "Could not open the specified file"
        
        btn_box = toga.Box(style=Pack(direction=ROW))
        save_btn = toga.Button(text = "💾   Save", style=Pack(flex=0.5), 
                               on_press = save_callback())
        cancel_btn = toga.Button(text = "❌   Exit", style=Pack(flex=0.5),
                                 on_press = cancel_callback())

        btn_box.add(*[save_btn, cancel_btn])

        self.result_label = toga.Label(text="", style=Pack(padding_top = 2, padding_bottom = 2))
        self.add(*[self.text_editor, self.result_label, btn_box])


class PasswordEditor(toga.Box):
    def __init__(self, app_fld, ui, app):
        super().__init__()

        def save_callback(auth_file):
            def on_press(button):
                with open(auth_file, "r") as f:
                    auth = json.load(f)
                
                # Perform checks here
                old_salt = bytes.fromhex(auth["salt"])
                old_pwd_hash = bytes.fromhex(auth["password_hash"])

                data_to_hash = self.current_password_input.value.encode('utf-8') + old_salt
                computed_hash = hashlib.sha256(data_to_hash).digest()

                if (computed_hash != old_pwd_hash or self.current_username_input.value != auth["username"]):
                    self.result_label.style.update(color = constants.RED)
                    self.result_label.text = "Wrong username or password"
                    return

                # Write new auth
                
                if self.new_password_input.value == self.confirm_password_input.value:
                    salt = os.urandom(16)
                    data = self.new_password_input.value.encode('utf-8') + salt
                    sha256_hash = hashlib.sha256(data).hexdigest()
                else:
                    self.result_label.style.update(color = constants.RED)
                    self.result_label.text = "Passwords do not match"
                    return

                if self.new_username_input.value != "":
                    auth["username"] = self.new_username_input.value

                auth["password_hash"] = sha256_hash
                auth["salt"] = salt.hex()

                with open(auth_file, "w") as f:
                    json.dump(auth, f, indent=2)

                self.result_label.style.update(color = constants.GREEN)
                self.result_label.text = "Username and password saved successfully"
                

            return on_press
        
        def cancel_callback():
            def on_press(button):
                # Cancel operations here
                ui.switch_page(*[SettingsPage(app_fld, ui, app), Filler(app_fld, ui, app), Toolbar(app_fld, ui, app)])
            return on_press

        self.style = Pack(direction=COLUMN, flex=1, padding=10)

        self.current_username_input = toga.TextInput(placeholder="Current username", style=Pack(padding_bottom=10))
        self.current_password_input = toga.TextInput(placeholder="Current password", style=Pack(padding_bottom=10))
        self.new_username_input = toga.TextInput(placeholder="New username (optional)", style=Pack(padding_bottom=10))
        self.new_password_input = toga.TextInput(placeholder="New password", style=Pack(padding_bottom=10))
        self.confirm_password_input = toga.TextInput(placeholder="Confirm new password", style=Pack(padding_bottom=10))
        
        btn_box = toga.Box(style=Pack(direction=ROW))
        save_btn = toga.Button(text = "💾   Save", style=Pack(flex=0.5), 
                               on_press = save_callback(os.path.join(app_fld, 'data', 'auth.json')))
        cancel_btn = toga.Button(text = "❌   Exit", style=Pack(flex=0.5),
                                 on_press = cancel_callback())

        btn_box.add(*[save_btn, cancel_btn])

        self.result_label = toga.Label(text="", style=Pack(padding_top = 2, padding_bottom = 2))
        self.add(*[
            toga.Label(text="Current username", style=Pack(padding_bottom=5)),
            self.current_username_input,
            toga.Label(text="Current password", style=Pack(padding_bottom=5)),
            self.current_password_input,
            toga.Label(text="New username (optional)", style=Pack(padding_bottom=5)),
            self.new_username_input,
            toga.Label(text="New password", style=Pack(padding_bottom=5)),
            self.new_password_input,
            toga.Label(text="Confirm new password", style=Pack(padding_bottom=5)),
            self.confirm_password_input,
            self.result_label,
            Filler(app_fld, ui, app),
            btn_box
        ])
