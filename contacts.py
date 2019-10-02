from rdflib import *
from rdflib.resource import *

import urwid
import curses

import operator

import pudb

PATH = 'test.n3'
GIVEN_NAME_REF = URIRef('http://hiea.de/contact#givenName')
g = None


### N3 functions

def loadFile(path):
    g = Graph()
    g.parse(path, format="n3")
    return g

def saveFile(path):
    g.serialize(format='n3', indent=True, destination=path)


def getContacts():
    contacts = []
    for s,p,o in g.triples( (None, GIVEN_NAME_REF, None) ):
        contacts.append(str(o))
        contacts.sort(key=operator.attrgetter('caption'))
    return contacts

def containsContact(name):
    return (None, GIVEN_NAME_REF, Literal(name)) in g

def addContact(name):
    if containsContact(name):
        return ["Error: ", name, " already exists."]
    else:
        g.add( (BNode(), GIVEN_NAME_REF, Literal(name)) )
        saveFile(PATH)
        menu = top.contents[0][0].base_widget.body
        menu.append(SubMenu(name, [SubMenu(u'givenName', [Choice(name)])]))
        menu.sort(key=operator.attrgetter('caption'))
        return [name, " added."]

def removeContact(name):
    if containsContact(name):
        # update n3
        g.remove( (None, GIVEN_NAME_REF, Literal(name)) )
        saveFile(PATH)

        # update urwid
        menu = top.contents[0][0].base_widget.body
        contact = next((x for x in menu if x.caption == name), None) # find list item
        if contact != None:
            menu.remove(contact)
        return [name, " removed."]
    else:
        return ["Error: ", name, " doesn't exists."]

def renameContact(old_name, new_name):
    if containsContact(old_name):
        if old_name == new_name:
            return ["Name unchanged."]

        triples = [s for s,p,o in g.triples((None, GIVEN_NAME_REF, Literal(old_name)))]

        if len(triples) > 1:
            return ["Error: Multiple persons with name ", old_name, " exist."]

        # update n3
        person = Resource(g, triples[0])
        person.set(GIVEN_NAME_REF, Literal(new_name))
        saveFile(PATH)

        # update urwid
        pu.db
        menu = top.contents[0][0].base_widget.body
        contact = next((x for x in menu if x.caption == old_name), None) # find list item
        if contact != None:
            #menu.remove(contact)
            #menu.append(SubMenu(new_name, [SubMenu(u'givenName', [Choice(new_name)])]))
            #TODO funktioniert noch nicht
            contact.caption = new_name
            #menu.append(contact)
            #menu.sort(key=operator.attrgetter('caption'))
        #return str(contact.menu)
        return [old_name, " renamed to ", new_name, "."]
    else:
        return ["Error: ", old_name, " doesn't exists."]


### urwid

class MenuButton(urwid.Button):
    def __init__(self, caption, callback):
        super(MenuButton, self).__init__("")
        urwid.connect_signal(self, 'click', callback)
        self._w = urwid.AttrMap(urwid.SelectableIcon(
            caption, 100), None, 'selected')
            #[u'  \N{BULLET} ', caption], 2), None, 'selected')

    def keypress(self, size, key):
        if key == 'i':
            add()
        elif key == 'h':
            name = str(self._w._original_widget.text)
            remove(name)
        elif key == 'a':
            name = str(self._w._original_widget.text)
            rename(name)
            #DEBUG:
            #edit = urwid.Edit(caption=u":TODO: edit ", edit_text=name)
            #fill.footer = urwid.BoxAdapter(Command(edit), height=1)
            #return super(MenuButton, self).keypress(size, key)
        else:
            return super(MenuButton, self).keypress(size, key)

class SubMenu(urwid.WidgetWrap):
    def __init__(self, caption, choices):
        super(SubMenu, self).__init__(MenuButton(caption, self.open_menu))
        line = urwid.Divider(u'\N{LOWER ONE QUARTER BLOCK}')
        listbox = urwid.ListBox(urwid.SimpleFocusListWalker(choices))
        self.menu = urwid.AttrMap(listbox, 'options')
        self.caption = caption

    def open_menu(self, button):
        top.open_box(self.menu)

    def keypress(self, size, key):
        if key == 't':
            #TODO
            #self.menu._original_widget.change_focus(size, 5)
            #position = self.menu._original_widget._body.next_position
            #self.menu._original_widget._body.set_focus(position)
            #name = str(self.menu._original_widget._body.next_position)
            #name = str(self.menu._original_widget.get_focus())
            #edit = urwid.Edit(caption=u":", edit_text=name)
            #fill.footer = urwid.BoxAdapter(Command(edit), height=5)
            return super(SubMenu, self).keypress(size, key)
        if key == 'r':
            return super(SubMenu, self).keypress(size, key)
        else:
            return super(SubMenu, self).keypress(size, key)


class Choice(urwid.WidgetWrap):
    def __init__(self, caption):
        super(Choice, self).__init__(
            MenuButton(caption, self.item_chosen))
        self.caption = caption

    def item_chosen(self, button):
        response = urwid.Text([u'  You chose ', self.caption, u'\n'])
        done = MenuButton(u'Ok', exit_program)
        response_box = urwid.Filler(urwid.Pile([response, done]))
        top.open_box(urwid.AttrMap(response_box, 'options'))

def exit_program(key):
    raise urwid.ExitMainLoop()


palette = [
    (None,  'light gray', 'black'),
    ('heading', 'light gray', 'black'),
    ('line', 'black', 'black'),
    ('options', 'light gray', 'black'),
    ('focus heading', 'light gray', 'black'),
    ('focus line', 'black', 'black'),
    ('focus options', 'light gray', 'black'),
    ('selected', 'black', 'light gray')]
focus_map = {
    'heading': 'focus heading',
    'options': 'focus options',
    'line': 'focus line'}

class HorizontalBoxes(urwid.Columns):
    def __init__(self):
        super(HorizontalBoxes, self).__init__([], dividechars=1)

    def open_box(self, box):
        if self.contents:
            del self.contents[self.focus_position + 1:]
        self.contents.append((urwid.AttrMap(box, 'options', focus_map),
            self.options('given', 24)))
        self.focus_position = len(self.contents) - 1

def navigation(key):
    if key in keyCommands.keys():
        keyCommands[key]()

def exit():
    raise urwid.ExitMainLoop()

class Command(urwid.Filler):
    def __init__(self, original_widget, data=None):
        super(Command, self).__init__(original_widget)
        self.data = data
    def keypress(self, size, key):
        if key == 'esc':
            fill.footer = None
            fill.set_focus('body')
        if key != 'enter':
            return super(Command, self).keypress(size, key)
        args = self.original_widget.edit_text.split()
        command = args[0]
        if command in ('add'):
            name = " ".join(args[1:])
            msg = addContact(name)
            #updateMenu()
        elif command in ('remove', 'delete', 'rm', 'del'):
            name = " ".join(args[1:])
            msg = removeContact(name)
            #updateMenu()
        elif command in ('rename', 'edit', 'rn'):
            old_name = self.data['name']
            new_name = " ".join(args[1:])
            msg = renameContact(old_name, new_name)
            #updateMenu()
        else:
            msg = 'Not a valid command.'
        self.original_widget = urwid.Text(msg)
        fill.set_focus('body')

def add():
    edit = urwid.Edit(caption=u":", edit_text=u"add ")
    fill.footer = urwid.BoxAdapter(Command(edit), height=1)
    fill.set_focus('footer')

def remove(name):
    edit = urwid.Edit(caption=u":", edit_text="delete {}".format(name))
    fill.footer = urwid.BoxAdapter(Command(edit), height=1)
    fill.set_focus('footer')

def rename(name):
    edit = urwid.Edit(caption=u":", edit_text="rename {}".format(name))
    data = {'name': name}
    fill.footer = urwid.BoxAdapter(Command(edit, data), height=1)
    fill.set_focus('footer')

keyCommands = {
        'q' : exit,
        'Q' : exit}


def loadMenu():
    global g
    g = loadFile(PATH)
    contact_menu = []
    for s,p,o in g.triples( (None, GIVEN_NAME_REF, None) ):
        # attributes
        # TODO make unique (giftIdea only once)
        attributes = []
        for s2,p2,o2 in g.triples( (s, None, None) ):
            # values
            values = []
            for s3,p3,o3 in g.triples( (s, p2, None) ):
                value = Choice(str(o3))
                values.append(value)
            values.sort(key=operator.attrgetter('caption'))
            attribute_menu = SubMenu(str(p2.split("#",1)[1]), values)
            attributes.append(attribute_menu)
        attributes.sort(key=operator.attrgetter('caption'))
        menu_entry = SubMenu(str(o), attributes)
        contact_menu.append(menu_entry)
    contact_menu.sort(key=operator.attrgetter('caption'))
    menu_top = SubMenu(u'Contacts', contact_menu)
    return menu_top

def updateMenu():
    #TODO Wenn ich die n3 verändert habe (z. B. durch add/rename/delete) sehe ich zwar die Änderung und kann weiterhin durch die oberste Menüebene navigieren, aber kann die Attribute der Kontakte nicht mehr sehen
    # TODO Hinzufügen, Bearbeiten und Löschen von Attributen und deren Werte
    menu_top = loadMenu()
    top = HorizontalBoxes()
    top.open_box(menu_top.menu)
    fill.body = top
    fill.set_focus('body')
    


menu_top = loadMenu()
top = HorizontalBoxes()
top.open_box(menu_top.menu)
#fill = urwid.Filler(top, valign='top', height=('relative', 100))
#fill = urwid.Frame(top)
fill = urwid.Frame(None)
fill.body = top
loop = urwid.MainLoop(fill, palette, unhandled_input=navigation)
loop.run()
