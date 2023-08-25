"""
Porting of Lightning-rod to other devices and architectures
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import os
from lightningrodapp.lightningrod_factory import LightningRodFactory
import lightningrodapp.pages as pages
import lightningrodapp.utils as utils

import logging

class LightningrodApp(toga.App):

    def startup(self):
        """
        Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        os.environ['DATA_FOLDER'] = os.path.join(self.paths.app, 'data')

        # Empty tmp folder
        tmp_folder = os.path.join(self.paths.app, 'data', 'tmp')
        if not os.path.exists(tmp_folder) : os.makedirs(tmp_folder)
        utils.empty_directory(tmp_folder)

        self.lr_factory = LightningRodFactory()

        self.log_handler = utils.Logger()
        root_logger = logging.getLogger()
        root_logger.addHandler(utils.LogHandler(self.log_handler.logs))

        ###
        # App building

        self.ui_handler = pages.UIHandler()
 
        self.scroll_container = toga.ScrollContainer(content=self.ui_handler.get_main_box())

        # Set Homepage
        self.ui_handler.add_ui_element(*[pages.HomePage(self.paths.app, self.ui_handler, self),
                                        pages.Filler(self.paths.app, self.ui_handler, self),
                                        pages.Toolbar(self.paths.app, self.ui_handler, self)])

        # The app ui will be redrawn every time change_page is invoked         

        ###

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.scroll_container
        self.main_window.show()

def main():
    return LightningrodApp()
