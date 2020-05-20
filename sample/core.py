from datetime import date,datetime
from subprocess import call
import operator
import os
import pudb #TODO
import pyperclip
import shutil

from objects import *
import cli
import notes
import rdf
import tui


"""
Business logic of the contact TUI.
"""
class Core:

    def __init__(self, config, test=False):
        self.rdfstore = rdf.RDFStore(config['path']['rdf_file'], config['rdf']['namespace'])
        self.notesstore = notes.NotesStore(config['path']['notes_dir'], config['editor'])
        self.cli = cli.CLI(self)
        self.last_keypress = None
        contacts = self.get_all_contacts()

        self.frame = tui.ContactFrame(config, self)
        self.frame.set_contact_list(contacts)

        if not test:
            loop = tui.ContactLoop(self.frame, config)

    """
    Returns a list of all contacts without their details.
    """
    def get_all_contacts(self):
        contact_names = self.rdfstore.get_all_contact_names() \
                + self.notesstore.get_all_contact_names()
        sorted_contact_names = sorted(set(contact_names))
        contacts = []
        for c in sorted_contact_names:
            contacts.append(Contact(c, self))
        return contacts 

    """
    Returns a list of the names of all contacts.
    """
    def get_all_contact_names(self):
        contact_names = self.rdfstore.get_all_contact_names() \
                + self.notesstore.get_all_contact_names()
        return sorted(set(contact_names))

    def contains_contact(self, contact):
        return self.rdfstore.contains_contact(contact) or \
                self.notesstore.contains_contact(contact)

    def contains_contact_name(self, name):
        return self.rdfstore.contains_contact_name(name) or \
                self.notesstore.contains_contact_name(name)

    def get_contact(self, name):
        pass

    def search_contact(self, name):
        self.frame.contact_list.jump_to_contact(name)
        return ""

    def add_contact(self, contact):
        if self.contains_contact(contact):
            return "Error: {} already exists.".format(contact.name)
        self.rdfstore.add_contact(contact)
        return "{} added.".format(contact.name)

    def rename_contact(self, contact, new_name):
        if not self.contains_contact(contact):
            return "Error: {} doesn't exist.".format(contact.name)
        if contact.name == new_name:
            return "Name unchanged."
        if self.contains_contact_name(new_name):
            return "Error: {} already exists.".format(new_name)
        if self.rdfstore.contains_contact(contact):
            self.rdfstore.rename_contact(contact, new_name)
        if self.notesstore.contains_contact(contact):
            self.notesstore.rename_contact(contact, new_name)
        return "{} renamed to {}.".format(contact.name, new_name)

    def delete_contact(self, contact):
        if not self.contains_contact(contact):
            return "Error: {} doesn't exists.".format(contact.name)
        if self.rdfstore.contains_contact(contact):
            self.rdfstore.delete_contact(contact)
        if self.notesstore.contains_contact(contact):
            self.notesstore.delete_contact(contact)
        return "{} deleted.".format(contact.name)
