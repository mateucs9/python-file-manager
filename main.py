import time
import tkinter as tk
import os
from tkinter import ALL, PhotoImage, ttk
from PIL import Image, ImageTk
import threading

class FileManager(tk.Tk):
    def __init__(self, path):
        # Main frame configuration
        tk.Tk.__init__(self)
        self.title('File Manager by SM')
        self.width = 900
        self.height = 600
        self.geometry('{}x{}'.format(self.width, self.height))
        self.config(bg='white')

        # Class variables
        self.icon_size = 20
        self.path = path
        self.image_files = os.listdir('icons')
        self.ext_dict = {
            'txt': 'notebook.png',
            'doc': 'notebook.png',
            'docx': 'notebook.png',
            'pdf': 'pdf.png',
            'xls': 'excel.png',
            'xlsx': 'excel.png',
            '': 'folder.png',
            'other': 'file.png'
        }
        self.not_allowed = ['.', '+', '$']
        self.large_font = ('Calibri', 36, )
        self.medium_font = ('Calibri', 24,)
        self.small_font = ('Calibri', 12, )
        self.size_dict = {}
        self.timer_id = None

        # Loading content
        self.load_images('icons/')
        self.start_loading()

    def get_widgets(self):
        self.header_frame = tk.Frame(self, bg='beige')
        self.header_frame.pack(side='top', fill='x')
        tk.Label(self.header_frame, text='Current path: '+self.path,
                 font=self.medium_font, bg='beige').pack(anchor='w')

        # Creating canvas and scrollbar
        self.canvas = tk.Canvas(self, bg='white')
        self.canvas.pack(side='left', fill='both', expand=True)

        self.scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.scrollbar.pack(side='right', fill='both')
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox(ALL)), '+')
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel, '+')

        # We create a frame that we will use from now on as main frame
        self.frame = tk.Frame(self.canvas, bg='white')
        self.canvas.create_window((0, 0), window=self.frame, anchor='nw')

        # Listing all directories and files in path
        self.labels = []
        row = 0
        for file in self.files:
            if file['name'][0] not in self.not_allowed:
                self.labels.append(tk.Label(self.frame, text=file['name'], name=file['short_name'], image=file['image'], compound='left', bg='white'))
                self.labels[row].grid(row=row, column=0, sticky='w')
                try:
                    self.labels[row].bind("<Enter>", self.link_on_enter, '+')
                    self.labels[row].bind("<Leave>", self.link_on_leave, '+')
                    self.labels[row].bind("<Button-1>", lambda e, self=self: self.change_path(e), '+')
                    tk.Label(self.frame, text=file['size'], bg='white').grid(row=row, column=1, sticky='w', padx=20)
                    row += 1
                except: 
                    continue

    def load_images(self, path):
        self.images = {}
        for ext in self.ext_dict.keys():
            image = ''
            if ext in self.ext_dict.keys():
                image = path+self.ext_dict[ext]
            else:
                image = path+'file.png'
            self.images[ext] = ImageTk.PhotoImage(Image.open(image).resize(
                (self.icon_size, self.icon_size), Image.ANTIALIAS))

    def get_image(self, ext):
        if ext in self.images.keys():
            return self.images[ext]
        else:
            return self.images['other']

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), 'units')

    def get_size(self, size, path):
        ext = os.path.splitext(path)[1].replace('.', '')
        if ext != '':
            return os.path.getsize(path)
        try:
            for file in os.listdir(path):
                self.files_analyzed += 1
                if file[0] not in self.not_allowed:
                    try:
                        file_path = path+'\\'+file
                        if file_path in self.size_dict.keys():
                            size += self.size_dict[file_path]
                        else:
                            if ext == '':
                                new_size = self.get_size(0, file_path)
                                self.size_dict[path] = new_size
                                size += new_size
                            else:
                                new_size = os.path.getsize(file_path)
                                self.size_dict[path] = new_size
                                size += new_size
                    except:
                        continue
        except:
            pass
        
        return size

    def get_size_str(self, size):
        if size < 1024:
            return f"{size} bytes"
        elif size < 1024*1024:
            return f"{round(size/1024, 0)} KB"
        elif size < 1024*1024*1024:
            return f"{round(size/(1024*1024), 1)} MB"
        elif size < 1024*1024*1024*1024:
            return f"{round(size/(1024*1024*1024), 2)} GB"

    def link_on_enter(self, e):
        e.widget['foreground'] = 'blue'
        e.widget['cursor'] = 'hand1'

    def link_on_leave(self, e):
        e.widget['foreground'] = 'black'

    def change_path(self, e):
        self.path = list(filter(
            lambda file: file['short_name'] == e.widget._name, self.files))[0]['path']
        self.start_loading()

    def load_files(self):
        self.loading_running = True

        size_dict = {}
        files = []
        for file in os.listdir(self.path):
            ext = os.path.splitext(file)[1].replace('.', '')
            path = self.path+'\\'+file
            size = self.get_size(0, path)
            short_name = '$'.join(file.split(' ')).replace('.', '#').lower()
            
            size_dict[path] = size
            files.append({
                'name': '   '+file,
                'short_name': short_name,
                'ext': ext,
                'path': path,
                'image': self.get_image(ext),
                'size': self.get_size_str(size),
                'size_bytes': size
            })


        self.files = sorted(files, key=lambda d: -d['size_bytes'])
       
        self.files.insert(0, {
            'name': '   /',
            'short_name': '/',
            'ext': '',
            'path': '\\'.join(self.path.split('\\')[:-1]),
            'image': self.get_image(''),
            'size': self.get_size_str(0),
            'size_bytes': 0
        })
        self.size_dict = self.size_dict | size_dict

        self.loading_running=False
    
    def clear_screen(self):
        if len(self.winfo_children()) > 0:
            children = self.winfo_children()
            for widget in children:
                try:
                    widget.destroy()
                except:
                    pass

    def start_loading(self):
        self.files_analyzed = 0
        self.t1 = threading.Thread(group=None, target=self.load_files)
        self.t1.setDaemon(True)
        self.t1.start()

        self.clear_screen()
        
        tk.Label(self, text='Loading', font=self.large_font, bg='white').pack(anchor='n')
        self.loading_canvas = tk.Canvas(self, width=self.width, height=self.height, bg='white')
        self.loading_canvas.pack()
        
        gif_path = os.getcwd()+'/loading'
        image_list = os.listdir(gif_path)
        
        giflist = [PhotoImage(file=gif_path+'/'+img) for img in image_list]
        for i in range(10000):
            for gif in giflist:
                if not self.loading_running:
                    self.clear_screen()
                    self.get_widgets()
                    return
                try:
                    self.loading_canvas.delete(text)
                except:
                    pass
                self.loading_canvas.create_image(self.width//2, self.height//2-75, image=gif, anchor='center')
                text = self.loading_canvas.create_text(self.width//2, self.height//2+50, text="{:,.0f} files analyzed".format(self.files_analyzed), fill='black', anchor='center')
                self.loading_canvas.update()
                time.sleep(0.1)


if __name__ == '__main__':
    path = r'C:\\'
    app = FileManager(path)
    app.mainloop()
