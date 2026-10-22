"""LionCut Studio 0.1 - Windows video editor starter."""
import json
import shutil
import subprocess
import tempfile
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk, filedialog, messagebox

FORMATS=[("Video files","*.mp4 *.mov *.mkv *.avi *.webm"),("All files","*.*")]

def command(name,*args):
    executable=shutil.which(name)
    if not executable:
        raise RuntimeError(f"{name} topilmadi. FFmpeg/FFprobe ni PATH ga qo'shing.")
    p=subprocess.run([executable,*map(str,args)],capture_output=True,text=True,
                     creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
    if p.returncode: raise RuntimeError(p.stderr[-1500:] or f"{name} xatosi")
    return p.stdout.strip()

def duration(path):
    return float(command("ffprobe","-v","error","-show_entries","format=duration",
                         "-of","default=noprint_wrappers=1:nokey=1",path))

class LionCut(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LionCut Studio 0.1")
        self.geometry("1050x650")
        self.clips=[]
        self.busy=False
        self.preview_image=None
        style=ttk.Style(self)
        style.theme_use("clam")
        toolbar=ttk.Frame(self,padding=10)
        toolbar.pack(fill="x")
        for title,fn in [("Video qo'shish",self.add),("Yuqoriga",lambda:self.move(-1)),
                         ("Pastga",lambda:self.move(1)),("O'chirish",self.remove),
                         ("Saqlash",self.save),("Ochish",self.load),("MP4 eksport",self.export)]:
            ttk.Button(toolbar,text=title,command=fn).pack(side="left",padx=3)
        pane=ttk.Panedwindow(self,orient="horizontal")
        pane.pack(fill="both",expand=True,padx=12,pady=10)
        left,right=ttk.Frame(pane),ttk.Frame(pane,padding=10)
        pane.add(left,weight=3);pane.add(right,weight=2)
        self.tree=ttk.Treeview(left,columns=("file","start","end","length"),show="headings")
        for key,title in [("file","Video"),("start","Boshlanish"),("end","Tugash"),("length","Uzunlik")]:
            self.tree.heading(key,text=title)
            self.tree.column(key,width=100 if key!="file" else 250)
        self.tree.pack(fill="both",expand=True)
        self.tree.bind("<<TreeviewSelect>>",self.selected)
        self.label=ttk.Label(right,text="Klip tanlang",wraplength=300)
        self.label.pack(anchor="w")
        self.start=tk.StringVar(value="0")
        self.end=tk.StringVar(value="0")
        for title,var in [("Boshlanish (sekund)",self.start),("Tugash (sekund)",self.end)]:
            ttk.Label(right,text=title).pack(anchor="w",pady=(12,2))
            ttk.Entry(right,textvariable=var).pack(fill="x")
        ttk.Button(right,text="Kesishni qo'llash",command=self.trim).pack(fill="x",pady=12)
        self.preview=tk.Label(right,text="Kadr ko'rinishi",height=12,bg="#151824",fg="white")
        self.preview.pack(fill="both",expand=True)
        ttk.Button(right,text="Kadrni ko'rsatish",command=self.frame).pack(fill="x",pady=8)
        self.status=tk.StringVar(value="Tayyor")
        ttk.Label(self,textvariable=self.status,padding=8).pack(fill="x")

    def current(self):
        selection=self.tree.selection()
        return int(selection[0]) if selection else None

    def redraw(self,selection=None):
        self.tree.delete(*self.tree.get_children())
        for i,c in enumerate(self.clips):
            self.tree.insert("","end",iid=str(i),values=(Path(c["path"]).name,
              f'{c["start"]:.2f}',f'{c["end"]:.2f}',f'{c["end"]-c["start"]:.2f}'))
        if selection is not None and 0<=selection<len(self.clips):
            self.tree.selection_set(str(selection))
            self.tree.see(str(selection))

    def selected(self,event=None):
        i=self.current()
        if i is not None:
            c=self.clips[i]
            self.label.config(text=Path(c["path"]).name)
            self.start.set(str(c["start"]))
            self.end.set(str(c["end"]))

    def add(self):
        paths=filedialog.askopenfilenames(filetypes=FORMATS)
        try:
            for path in paths:
                d=duration(path)
                if d<=0: raise ValueError(f"Video davomiyligi noto'g'ri: {path}")
                self.clips.append({"path":str(Path(path).resolve()),"start":0.0,"end":d})
            self.redraw(len(self.clips)-1)
        except Exception as exc: messagebox.showerror("Xato",str(exc))

    def trim(self):
        i=self.current()
        if i is None: return
        try:
            start,end=float(self.start.get()),float(self.end.get())
            maximum=duration(self.clips[i]["path"])
            if not 0<=start<end<=maximum+0.01: raise ValueError("Kesish vaqtlarini tekshiring")
            self.clips[i].update(start=start,end=min(end,maximum))
            self.redraw(i)
        except Exception as exc: messagebox.showerror("Xato",str(exc))

    def move(self,d):
        i=self.current()
        if i is not None and 0<=i+d<len(self.clips):
            self.clips[i],self.clips[i+d]=self.clips[i+d],self.clips[i]
            self.redraw(i+d)

    def remove(self):
        i=self.current()
        if i is not None:
            self.clips.pop(i)
            self.redraw(min(i,len(self.clips)-1))

    def save(self):
        dest=filedialog.asksaveasfilename(defaultextension=".lioncut",
                 filetypes=[("LionCut project","*.lioncut")])
        if dest:
            Path(dest).write_text(json.dumps({"version":1,"clips":self.clips},
                                  ensure_ascii=False,indent=2),encoding="utf-8")
            self.status.set("Loyiha saqlandi")

    def load(self):
        dest=filedialog.askopenfilename(filetypes=[("LionCut project","*.lioncut")])
        if not dest:return
        try:
            data=json.loads(Path(dest).read_text(encoding="utf-8"))
            clips=data["clips"]
            if not isinstance(clips,list):raise ValueError("Loyiha xato")
            for c in clips:
                if not isinstance(c,dict) or not {"path","start","end"}<=c.keys():
                    raise ValueError("Klip ma'lumoti xato")
            self.clips=clips
            self.redraw()
        except Exception as exc: messagebox.showerror("Xato",str(exc))

    def frame(self):
        i=self.current()
        if i is None:return
        try:
            from PIL import Image,ImageTk
            with tempfile.TemporaryDirectory() as td:
                dest=str(Path(td)/"frame.jpg")
                c=self.clips[i]
                command("ffmpeg","-hide_banner","-loglevel","error","-y",
                        "-ss",c["start"],"-i",c["path"],"-frames:v","1",
                        "-vf","scale=560:-2",dest)
                image=Image.open(dest)
                image.thumbnail((410,260))
                self.preview_image=ImageTk.PhotoImage(image)
                self.preview.config(image=self.preview_image,text="")
        except Exception as exc:messagebox.showerror("Xato",str(exc))

    def export(self):
        if self.busy or not self.clips:return
        dest=filedialog.asksaveasfilename(defaultextension=".mp4",filetypes=[("MP4","*.mp4")])
        if not dest:return
        self.busy=True
        clips=[dict(c) for c in self.clips]
        self.status.set("Eksport boshlandi...")
        threading.Thread(target=self.worker,args=(clips,dest),daemon=True).start()

    def worker(self,clips,dest):
        try:
            with tempfile.TemporaryDirectory() as td:
                parts=[]
                for i,c in enumerate(clips):
                    if not Path(c["path"]).is_file():raise FileNotFoundError(c["path"])
                    part=str(Path(td)/f"part_{i:04d}.mp4")
                    command("ffmpeg","-hide_banner","-loglevel","error","-y",
                      "-ss",c["start"],"-i",c["path"],"-t",float(c["end"])-float(c["start"]),
                      "-vf","scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,format=yuv420p",
                      "-an","-c:v","libx264","-preset","veryfast","-crf","23",part)
                    parts.append(part)
                    self.after(0,self.status.set,f"Eksport: {i+1}/{len(clips)}")
                listing=Path(td)/"concat.txt"
                listing.write_text("".join("file '"+p.replace("\\","/")+"'"+"\n" for p in parts),encoding="utf-8")
                command("ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat",
                        "-safe","0","-i",str(listing),"-c","copy",dest)
            self.after(0,self.status.set,f"Tayyor: {dest}")
            self.after(0,lambda:messagebox.showinfo("Tayyor",f"Video saqlandi:\n{dest}"))
        except Exception as exc:
            msg=str(exc)
            self.after(0,lambda:messagebox.showerror("Eksport xatosi",msg))
            self.after(0,self.status.set,"Eksport xatosi")
        finally:self.after(0,self.done)

    def done(self):self.busy=False

if __name__=="__main__":
    LionCut().mainloop()
