import tkinter
from tkinter import messagebox as mb
from tkinter import scrolledtext as st
from tkinter import simpledialog as sd
import client
import server
import sys


port_num_default = 10000


class LANChat(tkinter.Frame):
    def __init__(self, master=None):
        global port_num_default
        
        master.wm_title("CHATTY")
        master.protocol("WM_DELETE_WINDOW", self.close)
        
        tkinter.Frame.__init__(self, master)
        self.pack(fill=tkinter.BOTH, expand=1)
        self.widget()
        
        if mb.askyesno("", "Are you the server host?"):
            self.chat = server.Server(port_num_default)
            self.entryIP.delete(0, tkinter.END)
            self.entryIP.insert(0, self.chat.host_ip)
            self.entryIP.config(state='readonly')
            self.entryIP.bind('<FocusIn>', self.removePortLabel)
            self.entryPort.delete(0, tkinter.END)
            self.entryPort.insert(0, self.chat.host_port)
            self.entryPort.config(state='readonly')
            self.entryPort.bind('<FocusIn>', self.removePortLabel)
            self.hostLabelPort.pack(side=tkinter.LEFT)
        else:
            self.chat = None
            self.buttonConnect.pack(side=tkinter.LEFT)

        master.bind('<Return>', self.messageSend)
        master.bind('<KP_Enter>', self.messageSend)
        self.displayNewMessage()

    def hostConnection(host):
        hostNumIp = host.entryIP.get()
        if not host.ipChecker(hostNumIp):
            host.systemMessage("The IP number format is incorrect...")
            return

        portNum = host.entryPort.get()

        if not host.portChecker(portNum):
            msg = "The port number must be between 1024 and 65535"
            host.systemMessage(msg)
            return
  
        try:
            host.chat = client.Client(hostNumIp, int(portNum))
            host.buttonConnect.pack_forget()
            host.entryIP.config(state='readonly')
            host.entryPort.config(state='readonly')
        except Exception as e:
            msg = "Exception with IP/Port---investigate host process firewall settings"
            host.systemMessage(repr(e) + '\n' + msg)
   
    def ipChecker(none, ip):
        ipSections = ip.split('.')
        if len(ipSections) != 4:
            return False

        for part in ipSections:
            try:
                part = int(part)
                if part < 0 or part > 255:
                    return False
            except:
                return False
        return True

    def portChecker(none, port):
        try:
            port = int(port)
            if port > 1024 and port <= 65535:
                return True
            return False
        except:
            return False

    def widget(self):
        global port_num_default

        menubar = tkinter.Menu(self) #menu
        menu = tkinter.Menu(menubar, tearoff=0)
        menu.add_command(label="Change user name" , command=self.newNamePrompt)
        menu.add_separator()
        menu.add_command(label="Exit", command=self.close)
        menubar.add_cascade(label="Menu", menu=menu)
        self.master.config(menu=menubar)
        #frame ip/port
        portframeIP = tkinter.Frame(self, relief=tkinter.RAISED, bd=1) 
        portframeIP.pack(side=tkinter.TOP, fill=tkinter.X)
        #ip
        frameIP = tkinter.Frame(portframeIP)
        frameIP.pack(side=tkinter.LEFT)
        
        labelIP = tkinter.Label(frameIP, text="ip:")
        labelIP.pack(side=tkinter.LEFT)
       
        vcmd = (self.register(self.entryChecker), '%P', '%W')
       
        maxLengthIP = 15
        entryIP = tkinter.Entry(frameIP, width=maxLengthIP, validate='key', vcmd=vcmd)
        entryIP.pack(side=tkinter.LEFT)
        entryIP.insert(0, '') 
        self.entryIP = entryIP
        #port
        framePort = tkinter.Frame(portframeIP)
        framePort.pack(side=tkinter.LEFT)

        labelPort = tkinter.Label(framePort, text="port:")
        labelPort.pack(side=tkinter.LEFT)

        maxLengthPort = 5
        entryPort = tkinter.Entry(framePort, width=maxLengthPort, validate='key', vcmd=vcmd)
        entryPort.pack(side=tkinter.LEFT)
        entryPort.insert(0, port_num_default)
        self.entryPort = entryPort

        #Label for host port
        self.hostLabelPort = tkinter.Label(portframeIP, text="Host Port Number")
       
        frameMessage = tkinter.Frame(self)
        frameMessage.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        windowMessage = st.ScrolledText(frameMessage, height=10, width=80)
        windowMessage.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
        windowMessage.config(state=tkinter.DISABLED)
        self.windowMessage = windowMessage

        # msg entry frame
        frameMessageEntry = tkinter.Frame(frameMessage, relief=tkinter.RAISED, bd=1)
        frameMessageEntry.pack(side=tkinter.BOTTOM, fill=tkinter.X)

        entryMessage = tkinter.Entry(frameMessageEntry)
        entryMessage.pack(side=tkinter.LEFT, fill=tkinter.X, expand=1)
        entryMessage.focus()
        self.entryMessage = entryMessage
        
        sendButton = tkinter.Button(frameMessageEntry)
        sendButton["text"] = "Send"
        sendButton["command"] = self.messageSend
        sendButton.pack(side=tkinter.RIGHT)
        #client
        buttonConnect = tkinter.Button(portframeIP)
        buttonConnect["text"] = "Connect"
        buttonConnect["command"] = self.hostConnection
        self.buttonConnect = buttonConnect

        master = self.master
        master.update()
        tempMenuNum = 30
        minHeight = master.winfo_height() + tempMenuNum
        master.minsize(master.winfo_width(), minHeight)

    def removePortLabel(self, event=None):
        if self.hostLabelPort is not None:
            self.hostLabelPort.pack_forget()
            self.hostLabelPort = None

    def newNamePrompt(self):
        newName = sd.askstring("Name Change", "New name")
        if newName is not None:
            self.nameChangeRequest(newName)

    def nameChangeRequest(self, newName):
        if self.chat is not None:
            self.chat.messageSend("/NC- " + newName)
        else:
            self.systemMessage("A name change is not permitted until host connection has been established")

    def displayNewMessage(self):
        if self.chat is not None:
            messages = self.chat.get_new_msgs()
            for msg in messages:
                self.displayMessage(msg)
        self.master.after(1000, self.displayNewMessage)

    def displayMessage(self, message):
        self.windowMessage.config(state=tkinter.NORMAL)
        self.windowMessage.insert(tkinter.END, "%s\n" % message)
        self.windowMessage.yview(tkinter.END)
        self.windowMessage.config(state=tkinter.DISABLED)

    def messageSend(self, event=None):
        if self.chat is not None:
            message = self.entryMessage.get()
            self.entryMessage.delete(0, tkinter.END)
            self.chat.messageSend(message)

    def entryChecker(self, first, last):
        entry = self.master.nametowidget(last)
        if len(first) <= entry['width']:
            return True
        self.bell()
        return False
    
    def systemMessage(self, message):
        if not message:
            return

        message = "SYSTEM: " + message + "."
        self.displayMessage(message)

    def close(self):
        if self.chat is not None:
            self.chat.destroy()
        root.destroy()
    
root = tkinter.Tk()
chatty = LANChat(master=root)
chatty.mainloop()

