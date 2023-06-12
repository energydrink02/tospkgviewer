import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, simpledialog
from PIL import ImageTk
import os
import sys
import io
import PKG as PKG
import traceback
import texture as texture
from Helper import convert_size

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.geometry("900x700")
        self.parent.resizable(False, False)
        self.parent.title("Truth or Square PKG Editor")
        self.parent.iconbitmap(default=resource_path("coralanemone.ico"))

        s=ttk.Style()
        s.configure('Treeview', rowheight=18)

        self.tree = ttk.Treeview(self.parent, height=37)
        self.tree["columns"] = ("Name", "Size", "Size (Compressed)", "Type")
        self.tree.column("#0", anchor="w", width=50)
        self.tree.column("Name", anchor="w", width=300)
        self.tree.column("Size", anchor="center", width=110)
        self.tree.column("Size (Compressed)", anchor="center", width=110)
        self.tree.column("Type", anchor="center", width=100)

        self.tree.heading("#0", text="#")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Size", text="Size")
        self.tree.heading("Size (Compressed)", text="Size (Compressed)")
        self.tree.heading("Type", text="Type")

        self.tree.place(x=5, y=0)

        self.tree.bind("<Button-3>", self.onRightclick)
        self.tree.bind("<<TreeviewSelect>>", self.onTreeviewSelect)
        self.tree.bind("<Delete>", self.onDelete)
        self.tree.bind("<Double-Button-1>", self.onDouble)

        self.vsb = ttk.Scrollbar(self.parent, orient="vertical", command=self.tree.yview)
        self.vsb.place(x=680, y=0, height=700)
        self.tree.configure(yscrollcommand=self.vsb.set)

        # PKG Information Frame
        self.pkgInfoFrame = tk.LabelFrame(self.parent, text="PKG Information")
        self.pkgInfoFrame.place(x=700, y=570, height=100, width=180)

        self.pkgSizeDecompressedLabel = tk.Label(self.pkgInfoFrame)
        self.pkgSizeDecompressedLabel.pack(anchor="w")

        self.pkgSizeCompressedLabel = tk.Label(self.pkgInfoFrame)
        self.pkgSizeCompressedLabel.pack(anchor="w")

        self.pkgAmountEntriesLabel = tk.Label(self.pkgInfoFrame)
        self.pkgAmountEntriesLabel.pack(anchor="w")

        # Texture Preview Frame
        self.textureMainFrame = tk.LabelFrame(self.parent, text="Texture")
        self.textureMainFrame.place(x=705, y=0, height=250, width=180)

        self.texturePreviewFrame = tk.LabelFrame(self.textureMainFrame, text="Preview (128x128)")
        self.texturePreviewFrame.place(x=13, y=0, height=160, width=150)

        self.texturePreviewLabel = tk.Label(self.texturePreviewFrame)
        self.texturePreviewLabel.pack()

        self.textureOrigSizeStr = tk.StringVar()
        self.textureOrigSizeLabel = tk.Label(self.textureMainFrame, textvariable=self.textureOrigSizeStr, fg="gray", font=("Arial", 7))
        self.textureOrigSizeLabel.place(x=5, y=160)

        self.texturePaletteFormatStr = tk.StringVar()
        self.texturePaletteFormatLabel = tk.Label(self.textureMainFrame, textvariable=self.texturePaletteFormatStr, fg="gray", font=("Arial", 7))
        self.texturePaletteFormatLabel.place(x=105, y=160)

        self.exportTextureButton = tk.Button(self.textureMainFrame, text="Export Image as PNG", command= lambda: textureClass.exportTexture(filedialog.asksaveasfilename(initialfile=tree_name.split(".")[0], defaultextension=".png", filetypes=[("PNG", "*.png"),])))
        self.exportTextureButton.place(x=13, y=185, width=150)
        self.exportTextureButton.config(state="disabled")

        # Menu
        self.menu =tk.Menu(self.parent)
        self.parent.config(menu=self.menu)

        self.file_menu = tk.Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open", command=self.get_directory)
        self.file_menu.add_command(label="Save", command=self.save)
        self.file_menu.add_command(label="Save as...", command=lambda: self.save(True))

        self.tools_menu = tk.Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label="Tools", menu=self.tools_menu)
        self.tools_menu.add_command(label="Export all", command=self.exportAll)

        # Rightclick Menu
        self.rightclick_menu = tk.Menu(self.parent, tearoff=False)
        self.rightclick_menu.add_command(label="Export", command=self.export)
        self.rightclick_menu.add_command(label="Replace", command=self.replaceAsset)
        self.rightclick_menu.add_command(label="Rename", command=self.renameAsset)
        self.rightclick_menu.add_command(label="Delete", background="#FFAAA9", command=self.deleteAsset)

        self.pkg = None
 
    def onRightclick(self, event):
        if self.pkg == None: return
        self.rightclick_menu.tk_popup(event.x_root, event.y_root)

    def onDelete(self, event):
        if self.pkg == None: return
        if not self.tree.focus(): return
        self.deleteAsset()

    def onDouble(self, event):
        if self.pkg == None: return
        if not self.tree.focus(): return
        self.renameAsset()

    def onTreeviewSelect(self, event):
        if self.pkg == None: return

        global tree_tags, tree_name
        try:
            tree_tags = self.tree.item(self.tree.focus())["tags"]
            tree_name = self.tree.item(self.tree.focus())["values"][0]
        except:
            return

        if tree_name.endswith("rtf"): # Texture
            self.loadTexture()
        else:
            self.noneTexture()
        return

    # # # # # # # # # # # # # # # # # # # #

    def deleteAsset(self):
        askDelete = tk.messagebox.askyesno("Delete Asset", "Are you sure that you want to delete this asset?", icon="warning")
        if askDelete:
            self.pkg.assets.pop(tree_tags[0])
            self.pkg.Update()
            self.update_tree()
        return

    def renameAsset(self):
        newName = simpledialog.askstring("New Name", "Enter new Name (without extension):\t\t")
        if newName == None: return
        if len(newName) > 28:
            tk.messagebox.showerror("Error", f"Name is too long. Characters: {len(newName)}, Expected: <= 28")
            return
        self.pkg.assets[tree_tags[0]].name = newName + tree_name[-4:]

        self.update_tree()

    def replaceAsset(self):
        openfile = str(self.openFileDialog())
        if openfile == "": return
        compress = tk.messagebox.askyesno("Compress Asset", "Do you want to compress the Asset?")

        try:
            self.pkg.assets[tree_tags[0]].Update(open(openfile, "rb").read(), compress)
            self.pkg.Update()
            self.update_tree()
        except Exception as e:
            tk.messagebox.showerror(type(e).__name__, e)
        else:
            self.tree.tag_configure(tree_tags[0], background="#ba1300")
    
    # # # # # # # # # # # # # # # # # # # #

    def loadTexture(self):
        global textureClass
        try:
            textureClass = texture.Texture(io.BytesIO(self.getData()))

            self.texturePreview = ImageTk.PhotoImage(textureClass.image.resize((128,128)))
            self.texturePreviewLabel.configure(image=self.texturePreview, text="")
            self.texturePreviewLabel.image = self.texturePreview
        except:
            self.noneTexture("Unsupported Texture")
        else:
            self.textureOrigSizeStr.set(f"Texture Size: {textureClass.width}x{textureClass.height}")
            self.texturePaletteFormatStr.set(textureClass.paletteFormat)
            self.exportTextureButton.config(state="active")
        
    def noneTexture(self, textStr=""):
        self.texturePreviewLabel.configure(image="", text=textStr)
        for x in [self.textureOrigSizeStr, self.texturePaletteFormatStr]:
            x.set("")
        self.exportTextureButton.config(state="disabled")

    # # # # # # # # # # # # # # # # # # # #

    def getData(self):
        return self.pkg.assets[tree_tags[0]].getData()

    def export(self):
        directory = filedialog.askdirectory()
        if directory == "": return

        with open(directory + "/" + tree_name, "wb") as file:
            file.write(self.getData())

    def exportAll(self):
        if self.pkg == None: return

        directory = filedialog.askdirectory()
        if directory == "": return

        try:
            for asset in self.pkg.assets:
                with open(directory + "/" + asset.name, "wb") as file:
                    file.write(asset.getData())
        except Exception as e:
            tk.messagebos.showerror(type(e).__name__, traceback.format_exc())
        else:
            tk.messagebox.showinfo("Success!", "All files exported")

    def save(self, askDir=False):
        if self.pkg == None: return

        try:
            self.pkg.Update()
            if askDir:
                directory = filedialog.asksaveasfile(mode="wb", defaultextension=".pkg", filetypes=[("PKG", "*.pkg")])
                if directory == None: return
                self.pkg.save_as(directory)
            else:
                self.pkg.save()
            self.update_tree()
        except Exception as e:
            tk.messagebox.showerror(type(e).__name__, traceback.format_exc())
        else:
            tk.messagebox.showinfo("Success!", "File Saved")

    def update_tree(self):
        self.tree.delete(*self.tree.get_children())
        #self.tree.yview_moveto(0)

        self.pkgSizeCompressedLabel["text"] = f"Size (Compressed): {convert_size(self.pkg.totalSizeCompressed)}"
        self.pkgSizeDecompressedLabel["text"] = f"Size: {convert_size(self.pkg.totalSizeUncompressed)}"
        self.pkgAmountEntriesLabel["text"] = f"Entries: {str(self.pkg.amountAssets)}"

        for index, asset in enumerate(self.pkg.assets):
            self.tree.insert(parent="", index="end", iid=index, text=index, values=(asset.name, convert_size(asset.uncompressedSize), convert_size(asset.compressedSize), PKG.assettype.get(asset.name[-3:], " ")), tags=(index))
            self.tree.tag_configure(index, background="#ffffff")

    def openFileDialog(self, types=("*", "*.*")):
        return str(filedialog.askopenfilename(filetypes=[types]))

    def get_directory(self):
        self.directory = self.openFileDialog(("ToS PKG", "*.pkg"))
        if self.directory == "": return

        try:
            self.pkg = PKG.PKGHeader(open(self.directory, "rb"))
        except Exception as e:
            tk.messagebox.showerror(type(e).__name__, traceback.format_exc())
        else:
            self.parent.title(f"Truth or Square PKG Editor [{self.directory}]")
            self.update_tree()

if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()