# -*- coding: utf-8 -*-


class Manage(object):

    def __init__(self, modality='block'):
        self.modaliity = modality
        self.enabled = True
        self.menu_list = []
        self.action_list = []
        self.connect_list = []
        self.widget_matrix = []

    def __str__(self):
        return 'Manage'

    def add_menu(self, menu):
        self.menu_list.append(menu)

    def add_action(self, action):
        self.action_list.append(action)

    def add_row(self, widget_list):
        self.widget_matrix.append(widget_list)

    def get_menu_list(self):
        return self.menu_list

    def get_action_list(self):
        return self.action_list

    def get_widget_matrix(self):
        return self.widget_matrix

    def get_modality(self):
        return self.modaliity
