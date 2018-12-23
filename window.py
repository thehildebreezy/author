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
        
        # useful for saved or not
        self.docPath = None
        
        self.modified = False
        
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


    # update window title
    def updateTitle( self ):
        if self.docPath:
            title_path = self.docPath
        else:
            title_path = "Author"
        if self.modified:
            title_path += "*"
        self.set_title( title_path )
        return

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
        self.modified = True
        self.updateTitle()
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
    
    # keyboard shortcuts
    def keyShortCuts( self, target, event ):
        if event.get_state() & Gdk.ModifierType.CONTROL_MASK:
            keyval = Gdk.keyval_name( event.keyval )
            if keyval == 'o':
                self.open_doc()
            elif keyval == 's':
                self.save_doc()
        return
    
    # Scroll the content to where the line is
    def typeWriterScroll( self ):
        # then location of cursor
        loc = self.textView.get_cursor_locations().strong.y
        
        # now force scrollbar to that location
        self.scrolledWindow.get_vscrollbar().set_value( loc )
        
        return
    
    def open_doc( self ):
        dialog = Gtk.FileChooserDialog("Open document", self,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            docPath = dialog.get_filename()
            try:
                f = open(docPath, 'r')
                buf = self.textView.get_buffer()
                buf.set_text( f.read() )
                self.markdown.styleDoc()
                self.docPath = docPath
                self.modified = False
            except SomeError as err:
                print('Could not read %s: %s' % (docPath, err))

        dialog.destroy()
        
        self.updateTitle()
        
        return
        
    def save_doc( self ):
        docPath = None
        if self.docPath:
            docPath = self.docPath
        else:
            dialog = Gtk.FileChooserDialog("Save document", self,
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

            filter_any = Gtk.FileFilter()
            filter_any.set_name("Any files")
            filter_any.add_pattern("*")
            dialog.add_filter(filter_any)

            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                docPath = dialog.get_filename()
            else:
                docPath = None

            dialog.destroy()
        
        if docPath:
            buff = self.textView.get_buffer()
            text = buff.get_text( buff.get_start_iter(), buff.get_end_iter(), False)
            try:
                open(docPath, 'w').write(text)
                self.docPath = docPath
                self.modified = False
            except SomeError as err:
                print('Could not save %s: %s' % (docPath, err))
        
        self.updateTitle()
        
        return
    
    # attach listners and bindings to the Markdown checker
    def attachListeners(self):
        self.connect("configure-event",self.resizeScroll)
        self.textView.get_buffer().connect("changed",self.bufferChange)
        self.textView.connect("key-release-event", self.keyUp)
        self.textView.connect("button-release-event", self.mouseClick)
        
        # open / close
        self.connect("key-release-event", self.keyShortCuts)
        
        return
