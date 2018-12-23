import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from markdown import Markdown

class AuthorWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self,title="Author")
        
        self.set_name("mainwindow")
        
        # sets minimum size
        self.set_size_request( 600, 400 )
        
        # set up styles
        screen = Gdk.Screen.get_default()

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path('style.css')

        context = Gtk.StyleContext()
        context.add_provider_for_screen(screen, css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_USER)
        # // end setup styles
        
        
        # set up main box for holding stuff
        self.grandBox = Gtk.Box()
        self.add( self.grandBox )
        self.set_name("mainbox")
        
        # set up scrolling area
        self.scrolledWindow = Gtk.ScrolledWindow()
        self.scrolledWindow.set_hexpand(True)
        self.scrolledWindow.set_vexpand(True)
        self.scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        self.grandBox.pack_start( self.scrolledWindow, True, True, 0  )
        self.scrolledWindow.set_name('mainscroll')
        
        
        # set up initial textview
        self.textView = Gtk.TextView()
        self.textView.set_wrap_mode( Gtk.WrapMode.WORD_CHAR )
        self.scrolledWindow.add( self.textView)
        self.textView.set_name('mainview')
        self.setIndent(24)
        self.setMargin(40)
        
        # ste up markdown styler
        self.markdown = Markdown(self.textView.get_buffer())
        
        # attach working signals
        self.attachListeners()
        
        self.connect("destroy", Gtk.main_quit)
        self.show_all()

    # Set the indent overall, if we need to
    def setIndent(self, indent=-40 ):
        self.textView.set_indent( indent )
    
    # Set all the assorted margins for the page
    def setMargin(self, margin=40 ):
        self.textView.set_left_margin( margin )
        self.textView.set_right_margin( margin )
        self.textView.set_top_margin( margin )
        self.textView.set_bottom_margin( margin )
    
    # handle typewriter scrolling
    def resizeScroll(self,target,event):
        
        # first get size of window
        h = (self.get_allocation().height / 2)-16
        self.textView.set_bottom_margin( h )
        self.textView.set_top_margin( h )
        
        return
    
    # the buffer changed, run markdown styles
    def bufferChange( self, target ):
        # set up markdown handler
        self.markdown.pointUpdate()
        return
        
    
    def mouseClick( self, a, b ):
        self.typeWriterScroll()
        self.markdown.updateCurrentSentence()
        return
    
    # fire key up events, for now just typewriter scrolling
    def keyUp( self, target, event=0 ):
        self.typeWriterScroll()
        self.markdown.updateCurrentSentence()
        return
    
    # Scroll the content to where the line is
    def typeWriterScroll( self ):
        # then location of cursor
        loc = self.textView.get_cursor_locations().strong.y
        
        # now force scrollbar to that location
        self.scrolledWindow.get_vscrollbar().set_value( loc )
        
        return
        
    # attach listners and bindings to the Markdown checker
    def attachListeners(self):
        self.connect("configure-event",self.resizeScroll)
        self.textView.get_buffer().connect("changed",self.bufferChange)
        self.textView.connect("key-release-event", self.keyUp)
        self.textView.connect("button-release-event", self.mouseClick)
        return
