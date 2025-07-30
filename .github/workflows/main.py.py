from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import StringProperty, BooleanProperty
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.menu import MDDropdownMenu
from kivy.storage.jsonstore import JsonStore
import os, webbrowser

Window.size = (360, 640)

KV = '''
MDScreenManager:
    LoginScreen:
        name: "login"
    MainScreen:
        name: "main"

<LoginScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 20

        MDTopAppBar:
            title: "Neuron Academy"
            icon: "school"

        # Optional logo image - add logo.png to same folder if needed
        # Image:
        #     source: "logo.png"
        #     size_hint_y: 0.3

        MDTextField:
            id: username
            hint_text: "Username"
            icon_right: "account"

        MDTextField:
            id: password
            hint_text: "Password"
            icon_right: "lock"
            password: True

        MDTextField:
            id: class_input
            hint_text: "Enter Class (e.g., Class 6)"
            helper_text: "Required for Student login only"
            helper_text_mode: "on_focus"
            opacity: 1 if app.role == "student" else 0
            disabled: False if app.role == "student" else True

        MDRaisedButton:
            text: "Login"
            pos_hint: {"center_x": 0.5}
            on_release: app.login(username.text, password.text, class_input.text)

<MainScreen>:
    MDBottomNavigation:
        id: nav

        MDBottomNavigationItem:
            name: 'timetable'
            text: 'Timetable'
            icon: 'calendar'
            ScrollView:
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: 10
                    spacing: 10
                    size_hint_y: None
                    height: self.minimum_height

                    MDLabel:
                        text: "📅 Timetable"
                        bold: True

                    Image:
                        source: app.timetable_file if app.timetable_file.endswith(('.jpg', '.png')) else ''
                        size_hint_y: None
                        height: 200 if app.timetable_file.endswith(('.jpg', '.png')) else 0

                    MDRaisedButton:
                        text: "Open PDF"
                        opacity: 1 if app.timetable_file.endswith('.pdf') else 0
                        on_release: app.open_file(app.timetable_file)
                        disabled: not app.timetable_file.endswith('.pdf')

                    MDLabel:
                        text: app.timetable_text if not app.timetable_file else ""

        MDBottomNavigationItem:
            name: 'tests'
            text: 'Tests'
            icon: 'file-document'
            ScrollView:
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: 10
                    spacing: 10
                    size_hint_y: None
                    height: self.minimum_height

                    MDLabel:
                        text: "📝 Test Schedule"
                        bold: True

                    Image:
                        source: app.tests_file if app.tests_file.endswith(('.jpg', '.png')) else ''
                        size_hint_y: None
                        height: 200 if app.tests_file.endswith(('.jpg', '.png')) else 0

                    MDRaisedButton:
                        text: "Open PDF"
                        opacity: 1 if app.tests_file.endswith('.pdf') else 0
                        on_release: app.open_file(app.tests_file)
                        disabled: not app.tests_file.endswith('.pdf')

                    MDTextField:
                        id: test_writer
                        hint_text: "Write test schedule (Teacher/Admin only)"
                        multiline: True
                        on_text: app.tests_text = self.text
                        readonly: not app.can_edit_test()

        MDBottomNavigationItem:
            name: 'modules'
            text: 'Modules'
            icon: 'book-open'
            ScrollView:
                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: 15
                    padding: 10
                    size_hint_y: None
                    height: self.minimum_height

                    MDLabel:
                        text: "📚 Modules"
                        bold: True

                    MDRaisedButton:
                        text: "Open Modules File"
                        on_release: app.open_file(app.modules_file)
                        disabled: not app.modules_file

        MDBottomNavigationItem:
            name: 'announ.'
            text: 'Announ.'
            icon: 'bullhorn'
            ScrollView:
                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: 10
                    padding: 10
                    size_hint_y: None
                    height: self.minimum_height

                    MDLabel:
                        text: "📢 Announcements"

                    MDTextField:
                        id: announcement_input
                        hint_text: "Write announcement (Admin/Teacher only)"
                        multiline: True
                        on_text: app.announcement_text = self.text
                        readonly: not app.can_write_announcement()

        MDBottomNavigationItem:
            name: 'settings'
            text: 'Settings'
            icon: 'cog'
            MDBoxLayout:
                orientation: 'vertical'
                padding: 20
                spacing: 20

                MDSwitch:
                    id: theme_switch
                    text: "Dark Mode"
                    on_active: app.toggle_theme(self.active)

                MDSwitch:
                    text: "Notifications (not implemented)"

        MDBottomNavigationItem:
            name: 'admin'
            text: 'Admin Panel'
            icon: 'shield-account'
            id: admin_tab
            on_tab_press: app.reset_admin_panel()
            opacity: 0
            disabled: True

            ScrollView:
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: 15
                    spacing: 15
                    size_hint_y: None
                    height: self.minimum_height

                    MDLabel:
                        text: "🔧 Admin Panel"
                        halign: "center"
                        theme_text_color: "Primary"

                    MDLabel:
                        text: "Select Class:"
                    MDDropDownItem:
                        id: class_selector
                        text: app.admin_selected_class or "Select Class"
                        on_release:
                            app.menu.caller = self
                            app.menu.open()

                    MDTextField:
                        hint_text: "Write Timetable (optional if file uploaded)"
                        multiline: True
                        on_text: app.timetable_text = self.text

                    MDRaisedButton:
                        text: "Upload Timetable File"
                        on_release: app.open_file_manager("timetable")

                    MDTextField:
                        hint_text: "Write Test Schedule"
                        multiline: True
                        on_text: app.tests_text = self.text

                    MDRaisedButton:
                        text: "Upload Test Schedule File"
                        on_release: app.open_file_manager("tests")

                    MDTextField:
                        hint_text: "Write Announcement"
                        multiline: True
                        on_text: app.announcement_text = self.text

                    MDRaisedButton:
                        text: "Upload Module File"
                        on_release: app.open_file_manager("modules")

                    MDRaisedButton:
                        text: "Save for Selected Class"
                        on_release: app.save_class_data()
'''


class LoginScreen(MDScreen):
    pass


class MainScreen(MDScreen):
    pass


class NeuronAcademyApp(MDApp):
    role = "student"
    selected_class = ""
    admin_selected_class = StringProperty("")
    timetable_file = StringProperty("")
    tests_file = StringProperty("")
    modules_file = StringProperty("")
    announcement_text = StringProperty("")
    timetable_text = StringProperty("")
    tests_text = StringProperty("")
    file_target = ""
    dark_mode = BooleanProperty(False)

    def build(self):
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.theme_style = "Light"
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True,
        )
        self.store = JsonStore("neuron_data.json")
        self.menu = MDDropdownMenu(
            caller=None,
            items=[
                {"viewclass": "OneLineListItem", "text": f"Class {i}", "on_release": lambda x=f"Class {i}": self.set_admin_class(x)}
                for i in range(6, 13)
            ],
            width_mult=4,
        )
        return Builder.load_string(KV)

    def login(self, username, password, class_name):
        if username == "admin" and password == "admin123":
            self.role = "admin"
            self.selected_class = "Class 10"
        elif username == "teacher" and password == "teacher123":
            self.role = "teacher"
            self.selected_class = class_name.strip()
        elif username == "student" and password == "student123":
            self.role = "student"
            self.selected_class = class_name.strip()
        else:
            self.show_dialog("Error", "Incorrect credentials.")
            return

        if self.role == "student" and not self.selected_class:
            self.show_dialog("Error", "Please enter your class.")
            return

        self.load_class_data(self.selected_class)
        self.root.current = "main"
        admin_tab = self.root.get_screen("main").ids.admin_tab
        admin_tab.disabled = self.role != "admin"
        admin_tab.opacity = 1 if self.role == "admin" else 0

    def load_class_data(self, class_name):
        if self.store.exists(class_name):
            data = self.store.get(class_name)
            self.timetable_file = data.get("timetable_file", "")
            self.tests_file = data.get("tests_file", "")
            self.modules_file = data.get("modules_file", "")
            self.announcement_text = data.get("announcement_text", "")
            self.timetable_text = data.get("timetable_text", "")
            self.tests_text = data.get("tests_text", "")
        else:
            self.timetable_file = ""
            self.tests_file = ""
            self.modules_file = ""
            self.announcement_text = ""
            self.timetable_text = ""
            self.tests_text = ""

    def save_class_data(self):
        class_key = self.admin_selected_class if self.role == "admin" else self.selected_class
        if not class_key:
            self.show_dialog("Error", "Please select a class.")
            return
        self.store.put(class_key,
            timetable_file=self.timetable_file,
            tests_file=self.tests_file,
            modules_file=self.modules_file,
            announcement_text=self.announcement_text,
            timetable_text=self.timetable_text,
            tests_text=self.tests_text,
        )
        self.show_dialog("Saved", f"Data saved for {class_key}")

    def open_file_manager(self, target):
        self.file_target = target
        self.file_manager.show(os.path.expanduser("~"))

    def select_path(self, path):
        if self.file_target == "timetable":
            self.timetable_file = path
        elif self.file_target == "tests":
            self.tests_file = path
        elif self.file_target == "modules":
            self.modules_file = path
        self.save_class_data()
        self.exit_manager()

    def exit_manager(self, *args):
        self.file_manager.close()

    def open_file(self, path):
        if os.path.exists(path):
            webbrowser.open("file://" + path)
        else:
            self.show_dialog("Error", "File not found!")

    def toggle_theme(self, is_dark):
        self.theme_cls.theme_style = "Dark" if is_dark else "Light"

    def can_edit_test(self):
        return self.role in ["teacher", "admin"]

    def can_write_announcement(self):
        return self.role in ["teacher", "admin"]

    def show_dialog(self, title, text):
        MDDialog(title=title, text=text).open()

    def set_admin_class(self, class_name):
        self.admin_selected_class = class_name
        self.root.get_screen("main").ids.class_selector.text = class_name
        self.menu.dismiss()
        self.load_class_data(class_name)

    def reset_admin_panel(self):
        self.root.get_screen("main").ids.class_selector.text = self.admin_selected_class or "Select Class"


if __name__ == "__main__":
    NeuronAcademyApp().run()
