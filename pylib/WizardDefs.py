# -*- coding: utf-8 -*-

class WizardPage(object):
    enabled = True
    page_title = None
    page_subtitle = None
    page_id = None
    layout = "vertical"
    banner = None
    template = "default"
    content = None
    custom_button1 = None
    custom_button2 = None
    custom_button3 = None
    
    def __str__(self):
        return self.page_title

    def get_page_title(self):
        return self.__str__()

    def get_page_subtitle(self):
        return self.page_subtitle

    def get_page_id(self):
        return self.page_id

    def get_next_page_id(self):
        return -2

    def get_layout(self):
        return self.layout

    def get_banner(self):
        return self.banner

    def get_template(self):
        return self.template
        
    def get_content(self):
        return self.content
