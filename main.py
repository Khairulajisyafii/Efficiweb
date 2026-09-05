import os
import sys
import customtkinter as ctk
from models import Project
from views import HomeView, DashboardView

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def resource_path(relative_path: str) -> str:
    """Resolve path aset — bekerja di mode dev maupun setelah di-bundle PyInstaller."""
    base = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base, relative_path)

class App(ctk.CTk):
    """Main Application Controller"""
    def __init__(self):
        super().__init__()
        
        try:
            self.iconbitmap(resource_path("icon.ico"))
        except Exception:
            pass # Ignore if icon is missing during dev
            
        self.title("Efficiweb - Modern Edition")
        self.geometry("800x600")
        self.minsize(250, 400)
        
        # Transparent glass feel
        self.attributes('-alpha', 0.97)
        
        self.current_project = None
        
        # Grid setup for main window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        for F in (HomeView, DashboardView):
            frame = F(self, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(HomeView)
        
    def show_frame(self, container_class):
        self.frames[container_class].tkraise()
        if hasattr(self.frames[container_class], "on_show"):
            self.frames[container_class].on_show()
        
    def open_project(self, name):
        self.current_project = Project.load(name)
        if self.current_project:
            self.frames[DashboardView].load_project_details()
            self.show_frame(DashboardView)
            
    def go_home(self):
        self.frames[HomeView].on_show()
        self.show_frame(HomeView)

if __name__ == "__main__":
    app = App()
    app.mainloop()