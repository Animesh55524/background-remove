from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserListView
from kivy.core.window import Window
from kivy.utils import platform
from rembg import remove
from PIL import Image as PILImage
import os
import io

# If running on Android, set up storage permissions
if platform == "android":
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path

    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
    storage_path = primary_external_storage_path()
else:
    storage_path = os.path.expanduser("~")


class RemoveBGApp(App):
    def build(self):
        Window.clearcolor = (0.95, 0.95, 0.95, 1)  # Light background
        self.icon = "icon.png"  # Use .png instead of .ico for Android
        self.title = "Remove Background App"

        # Main layout
        main_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        # Logo at the top
        logo_widget = Image(source="logo.png", size_hint=(1, 0.2), allow_stretch=True, keep_ratio=True)
        main_layout.add_widget(logo_widget)

        # Input and output image widgets
        self.input_image_widget = Image(size_hint=(1, 0.4))
        self.output_image_widget = Image(size_hint=(1, 0.4))
        main_layout.add_widget(self.input_image_widget)
        main_layout.add_widget(self.output_image_widget)

        # Buttons for actions
        buttons_layout = BoxLayout(size_hint=(1, 0.1))
        select_button = Button(text="Select Image")
        remove_button = Button(text="Remove Background")
        remove_button.disabled = True  # Initially disabled

        select_button.bind(on_release=self.open_folder_dialog)
        remove_button.bind(on_release=self.remove_background)
        buttons_layout.add_widget(select_button)
        buttons_layout.add_widget(remove_button)
        main_layout.add_widget(buttons_layout)

        self.remove_button = remove_button
        self.file_path = None

        return main_layout

    def open_folder_dialog(self, instance):
        filechooser = FileChooserListView(filters=["*.png", "*.jpg", "*.jpeg"], path=storage_path)
        popup_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        popup_layout.add_widget(Label(text="Select an Image File", size_hint=(1, 0.1)))
        popup_layout.add_widget(filechooser)

        # Buttons for file chooser
        button_layout = BoxLayout(size_hint=(1, 0.1))
        select_button = Button(text="Select")
        cancel_button = Button(text="Cancel")

        def load_image(instance):
            if filechooser.selection:
                self.file_path = filechooser.selection[0]
                popup.dismiss()
                self.display_input_image(self.file_path)
                self.remove_button.disabled = False

        def close_popup(instance):
            popup.dismiss()

        select_button.bind(on_release=load_image)
        cancel_button.bind(on_release=close_popup)
        button_layout.add_widget(select_button)
        button_layout.add_widget(cancel_button)

        popup_layout.add_widget(button_layout)
        popup = Popup(title="Open Folder", content=popup_layout, size_hint=(0.9, 0.9))
        popup.open()

    def display_input_image(self, file_path):
        self.input_image_widget.source = file_path
        self.input_image_widget.reload()

    def remove_background(self, instance):
        if not self.file_path:
            return

        with open(self.file_path, "rb") as file:
            input_data = file.read()
            output_data = remove(input_data)

        output_image = PILImage.open(io.BytesIO(output_data))
        output_path = os.path.join(storage_path, "Download", "output_no_bg.png")
        output_image.save(output_path)

        self.output_image_widget.source = output_path
        self.output_image_widget.reload()


if __name__ == "__main__":
    RemoveBGApp().run()
