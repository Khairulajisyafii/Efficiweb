import tkinter as tk
from config import FONT_FAMILY, COLOR_PRIMARY, COLOR_PRIMARY_DARK, COLOR_BG_LIGHT, COLOR_TEXT_DARK

class ScrollableFrame(tk.Frame):
    """Komponen kontainer Tkinter dengan fungsionalitas scrollbar bawaan."""
    def __init__(self, parent, bg_color=COLOR_PRIMARY_DARK, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, bg=bg_color)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=bg_color)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units") if self.canvas.winfo_exists() else None)

class ModernButton(tk.Button):
    """Tombol bergaya modern flat dengan visual interaktif hover."""
    def __init__(self, parent, text, bg_color, fg_color="#FFFFFF", command=None, font=(FONT_FAMILY, 9, "bold"), *args, **kwargs) -> None:
        super().__init__(
            parent, text=text, bg=bg_color, fg=fg_color, command=command, font=font,
            relief="flat", bd=0, highlightthickness=0, cursor="hand2",
            activebackground=bg_color, activeforeground=fg_color, pady=4, padx=12, *args, **kwargs
        )
        self.bg_color = bg_color
        self.bind("<Enter>", lambda e: self.configure(bg=self.adjust_brightness(self.bg_color, -15)))
        self.bind("<Leave>", lambda e: self.configure(bg=self.bg_color))
        
    @staticmethod
    def adjust_brightness(hex_color: str, pct: int) -> str:
        h = hex_color.lstrip('#')
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"#{max(0, min(255, r+pct)):02x}{max(0, min(255, g+pct)):02x}{max(0, min(255, b+pct)):02x}"

class ModernEntry(tk.Frame):
    """Kolom input modern minimalis lengkap dengan label teks di atasnya."""
    def __init__(self, parent, label_text: str, default_value: str = "", *args, **kwargs) -> None:
        super().__init__(parent, bg=COLOR_BG_LIGHT, *args, **kwargs)
        tk.Label(self, text=label_text, font=(FONT_FAMILY, 8, "bold"), fg=COLOR_TEXT_DARK, bg=COLOR_BG_LIGHT, anchor="w").pack(fill="x", pady=(0, 1))
        self.entry_frame = tk.Frame(self, bg="#CCCCCC", bd=1)
        self.entry_frame.pack(fill="x")
        self.entry = tk.Entry(self.entry_frame, relief="flat", bd=2, font=(FONT_FAMILY, 9), bg="#FFFFFF", insertbackground=COLOR_TEXT_DARK, fg=COLOR_TEXT_DARK)
        self.entry.pack(fill="x", ipady=1)
        if default_value: 
            self.entry.insert(0, default_value)
        self.entry.bind("<FocusIn>", lambda e: self.entry_frame.configure(bg=COLOR_PRIMARY))
        self.entry.bind("<FocusOut>", lambda e: self.entry_frame.configure(bg="#CCCCCC"))

    def get(self) -> str: 
        return self.entry.get().strip()
    def set(self, text: str) -> None:
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)