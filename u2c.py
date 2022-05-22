from burp import IBurpExtender
from burp import IMessageEditorTabFactory
from burp import IMessageEditorTab

import re

class BurpExtender(IBurpExtender, IMessageEditorTabFactory):
    
    #
    # implement IBurpExtender
    #
    
    def	registerExtenderCallbacks(self, callbacks):
        # keep a reference to our callbacks object
        self._callbacks = callbacks
        
        # obtain an extension helpers object
        self._helpers = callbacks.getHelpers()
        
        # set our extension name
        callbacks.setExtensionName("U2C")
        
        # register ourselves as a message editor tab factory
        callbacks.registerMessageEditorTabFactory(self)
        
    # 
    # implement IMessageEditorTabFactory
    #
    
    def createNewInstance(self, controller, editable):
        # create a new instance of our custom editor tab
        return U2CTab(self, controller, False)
        
# 
# class implementing IMessageEditorTab
#

class U2CTab(IMessageEditorTab):
    def __init__(self, extender, controller, editable):
        self._extender = extender
        self._editable = editable
        
        # create an instance of Burp's text editor, to display our u2c data
        self._txtInput = extender._callbacks.createTextEditor()
        self._txtInput.setEditable(editable)
        
    #
    # implement IMessageEditorTab
    #

    def getTabCaption(self):
        return "U2C"
        
    def getUiComponent(self):
        return self._txtInput.getComponent()
        
    def isEnabled(self, content, isRequest):
        # Check response if containing unicode character
        contentStr = self._extender._helpers.bytesToString(content)
        regexp = re.compile(r'\\u[a-z0-9]{4}')
        existsUnicode = regexp.search(contentStr.lower())
        return (not isRequest) and existsUnicode
        
    def setMessage(self, content, isRequest):
        if content is None:
            # clear our display
            self._txtInput.setText(None)
            self._txtInput.setEditable(False)
        
        else:
            # Convert Unicode to Chinese
            contentStr = self._extender._helpers.bytesToString(content)
            self._txtInput.setText(
                self._extender._helpers.stringToBytes(
                    contentStr.decode('unicode-escape').encode('utf-8')
                )
            )
            self._txtInput.setEditable(self._editable)
        
        # remember the displayed content
        self._currentMessage = content
    
    def getMessage(self):
        # don't change the original response
        return self._currentMessage
    
    def isModified(self):
        return False
    
    def getSelectedData(self):
        return self._txtInput.getSelectedText()
