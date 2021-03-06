from tkinter import *
from tkinter import font

class App:

    def __init__(self, master):

        #Our main frame, containing everything.
        self.frame = Frame(
            master,
            width    = 1024,
            height   = 768,
            bg       = "#303030",
            colormap = "new"
        )
        self.frame.pack()

        #temporary
        self.frame.pack_propagate(0)

        #Our toolbar, holding all our buttons.
        toolbar = Frame(
            self.frame,
            bg="#303030"
        )
        toolbar.pack(side=BOTTOM)

        #Button that leads to our magnet dialog.
        self.magnet_button = Button(
            toolbar,
            text               = "Magnet",
            fg                 = "white",
            bg                 = "#1d8fc9",
            font               = "ubuntu",
            relief             = "flat",
            activebackground   = "#4cb3e6",
            activeforeground   = "white",
            highlightthickness = 0,
            width              = 10,
            command            = self.open_dialog
        )
        self.magnet_button.pack(side=LEFT, padx=5, pady=10)

        #Button that toggles fullscreen.
        self.fullscreen_button = Button(
            toolbar,
            text               = "Fullscreen",
            fg                 = "white",
            bg                 = "#1d8fc9",
            font               = "ubuntu",
            relief             = "flat",
            activebackground   = "#4cb3e6",
            activeforeground   = "white",
            highlightthickness = 0,
            width              = 10,
            command            = self.show_fullscreen
        )
        self.fullscreen_button.pack(side=RIGHT, padx=5, pady=10)

    def open_dialog(self):

        #The dialog window.
        magnet_dialog = self.magnet_dialog = Toplevel(
            self.frame,
            bg="#303030"
        )

        #The white text.
        label = Label(
            magnet_dialog,
            text = "Magnet link:",
            fg   = "white",
            bg   = "#303030",
            font = "ubuntu",
        )
        label.pack(pady=8)

        #The text box.
        self.magnet_entry = Entry(
            magnet_dialog,
            fg                 = "white",
            bg                 = "#101010",
            font               = "ubuntu",
            relief             = "flat",
            insertbackground   = "white",
            highlightthickness = 0,
            width              = 50
        )
        self.magnet_entry.pack(padx=10)

        #The button.
        stream_button = Button(
            magnet_dialog,
            text               = "Stream",
            fg                 = "white",
            bg                 = "#1d8fc9",
            font               = "ubuntu",
            relief             = "flat",
            activebackground   = "#4cb3e6",
            activeforeground   = "white",
            highlightthickness = 0,
            width              = 10,
            command            = self.ok
        )
        stream_button.pack(pady=10)

    def show_fullscreen(self):
        print("Fullscreen Mode")
        root.maxsize()

    def ok(self):
        print("Magnet link: ", self.magnet_entry.get())
        self.magnet_dialog.destroy()

root = Tk()
root.title("Streamer")
print(font.families())
#root.resizable(width=False, height=False)
#root.geometry("1024x768")
app = App(root)

root.mainloop()
#root.destroy() # optional; see description below