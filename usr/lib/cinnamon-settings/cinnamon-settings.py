#!/usr/bin/env python

try:
    import os
    import commands
    import sys
    import string    
    import gettext
    from gi.repository import Gio, Gtk
    from gi.repository import GdkPixbuf 
except Exception, detail:
    print detail
    sys.exit(1)


# i18n
gettext.install("cinnamon-settings", "/usr/share/cinnamon/locale")

# i18n for menu item
menuName = _("Desktop Settings")
menuGenericName = _("Desktop Configuration Tool")
menuComment = _("Fine-tune desktop settings")
                                  
class SidePage:
    def __init__(self, name, icon, content_box):        
        self.name = name
        self.icon = icon
        self.content_box = content_box
        self.widgets = []
        
    def add_widget(self, widget):
        self.widgets.append(widget)
        
    def build(self):
        # Clear all the widgets from the content box
        widgets = self.content_box.get_children()
        for widget in widgets:
            self.content_box.remove(widget)
        
        # Add our own widgets
        for widget in self.widgets:
            self.content_box.add(widget)
            self.content_box.show_all()
            
class GSettingsCheckButton(Gtk.CheckButton):    
    def __init__(self, label, schema, key):        
        self.key = key
        super(GSettingsCheckButton, self).__init__(label)
        self.settings = Gio.Settings.new(schema)        
        self.set_active(self.settings.get_boolean(self.key))
        self.settings.connect("changed::"+self.key, self.on_my_setting_changed)
        self.connect('toggled', self.on_my_value_changed)            
    
    def on_my_setting_changed(self, settings, key):
        self.set_active(self.settings.get_boolean(self.key))
        
    def on_my_value_changed(self, widget):
        self.settings.set_boolean(self.key, self.get_active())

class GSettingsEntry(Gtk.HBox):    
    def __init__(self, label, schema, key):        
        self.key = key
        super(GSettingsEntry, self).__init__()
        self.label = Gtk.Label(label)
        self.content_widget = Gtk.Entry()
        self.add(self.label)
        self.add(self.content_widget)     
        self.settings = Gio.Settings.new(schema)        
        self.content_widget.set_text(self.settings.get_string(self.key))
        self.settings.connect("changed::"+self.key, self.on_my_setting_changed)
        self.content_widget.connect('changed', self.on_my_value_changed)            
    
    def on_my_setting_changed(self, settings, key):
        self.content_widget.set_text(self.settings.get_string(self.key))
        
    def on_my_value_changed(self, widget):
        self.settings.set_string(self.key, self.content_widget.get_text())
        
class MainWindow:
  
    # Change pages
    def side_view_nav(self, side_view):
        selected_items = side_view.get_selected_items()
        if len(selected_items) > 0:
            path = selected_items[0];            
            iterator = self.store.get_iter(path)
            print self.store.get_value(iterator, 0)
            self.store.get_value(iterator,2).build()
            
    ''' Create the UI '''
    def __init__(self):        
        
        self.builder = Gtk.Builder()
        self.builder.add_from_file("/usr/lib/cinnamon-settings/cinnamon-settings.ui")
        self.window = self.builder.get_object("main_window")
        self.side_view = self.builder.get_object("side_view")
        self.content_box = self.builder.get_object("content_box")
        self.button_cancel = self.builder.get_object("button_cancel")
        
        self.window.connect("destroy", Gtk.main_quit)


        self.sidePages = []
                               
        sidePage = SidePage(_("Terminal"), "terminal", self.content_box)
        self.sidePages.append(sidePage);
                       
        sidePage = SidePage(_("Panel"), "preferences-desktop", self.content_box)
        self.sidePages.append(sidePage);
        sidePage.add_widget(GSettingsEntry(_("Menu text"), "org.cinnamon", "menu-text")) 
        sidePage.add_widget(GSettingsCheckButton(_("Auto-hide panel"), "org.cinnamon", "panel-autohide")) 
        
        sidePage = SidePage(_("Hot Corner"), "preferences-desktop", self.content_box)
        self.sidePages.append(sidePage);
        sidePage.add_widget(GSettingsCheckButton(_("Overview icon visible"), "org.cinnamon", "overview-corner-visible")) 
        sidePage.add_widget(GSettingsCheckButton(_("Overview hot corner enabled"), "org.cinnamon", "overview-corner-hover")) 
        
                                
        # create the backing store for the side nav-view.                    
        theme = Gtk.IconTheme.get_default()
        self.store = Gtk.ListStore(str, GdkPixbuf.Pixbuf, object)
        for sidePage in self.sidePages:
            img = theme.load_icon(sidePage.icon, 36, 0)                        
            self.store.append([sidePage.name, img, sidePage])     
                    
        
        # set up the side view - navigation.
        self.side_view.set_text_column(0)
        self.side_view.set_pixbuf_column(1)
        self.side_view.set_model(self.store)
        #path = self.side_view.get_path_at_pos(0,0)
        #self.side_view.select_path(path)
        self.side_view.connect("selection_changed", self.side_view_nav )

        # set up larger components.
        self.window.set_title(_("Desktop Settings"))
        self.window.connect("destroy", Gtk.main_quit)
        self.button_cancel.connect("clicked", Gtk.main_quit)                                    
        self.window.show()

  
                
if __name__ == "__main__":
    MainWindow()
    Gtk.main()
