import tkinter as tk
from models import Project
from views import HomeView, DashboardView

class App(tk.Tk):
    """main controller"""
    def __init__(self):
        super().__init__()
        self.iconphoto(True,tk.PhotoImage(file="icon.png"))
        self.title("Efficiweb v.01")
        self.geometry("450x600")
        self.resizable(False, False)
        self.current_project = None
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        for F in (HomeView, DashboardView):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(HomeView)
        
    def show_frame(self, container_class):
        self.frames[container_class].tkraise()
        
    def open_project(self, name):
        self.current_project = Project.load(name)
        if self.current_project:
            self.frames[DashboardView].load_project_details()
            self.show_frame(DashboardView)
            
    def go_home(self):
        self.frames[HomeView].refresh_projects()
        self.show_frame(HomeView)

if __name__ == "__main__":
    app = App()
    app.mainloop()