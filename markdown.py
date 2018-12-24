import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango

class Markdown:

    def __init__(self, textBuffer):
        #define some stuff
        self.textBuffer = textBuffer
        
        # create tags
        
        # tags we will be using here
        self.headTag = self.textBuffer.create_tag( "heading", weight=Pango.Weight.BOLD, left_margin=26)
        self.boldTag = self.textBuffer.create_tag( "bold", weight=Pango.Weight.BOLD )
        self.italTag = self.textBuffer.create_tag( "italic", style=Pango.Style.ITALIC )
        self.undrTag = self.textBuffer.create_tag( "underline", underline = Pango.Underline.SINGLE )
        self.currTag = self.textBuffer.create_tag( "currentline", foreground = "#333" )
        
        return
    
    def pointUpdate( self ):
        self.styleLine()
        self.updateCurrentSentence()
        return
    
    def styleScope(self, start, end):
        
        # might as well clear all of our tags out of here
        self.textBuffer.remove_all_tags(start,end)
        
        self.applyTags("*", self.boldTag, start, end )
        self.applyTags("/", self.italTag, start, end )
        self.applyTags("_", self.undrTag, start, end )
        self.applyHead("#", self.headTag, start, end )
            
        return
    
    # apply headed tags
    def applyHead(self, search, tag, start, end):
        
        start = self.textBuffer.get_iter_at_offset( start.get_offset() )
        end = self.textBuffer.get_iter_at_offset( end.get_offset() )
        end.forward_to_line_end()
        
        self.textBuffer.remove_tag( tag, start, end )
        
        next = self.textBuffer.get_iter_at_offset( start.get_offset() )
        next.forward_char()
        
        text = self.textBuffer.get_text(start, next,True)
        
        if text == "#":
            self.textBuffer.apply_tag( tag, start, end )
        return
    
    # apply styled tags
    def applyTags(self, search, tag, start, end):
        
        start = self.textBuffer.get_iter_at_offset( start.get_offset() )
        end = self.textBuffer.get_iter_at_offset( end.get_offset() )
        
        self.textBuffer.remove_tag( tag, start, end )
        
        # start the loop which will find the flags we're looking for
        result = start.forward_search( search, Gtk.TextSearchFlags.TEXT_ONLY, end)
        
        # while there are still matches
        while result:
            # find the corresponding tag later on
            next = result[1].forward_search(search, Gtk.TextSearchFlags.TEXT_ONLY, end)
            if next: # if we found a match
                # apply the tag and set the start search to the end of thsi tag
                self.textBuffer.apply_tag( tag, result[0], next[1] )
                start = next[1]
            else:
                # otherwise just we're just going to end it
                start = end
            
            # start searching again where we left off
            result = start.forward_search( search, Gtk.TextSearchFlags.TEXT_ONLY, end)
        
        return
    
    # Style the entire document
    def styleDoc(self):
    
        start = self.textBuffer.get_start_iter()
        end   = self.textBuffer.get_end_iter()
        
        # loop over lines
        while start.get_offset() != end.get_offset():        
            self.styleLine( start )
            start.forward_line()
        
        return
        
    
    # highlight the current sentence
    def updateCurrentSentence( self ):
        
        # first clear currentline
        lineIter = self.textBuffer.get_iter_at_offset( 
            self.textBuffer.props.cursor_position
        )
        
        # if its not already the current sentence
        if not lineIter.has_tag( self.currTag ):
            # remove all currTag instances
            self.textBuffer.remove_tag( self.currTag,
                self.textBuffer.get_start_iter(),
                self.textBuffer.get_end_iter()
            )
            
            # start a new tag, find out where the sentence begins and ends
            if lineIter.ends_line():
                endIter = self.textBuffer.get_iter_at_offset( lineIter.get_offset() )
                lineIter.backward_sentence_starts(1)
            else:
                if not lineIter.ends_sentence():
                    lineIter.forward_sentence_end()
                
                endIter = self.textBuffer.get_iter_at_offset( lineIter.get_offset() )
                
                lineIter.backward_sentence_start()
            
            self.textBuffer.apply_tag( self.currTag, lineIter, endIter )
            
        return
    
    
    # styles the currently selected line
    def styleLine(self, start=None):
    
        if start:
            lineIter = start
        else:
            # get cursor location
            lineIter = self.textBuffer.get_iter_at_offset( 
                self.textBuffer.props.cursor_position
            )
        
        endIter = 0
            
        if not lineIter.ends_line():
            lineIter.forward_to_line_end()
        
        endIter = self.textBuffer.get_iter_at_offset( lineIter.get_offset() )
        
        lineIter.set_line( lineIter.get_line() )
        
        
        self.styleScope( lineIter, endIter )
        
        return
