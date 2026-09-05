import os
import json
import webbrowser
import tkinter as tk
from typing import Dict, List, Optional

import customtkinter as ctk
import tkinter.messagebox as messagebox

from config import (
    DATABASE_DIR, FONT_FAMILY, 
    COLOR_BG_MAIN, COLOR_BG_SIDEBAR, COLOR_BG_CARD, COLOR_BG_INPUT,
    COLOR_TEXT_LIGHT, COLOR_TEXT_MUTED,
    COLOR_ACCENT_CYAN, COLOR_ACCENT_TEAL, COLOR_DANGER, COLOR_SUCCESS
)
from utils import ColorConverter
from models import Project, GlobalShortlinkStore, GlobalSnippetStore

EMOJI_LIST = [
    "🌐", "🔗", "📌", "⭐", "🚀", "📦", "🎨", "🛠️",
    "📝", "🔍", "💡", "🏠", "📊", "📱", "💻", "🖥️",
    "⚙️", "🔧", "🔨", "🗂️", "📁", "🌟", "✅", "⚡",
    "🎯", "🧩", "🔐", "🔑", "🌈", "🐙", "🦊", "🔵",
    "🟢", "🔴", "🟡", "🔥", "💎", "🏆", "📮", "🗃️",
    "📋", "🖊️", "🔖", "🧲", "🔔", "🌍", "📡", "🛡️",
    "🪝", "🪄", "🧪", "🔬", "🗺️", "🎭", "🎪", "💬",
]

# ============================================================================
# DIALOGS
# ============================================================================

class EmojiPickerDialog(ctk.CTkToplevel):
    def __init__(self, parent, current_emoji: str, callback):
        super().__init__(parent)
        self.title("Select Icon")
        self.geometry("380x320")
        self.resizable(False, False)
        self.attributes('-alpha', 0.98)
        self.configure(fg_color=COLOR_BG_CARD)
        self.callback = callback
        
        self.transient(parent)
        self.grab_set()
        
        ctk.CTkLabel(self, text="Select Shortlink Icon", font=(FONT_FAMILY, 16, "bold"), text_color=COLOR_TEXT_LIGHT).pack(pady=(15, 10))
        
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        cols = 6
        for i, emoji in enumerate(EMOJI_LIST):
            is_active = (emoji == current_emoji)
            btn = ctk.CTkButton(
                scroll, text=emoji, width=40, height=40, font=("Segoe UI Emoji", 18),
                fg_color=COLOR_ACCENT_CYAN if is_active else COLOR_BG_INPUT,
                text_color="#000000" if is_active else COLOR_TEXT_LIGHT,
                hover_color=COLOR_ACCENT_TEAL,
                command=lambda e=emoji: self._select(e)
            )
            btn.grid(row=i // cols, column=i % cols, padx=5, pady=5)
            
    def _select(self, emoji):
        self.callback(emoji)
        self.destroy()

class ShortlinkFormDialog(ctk.CTkToplevel):
    def __init__(self, parent, title: str, initial_data: Optional[Dict] = None, on_submit=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x380")
        self.resizable(False, False)
        self.attributes('-alpha', 0.98)
        self.configure(fg_color=COLOR_BG_CARD)
        self.on_submit = on_submit
        
        self.transient(parent)
        self.grab_set()
        
        self.selected_emoji = initial_data.get("icon", "🔗") if initial_data else "🔗"
        
        ctk.CTkLabel(self, text=title, font=(FONT_FAMILY, 18, "bold"), text_color=COLOR_ACCENT_CYAN).pack(pady=(20, 15))
        
        icon_frame = ctk.CTkFrame(self, fg_color="transparent")
        icon_frame.pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(icon_frame, text="Icon:", font=(FONT_FAMILY, 12, "bold"), text_color=COLOR_TEXT_MUTED).pack(side="left")
        self.icon_btn = ctk.CTkButton(
            icon_frame, text=self.selected_emoji, width=50, height=40, font=("Segoe UI Emoji", 18),
            fg_color=COLOR_BG_INPUT, hover_color=COLOR_BG_MAIN,
            command=self._open_emoji_picker
        )
        self.icon_btn.pack(side="left", padx=10)
        
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Display Name", height=40, fg_color=COLOR_BG_INPUT, border_color=COLOR_BG_MAIN)
        self.name_entry.pack(fill="x", padx=30, pady=10)
        
        self.url_entry = ctk.CTkEntry(self, placeholder_text="URL / Link", height=40, fg_color=COLOR_BG_INPUT, border_color=COLOR_BG_MAIN)
        self.url_entry.pack(fill="x", padx=30, pady=10)
        
        if initial_data:
            self.name_entry.insert(0, initial_data.get("name", ""))
            self.url_entry.insert(0, initial_data.get("url", ""))
            
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkButton(btn_frame, text="Cancel", width=100, fg_color=COLOR_DANGER, hover_color="#CC0000", text_color="#FFFFFF", command=self.destroy).pack(side="left")
        ctk.CTkButton(btn_frame, text="Submit", width=100, fg_color=COLOR_SUCCESS, hover_color="#444444", text_color="#FFFFFF", command=self._submit).pack(side="right")
        
    def _open_emoji_picker(self):
        EmojiPickerDialog(self, self.selected_emoji, self._update_emoji)
        
    def _update_emoji(self, emoji):
        self.selected_emoji = emoji
        self.icon_btn.configure(text=emoji)
        
    def _submit(self):
        name = self.name_entry.get().strip()
        url = self.url_entry.get().strip()
        if not name or not url:
            messagebox.showerror("Error", "Name and URL are required!", parent=self)
            return
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        if self.on_submit:
            self.on_submit({"icon": self.selected_emoji, "name": name, "url": url})
        self.destroy()

class CssSnippetFormDialog(ctk.CTkToplevel):
    def __init__(self, parent, title: str, initial_data: Optional[Dict] = None, on_submit=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("600x500")
        self.minsize(500, 450)
        self.attributes('-alpha', 0.98)
        self.configure(fg_color=COLOR_BG_CARD)
        self.on_submit = on_submit
        
        self.transient(parent)
        self.grab_set()
        
        header = ctk.CTkFrame(self, fg_color=COLOR_BG_MAIN, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text=f"📋 {title}", font=(FONT_FAMILY, 16, "bold"), text_color=COLOR_ACCENT_CYAN, anchor="w").pack(padx=20, pady=15, fill="x")
        
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Snippet Name", height=40, fg_color=COLOR_BG_INPUT, border_color=COLOR_BG_MAIN)
        self.name_entry.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(self, text="CSS Code:", font=(FONT_FAMILY, 12, "bold"), text_color=COLOR_TEXT_MUTED, anchor="w").pack(fill="x", padx=20)
        
        self.code_text = ctk.CTkTextbox(self, font=("Consolas", 13), fg_color=COLOR_BG_INPUT, border_color=COLOR_BG_MAIN, border_width=2)
        self.code_text.pack(fill="both", expand=True, padx=20, pady=(5, 10))
        self.code_text.bind("<Tab>", self._on_tab)
        
        if initial_data:
            self.name_entry.insert(0, initial_data.get("name", ""))
            self.code_text.insert("1.0", initial_data.get("code", ""))
            
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        ctk.CTkButton(btn_frame, text="Cancel", width=120, fg_color=COLOR_DANGER, hover_color="#CC0000", text_color="#FFFFFF", command=self.destroy).pack(side="left")
        ctk.CTkButton(btn_frame, text="Save Snippet", width=120, fg_color=COLOR_SUCCESS, hover_color="#444444", text_color="#FFFFFF", command=self._submit).pack(side="right")
        
    def _on_tab(self, event):
        self.code_text.insert("insert", "    ")
        return "break"
        
    def _submit(self):
        name = self.name_entry.get().strip()
        code = self.code_text.get("1.0", "end").strip()
        if not name or not code:
            messagebox.showerror("Error", "Name and Code cannot be empty!", parent=self)
            return
        if self.on_submit:
            self.on_submit({"name": name, "code": code})
        self.destroy()

class CssSnippetViewDialog(ctk.CTkToplevel):
    def __init__(self, parent, snippet: Dict):
        super().__init__(parent)
        self.title(snippet.get("name", "Snippet"))
        self.geometry("600x500")
        self.minsize(400, 300)
        self.attributes('-alpha', 0.98)
        self.configure(fg_color=COLOR_BG_CARD)
        
        self.transient(parent)
        self.grab_set()
        
        header = ctk.CTkFrame(self, fg_color=COLOR_BG_MAIN, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text=f"📋 {snippet.get('name', '')}", font=(FONT_FAMILY, 16, "bold"), text_color=COLOR_ACCENT_TEAL, anchor="w").pack(padx=20, pady=15, fill="x")
        
        code = snippet.get("code", "")
        
        self.code_text = ctk.CTkTextbox(self, font=("Consolas", 13), fg_color=COLOR_BG_INPUT)
        self.code_text.pack(fill="both", expand=True, padx=20, pady=20)
        self.code_text.insert("1.0", code)
        self.code_text.configure(state="disabled")
        
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=20, pady=(0, 20))
        
        self.copy_btn = ctk.CTkButton(bottom, text="⎘ Copy All", fg_color=COLOR_ACCENT_CYAN, text_color="#000000", hover_color=COLOR_ACCENT_TEAL, command=lambda: self._copy(code))
        self.copy_btn.pack(side="left")
        ctk.CTkButton(bottom, text="Close", fg_color=COLOR_BG_INPUT, hover_color=COLOR_BG_MAIN, command=self.destroy).pack(side="right")
        
    def _copy(self, code):
        self.clipboard_clear()
        self.clipboard_append(code)
        self.copy_btn.configure(text="✅ Copied!", fg_color=COLOR_SUCCESS, text_color="#FFFFFF")
        self.after(1500, lambda: self.copy_btn.configure(text="⎘ Copy All", fg_color=COLOR_ACCENT_CYAN, text_color="#000000"))

# ============================================================================
# MAIN VIEWS
# ============================================================================

class HomeView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG_MAIN, corner_radius=0)
        self.controller = controller
        self._is_small_state = False
        
        # Use native tk.PanedWindow for zero-flicker sash
        self.paned = tk.PanedWindow(
            self, orient="horizontal", sashwidth=5, sashpad=0,
            bg="#333333", bd=0, opaqueresize=True, sashrelief="flat"
        )
        self.paned.pack(fill="both", expand=True)
        
        # -- Sidebar --
        self.sidebar = ctk.CTkFrame(self.paned, fg_color=COLOR_BG_SIDEBAR, corner_radius=0)
        self.paned.add(self.sidebar, minsize=50, width=160, stretch="never")
        
        # Brand
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", pady=30, padx=10)
        self.lbl_brand = ctk.CTkLabel(brand_frame, text="EFFICIWEB", font=(FONT_FAMILY, 18, "bold"), text_color=COLOR_ACCENT_CYAN)
        self.lbl_brand.pack(anchor="w")
        self.lbl_brand_sub = ctk.CTkLabel(brand_frame, text="webdev tools", font=(FONT_FAMILY, 10, "italic"), text_color=COLOR_TEXT_MUTED)
        self.lbl_brand_sub.pack(anchor="w")
        
        # Global Tools
        self.lbl_global = ctk.CTkLabel(self.sidebar, text="GLOBAL", font=(FONT_FAMILY, 10, "bold"), text_color=COLOR_TEXT_MUTED)
        self.lbl_global.pack(anchor="w", padx=10, pady=(20, 5))
        
        self.btn_sl = ctk.CTkButton(
            self.sidebar, text="🔗 Shortlinks", font=(FONT_FAMILY, 13, "bold"),
            fg_color="transparent", text_color=COLOR_TEXT_LIGHT, hover_color=COLOR_BG_CARD,
            anchor="w", command=self.open_global_shortlinks
        )
        self.btn_sl.pack(fill="x", padx=5, pady=5)
        
        self.btn_css = ctk.CTkButton(
            self.sidebar, text="💄 CSS", font=(FONT_FAMILY, 13, "bold"),
            fg_color="transparent", text_color=COLOR_TEXT_LIGHT, hover_color=COLOR_BG_CARD,
            anchor="w", command=self.open_global_css
        )
        self.btn_css.pack(fill="x", padx=5, pady=5)
        
        # -- Main Content --
        self.main_content = ctk.CTkFrame(self.paned, fg_color=COLOR_BG_MAIN, corner_radius=0)
        self.paned.add(self.main_content, minsize=200, stretch="always")
        
        inner = ctk.CTkFrame(self.main_content, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=30, pady=30)
        inner.grid_rowconfigure(1, weight=1)
        inner.grid_columnconfigure(0, weight=1)
        
        header_frame = ctk.CTkFrame(inner, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(header_frame, text="Your Projects", font=(FONT_FAMILY, 28, "bold"), text_color=COLOR_TEXT_LIGHT).pack(side="left")
        ctk.CTkButton(header_frame, text="＋ New Project", font=(FONT_FAMILY, 13, "bold"), fg_color=COLOR_ACCENT_CYAN, text_color="#000000", hover_color=COLOR_ACCENT_TEAL, command=self.open_new_project_dialog).pack(side="right")
        
        self.scroll_frame = ctk.CTkScrollableFrame(inner, fg_color="transparent")
        self.scroll_frame.grid(row=1, column=0, sticky="nsew")
        
        # Bind sidebar resize to toggle icon-only mode
        self.sidebar.bind("<Configure>", self._on_sidebar_resize)

    def _on_sidebar_resize(self, event):
        w = event.width
        is_small = w < 130
        if is_small != self._is_small_state:
            self._is_small_state = is_small
            if is_small:
                self.lbl_brand.configure(text="EW")
                self.lbl_brand_sub.pack_forget()
                self.lbl_global.pack_forget()
                self.btn_sl.configure(text="🔗", anchor="center")
                self.btn_css.configure(text="💄", anchor="center")
            else:
                self.lbl_brand.configure(text="EFFICIWEB")
                try:
                    self.lbl_brand_sub.pack(anchor="w")
                    self.lbl_global.pack(anchor="w", padx=10, pady=(20, 5))
                except Exception:
                    pass
                self.btn_sl.configure(text="🔗 Shortlinks", anchor="w")
                self.btn_css.configure(text="💄 CSS", anchor="w")

    def on_show(self):
        self.refresh_projects()
        
    def refresh_projects(self):
        for w in self.scroll_frame.winfo_children():
            w.destroy()
            
        if not os.path.exists(DATABASE_DIR) or not os.listdir(DATABASE_DIR):
            ctk.CTkLabel(self.scroll_frame, text="No projects found. Create one to get started!", font=(FONT_FAMILY, 14), text_color=COLOR_TEXT_MUTED).pack(pady=40)
            return
            
        for file in os.listdir(DATABASE_DIR):
            if file.endswith('.json'):
                try:
                    with open(os.path.join(DATABASE_DIR, file), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self._create_project_card(data.get("name", file[:-5]), data.get("short_desc", ""))
                except Exception:
                    pass
                    
    def _create_project_card(self, name: str, desc: str):
        card = ctk.CTkFrame(self.scroll_frame, fg_color=COLOR_BG_CARD, corner_radius=10)
        card.pack(fill="x", pady=10, padx=5)
        
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(info_frame, text=name, font=(FONT_FAMILY, 18, "bold"), text_color=COLOR_TEXT_LIGHT).pack(anchor="w")
        if desc:
            ctk.CTkLabel(info_frame, text=desc, font=(FONT_FAMILY, 13), text_color=COLOR_TEXT_MUTED).pack(anchor="w")
            
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(side="right", padx=20, pady=20)
        
        ctk.CTkButton(btn_frame, text="Open ➔", width=80, font=(FONT_FAMILY, 12, "bold"), fg_color=COLOR_ACCENT_TEAL, hover_color="#666666", text_color="#000000", command=lambda n=name: self.controller.open_project(n)).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🗑", width=40, font=("Segoe UI Emoji", 14), fg_color=COLOR_BG_INPUT, text_color=COLOR_DANGER, hover_color="#333333", command=lambda n=name: self.delete_project(n)).pack(side="left", padx=5)
        
    def open_new_project_dialog(self):
        dialog = ctk.CTkToplevel(self.controller)
        dialog.title("New Project")
        dialog.geometry("450x450")
        dialog.resizable(False, False)
        dialog.attributes('-alpha', 0.98)
        dialog.configure(fg_color=COLOR_BG_CARD)
        dialog.transient(self.controller)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text="Create New Project", font=(FONT_FAMILY, 20, "bold"), text_color=COLOR_ACCENT_CYAN).pack(pady=(25, 20))
        
        name_entry = ctk.CTkEntry(dialog, placeholder_text="Project Name", height=45, fg_color=COLOR_BG_INPUT, border_color=COLOR_BG_MAIN)
        name_entry.pack(fill="x", padx=40, pady=10)
        
        desc_entry = ctk.CTkEntry(dialog, placeholder_text="Short Description", height=45, fg_color=COLOR_BG_INPUT, border_color=COLOR_BG_MAIN)
        desc_entry.pack(fill="x", padx=40, pady=10)
        
        full_desc = ctk.CTkTextbox(dialog, height=100, fg_color=COLOR_BG_INPUT, border_color=COLOR_BG_MAIN, border_width=2)
        full_desc.insert("1.0", "Full notes or description...")
        full_desc.pack(fill="x", padx=40, pady=10)
        
        def submit():
            p_name = name_entry.get().strip()
            s_desc = desc_entry.get().strip()
            f_desc = full_desc.get("1.0", "end").strip()
            if not p_name:
                return messagebox.showerror("Error", "Project name is required!", parent=dialog)
            if os.path.exists(os.path.join(DATABASE_DIR, f"{p_name.lower().replace(' ', '_')}.json")):
                return messagebox.showerror("Error", "Project name already exists!", parent=dialog)
                
            Project(name=p_name, short_desc=s_desc, full_desc=f_desc).save()
            dialog.destroy()
            self.refresh_projects()
            
        ctk.CTkButton(dialog, text="Create Project", height=45, font=(FONT_FAMILY, 14, "bold"), fg_color=COLOR_SUCCESS, hover_color="#444444", text_color="#FFFFFF", command=submit).pack(fill="x", padx=40, pady=(15, 20))

    def delete_project(self, name):
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete '{name}'?"):
            Project(name=name).delete()
            self.refresh_projects()

    def open_global_shortlinks(self):
        GlobalShortlinkManagerDialog(self.controller)
        
    def open_global_css(self):
        GlobalCssManagerDialog(self.controller)


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG_MAIN, corner_radius=0)
        self.controller = controller
        self._is_small_state = False
        
        # Use native tk.PanedWindow for zero-flicker sash
        self.paned = tk.PanedWindow(
            self, orient="horizontal", sashwidth=5, sashpad=0,
            bg="#333333", bd=0, opaqueresize=True, sashrelief="flat"
        )
        self.paned.pack(fill="both", expand=True)
        
        # -- Sidebar Navigation --
        self.sidebar = ctk.CTkFrame(self.paned, fg_color=COLOR_BG_SIDEBAR, corner_radius=0)
        self.paned.add(self.sidebar, minsize=50, width=160, stretch="never")
        
        # Project Title Area
        self.lbl_proj_title = ctk.CTkLabel(self.sidebar, text="Project", font=(FONT_FAMILY, 18, "bold"), text_color=COLOR_ACCENT_CYAN, wraplength=140)
        self.lbl_proj_title.pack(anchor="w", padx=10, pady=(30, 20))
        
        # Nav Buttons
        self.nav_btns = {}
        tabs = [("colors", "🎨 Colors"), ("shortlinks", "🔗 Shortlinks"), ("css", "📋 CSS Snippets")]
        for tab_id, text in tabs:
            btn = ctk.CTkButton(
                self.sidebar, text=text, font=(FONT_FAMILY, 13, "bold"),
                fg_color="transparent", text_color=COLOR_TEXT_MUTED, hover_color=COLOR_BG_CARD,
                anchor="w", height=40, command=lambda t=tab_id: self.show_tab(t)
            )
            btn.pack(fill="x", padx=5, pady=5)
            self.nav_btns[tab_id] = btn
            
        spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        spacer.pack(fill="both", expand=True)
        
        self.btn_back = ctk.CTkButton(
            self.sidebar, text="← Back", font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLOR_BG_INPUT, text_color=COLOR_TEXT_LIGHT, hover_color=COLOR_BG_CARD,
            height=40, anchor="center", command=self.controller.go_home
        )
        self.btn_back.pack(fill="x", padx=10, pady=30)
        
        # -- Main Content --
        self.main_content = ctk.CTkFrame(self.paned, fg_color=COLOR_BG_MAIN, corner_radius=0)
        self.paned.add(self.main_content, minsize=200, stretch="always")
        
        inner = ctk.CTkFrame(self.main_content, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=30, pady=30)
        inner.grid_rowconfigure(0, weight=1)
        inner.grid_columnconfigure(0, weight=1)
        
        # Panels
        self.panels = {}
        
        self.panels["colors"] = ctk.CTkFrame(inner, fg_color="transparent")
        self.panels["colors"].grid_rowconfigure(1, weight=1)
        self.panels["colors"].grid_columnconfigure(0, weight=1)
        self.init_colors_panel()
        
        self.panels["shortlinks"] = ctk.CTkFrame(inner, fg_color="transparent")
        self.panels["shortlinks"].grid_rowconfigure(1, weight=1)
        self.panels["shortlinks"].grid_columnconfigure(0, weight=1)
        self.init_shortlinks_panel()
        
        self.panels["css"] = ctk.CTkFrame(inner, fg_color="transparent")
        self.panels["css"].grid_rowconfigure(1, weight=1)
        self.panels["css"].grid_columnconfigure(0, weight=1)
        self.init_css_panel()
        
        # Bind sidebar resize to toggle icon-only mode
        self.sidebar.bind("<Configure>", self._on_sidebar_resize)

    def _on_sidebar_resize(self, event):
        w = event.width
        is_small = w < 130
        if is_small != self._is_small_state:
            self._is_small_state = is_small
            if is_small:
                proj_name = self.controller.current_project.name if self.controller.current_project else ""
                self.lbl_proj_title.configure(text=proj_name[:2] + ".." if len(proj_name) > 2 else proj_name)
                self.nav_btns["colors"].configure(text="🎨", anchor="center")
                self.nav_btns["shortlinks"].configure(text="🔗", anchor="center")
                self.nav_btns["css"].configure(text="📋", anchor="center")
                self.btn_back.configure(text="←", anchor="center")
            else:
                proj_name = self.controller.current_project.name if self.controller.current_project else ""
                self.lbl_proj_title.configure(text=proj_name)
                self.nav_btns["colors"].configure(text="🎨 Colors", anchor="w")
                self.nav_btns["shortlinks"].configure(text="🔗 Shortlinks", anchor="w")
                self.nav_btns["css"].configure(text="📋 CSS Snippets", anchor="w")
                self.btn_back.configure(text="← Back", anchor="center")

    def on_show(self):
        pass
        
    def load_project_details(self):
        if self.controller.current_project:
            self.lbl_proj_title.configure(text=self.controller.current_project.name)
            self.show_tab("colors")
            
    def show_tab(self, tab_id):
        for t, btn in self.nav_btns.items():
            if t == tab_id:
                btn.configure(fg_color=COLOR_BG_CARD, text_color=COLOR_ACCENT_CYAN)
            else:
                btn.configure(fg_color="transparent", text_color=COLOR_TEXT_MUTED)
                
        for t, panel in self.panels.items():
            panel.grid_forget()
            
        self.panels[tab_id].grid(row=0, column=0, sticky="nsew")
        
        if tab_id == "colors":
            self.refresh_colors()
        elif tab_id == "shortlinks":
            self.refresh_shortlinks()
        elif tab_id == "css":
            self.refresh_css()

    # --- Colors Panel ---
    def init_colors_panel(self):
        p = self.panels["colors"]
        
        header = ctk.CTkFrame(p, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        ctk.CTkLabel(header, text="Color Palette", font=(FONT_FAMILY, 24, "bold"), text_color=COLOR_TEXT_LIGHT).pack(side="left")
        
        # Add form directly at the top right
        add_frame = ctk.CTkFrame(header, fg_color="transparent")
        add_frame.pack(side="right")
        self.color_name_var = ctk.StringVar()
        self.color_hex_var = ctk.StringVar()
        
        name_wrapper = ctk.CTkFrame(add_frame, fg_color="transparent")
        name_wrapper.pack(side="left", padx=5)
        ctk.CTkLabel(name_wrapper, text="Color Name:", font=(FONT_FAMILY, 11, "bold"), text_color=COLOR_TEXT_MUTED).pack(anchor="w", pady=(0, 2))
        ctk.CTkEntry(name_wrapper, textvariable=self.color_name_var, placeholder_text="e.g. Background", width=100, height=35).pack(anchor="w")
        
        hex_wrapper = ctk.CTkFrame(add_frame, fg_color="transparent")
        hex_wrapper.pack(side="left", padx=5)
        ctk.CTkLabel(hex_wrapper, text="Color Code (Auto):", font=(FONT_FAMILY, 11, "bold"), text_color=COLOR_TEXT_MUTED).pack(anchor="w", pady=(0, 2))
        ctk.CTkEntry(hex_wrapper, textvariable=self.color_hex_var, placeholder_text="#FFF / rgb() / hsl()", width=120, height=35).pack(anchor="w")
        
        btn_wrapper = ctk.CTkFrame(add_frame, fg_color="transparent")
        btn_wrapper.pack(side="left", padx=5)
        ctk.CTkLabel(btn_wrapper, text="", font=(FONT_FAMILY, 11, "bold")).pack(pady=(0, 2)) # spacer
        ctk.CTkButton(btn_wrapper, text="＋ Add", width=70, height=35, font=(FONT_FAMILY, 12, "bold"), fg_color=COLOR_SUCCESS, hover_color="#444444", text_color="#FFFFFF", command=self.add_color).pack()
        
        self.colors_scroll = ctk.CTkScrollableFrame(p, fg_color="transparent")
        self.colors_scroll.grid(row=1, column=0, sticky="nsew")

    def refresh_colors(self):
        for w in self.colors_scroll.winfo_children():
            w.destroy()
            
        proj = self.controller.current_project
        if not proj or not proj.colors:
            ctk.CTkLabel(self.colors_scroll, text="No colors added yet.", text_color=COLOR_TEXT_MUTED).pack(pady=20)
            return
            
        for i, color in enumerate(proj.colors):
            card = ctk.CTkFrame(self.colors_scroll, fg_color=COLOR_BG_CARD, corner_radius=8)
            card.pack(fill="x", pady=5)
            
            box = ctk.CTkFrame(card, width=40, height=40, fg_color=color.get("hex", "#FFFFFF"), corner_radius=6)
            box.pack(side="left", padx=15, pady=15)
            
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, pady=10)
            
            ctk.CTkLabel(info, text=color.get("name", "Unnamed"), font=(FONT_FAMILY, 14, "bold"), text_color=COLOR_TEXT_LIGHT).pack(anchor="w")
            
            vals = ctk.CTkFrame(info, fg_color="transparent")
            vals.pack(fill="x", pady=(5, 0))
            for fmt in ["hex", "rgba", "hsl"]:
                v = color.get(fmt, "")
                btn = ctk.CTkButton(vals, text=f"{fmt.upper()}: {v}", font=(FONT_FAMILY, 11, "bold"), fg_color=COLOR_BG_INPUT, hover_color="#444444", text_color=COLOR_TEXT_MUTED, width=10, height=24)
                btn.configure(command=lambda val=v, b=btn: self._copy_color_btn(val, b))
                btn.pack(side="left", padx=(0, 6))
                
            ctk.CTkButton(card, text="🗑", width=40, fg_color="transparent", text_color=COLOR_DANGER, hover_color=COLOR_BG_INPUT, command=lambda idx=i: self.delete_color(idx)).pack(side="right", padx=15)

    def _copy_color_btn(self, text, btn):
        self.clipboard_clear()
        self.clipboard_append(text)
        orig_text = btn.cget("text")
        btn.configure(text="✅ Copied!", text_color=COLOR_TEXT_LIGHT)
        self.after(1200, lambda: btn.configure(text=orig_text, text_color=COLOR_TEXT_MUTED) if btn.winfo_exists() else None)
        
    def add_color(self):
        proj = self.controller.current_project
        name = self.color_name_var.get().strip()
        val = self.color_hex_var.get().strip()
        if not name or not val:
            return messagebox.showerror("Error", "Name and value required.")
            
        res = ColorConverter.auto_convert(val)
        if not res:
            return messagebox.showerror("Error", "Invalid color format. Try #HEX, rgb(), or hsl().")
            
        proj.colors.append({"name": name, "hex": res["hex"], "rgba": res["rgba"], "hsl": res["hsl"]})
        proj.save()
        self.color_name_var.set("")
        self.color_hex_var.set("")
        self.refresh_colors()
        
    def delete_color(self, index):
        if messagebox.askyesno("Confirm", "Delete this color?"):
            self.controller.current_project.colors.pop(index)
            self.controller.current_project.save()
            self.refresh_colors()

    # --- Shortlinks Panel ---
    def init_shortlinks_panel(self):
        p = self.panels["shortlinks"]
        header = ctk.CTkFrame(p, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        ctk.CTkLabel(header, text="Project Shortlinks", font=(FONT_FAMILY, 24, "bold"), text_color=COLOR_TEXT_LIGHT).pack(side="left")
        ctk.CTkButton(header, text="＋ Add Shortlink", width=120, height=35, fg_color=COLOR_ACCENT_TEAL, hover_color="#666666", text_color="#000000", command=self.add_proj_shortlink).pack(side="right")
        
        self.sl_scroll = ctk.CTkScrollableFrame(p, fg_color="transparent")
        self.sl_scroll.grid(row=1, column=0, sticky="nsew")

    def refresh_shortlinks(self):
        for w in self.sl_scroll.winfo_children():
            w.destroy()
        proj = self.controller.current_project
        if proj and proj.shortlinks:
            for i, sl in enumerate(proj.shortlinks):
                self._build_sl_card(self.sl_scroll, sl, i, is_global=False)
        else:
            ctk.CTkLabel(self.sl_scroll, text="No project shortlinks yet.", text_color=COLOR_TEXT_MUTED).pack(pady=10)
            
        global_sl = GlobalShortlinkStore.load()
        if global_sl:
            ctk.CTkLabel(self.sl_scroll, text="--- GLOBAL SHORTLINKS ---", font=(FONT_FAMILY, 12, "bold"), text_color=COLOR_TEXT_MUTED).pack(pady=(15, 5))
            for i, sl in enumerate(global_sl):
                self._build_sl_card(self.sl_scroll, sl, i, is_global=True)
            
    def _build_sl_card(self, parent, sl, index, is_global=False):
        card = ctk.CTkFrame(parent, fg_color=COLOR_BG_CARD, corner_radius=8)
        card.pack(fill="x", pady=5)
        
        ctk.CTkLabel(card, text=sl.get("icon", "🔗"), font=("Segoe UI Emoji", 24)).pack(side="left", padx=15, pady=15)
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, pady=10)
        
        ctk.CTkLabel(info, text=sl.get("name", "Link"), font=(FONT_FAMILY, 15, "bold"), text_color=COLOR_TEXT_LIGHT).pack(anchor="w")
        url = sl.get("url", "")
        url_lbl = ctk.CTkLabel(info, text=url if len(url) < 40 else url[:37]+"...", font=(FONT_FAMILY, 11), text_color=COLOR_TEXT_MUTED, cursor="hand2")
        url_lbl.pack(anchor="w")
        url_lbl.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))
        
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(side="right", padx=15)
        
        ctk.CTkButton(btn_frame, text="🌐", width=40, fg_color="transparent", text_color=COLOR_ACCENT_CYAN, hover_color=COLOR_BG_INPUT, command=lambda u=url: webbrowser.open(u)).pack(side="left", padx=2)
        if not is_global:
            ctk.CTkButton(btn_frame, text="✎", width=40, fg_color="transparent", text_color=COLOR_SUCCESS, hover_color=COLOR_BG_INPUT, command=lambda i=index: self.edit_proj_shortlink(i)).pack(side="left", padx=2)
            ctk.CTkButton(btn_frame, text="🗑", width=40, fg_color="transparent", text_color=COLOR_DANGER, hover_color=COLOR_BG_INPUT, command=lambda i=index: self.del_proj_shortlink(i)).pack(side="left", padx=2)
        else:
            ctk.CTkLabel(btn_frame, text="(Global)", font=(FONT_FAMILY, 10, "italic"), text_color=COLOR_TEXT_MUTED).pack(side="left", padx=5)

    def add_proj_shortlink(self):
        def on_submit(data):
            self.controller.current_project.shortlinks.append(data)
            self.controller.current_project.save()
            self.refresh_shortlinks()
        ShortlinkFormDialog(self.controller, "Add Project Shortlink", on_submit=on_submit)

    def edit_proj_shortlink(self, index):
        def on_submit(data):
            self.controller.current_project.shortlinks[index] = data
            self.controller.current_project.save()
            self.refresh_shortlinks()
        ShortlinkFormDialog(self.controller, "Edit Project Shortlink", initial_data=self.controller.current_project.shortlinks[index], on_submit=on_submit)

    def del_proj_shortlink(self, index):
        if messagebox.askyesno("Confirm", "Delete this shortlink?"):
            self.controller.current_project.shortlinks.pop(index)
            self.controller.current_project.save()
            self.refresh_shortlinks()

    # --- CSS Panel ---
    def init_css_panel(self):
        p = self.panels["css"]
        header = ctk.CTkFrame(p, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        ctk.CTkLabel(header, text="Project CSS Snippets", font=(FONT_FAMILY, 24, "bold"), text_color=COLOR_TEXT_LIGHT).pack(side="left")
        ctk.CTkButton(header, text="＋ Add Snippet", width=120, height=35, fg_color=COLOR_ACCENT_TEAL, hover_color="#666666", text_color="#000000", command=self.add_proj_css).pack(side="right")
        
        self.css_scroll = ctk.CTkScrollableFrame(p, fg_color="transparent")
        self.css_scroll.grid(row=1, column=0, sticky="nsew")

    def refresh_css(self):
        for w in self.css_scroll.winfo_children():
            w.destroy()
        proj = self.controller.current_project
        if proj and proj.snippets:
            for i, sn in enumerate(proj.snippets):
                self._build_css_card(self.css_scroll, sn, i, is_global=False)
        else:
            ctk.CTkLabel(self.css_scroll, text="No project CSS snippets yet.", text_color=COLOR_TEXT_MUTED).pack(pady=10)
            
        global_sn = GlobalSnippetStore.load()
        if global_sn:
            ctk.CTkLabel(self.css_scroll, text="--- GLOBAL CSS SNIPPETS ---", font=(FONT_FAMILY, 12, "bold"), text_color=COLOR_TEXT_MUTED).pack(pady=(15, 5))
            for i, sn in enumerate(global_sn):
                self._build_css_card(self.css_scroll, sn, i, is_global=True)
            
    def _build_css_card(self, parent, sn, index, is_global=False):
        card = ctk.CTkFrame(parent, fg_color=COLOR_BG_CARD, corner_radius=8)
        card.pack(fill="x", pady=5)
        
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(top, text=f"📋 {sn.get('name', '')}", font=(FONT_FAMILY, 15, "bold"), text_color=COLOR_TEXT_LIGHT).pack(side="left")
        
        btn_frame = ctk.CTkFrame(top, fg_color="transparent")
        btn_frame.pack(side="right")
        code = sn.get("code", "")
        
        copy_btn = ctk.CTkButton(btn_frame, text="⎘ Copy", width=50, height=24, font=(FONT_FAMILY, 10, "bold"), fg_color=COLOR_BG_INPUT, text_color=COLOR_TEXT_LIGHT, hover_color=COLOR_ACCENT_TEAL, command=lambda c=code, b=btn_frame: self._copy_css(c, b))
        copy_btn.pack(side="left", padx=2)
        
        ctk.CTkButton(btn_frame, text="👁", width=30, height=24, fg_color="transparent", text_color=COLOR_TEXT_LIGHT, hover_color=COLOR_BG_INPUT, command=lambda s=sn: CssSnippetViewDialog(self.controller, s)).pack(side="left", padx=2)
        if not is_global:
            ctk.CTkButton(btn_frame, text="✎", width=30, height=24, fg_color="transparent", text_color=COLOR_SUCCESS, hover_color=COLOR_BG_INPUT, command=lambda i=index: self.edit_proj_css(i)).pack(side="left", padx=2)
            ctk.CTkButton(btn_frame, text="🗑", width=30, height=24, fg_color="transparent", text_color=COLOR_DANGER, hover_color=COLOR_BG_INPUT, command=lambda i=index: self.del_proj_css(i)).pack(side="left", padx=2)
        else:
            ctk.CTkLabel(btn_frame, text="(Global)", font=(FONT_FAMILY, 10, "italic"), text_color=COLOR_TEXT_MUTED).pack(side="left", padx=5)
        
        # Preview
        lines = code.split('\n')
        preview = '\n'.join(lines[:3]) + ("\n..." if len(lines) > 3 else "")
        if preview.strip():
            prev_frame = ctk.CTkFrame(card, fg_color=COLOR_BG_INPUT, corner_radius=4)
            prev_frame.pack(fill="x", padx=15, pady=(0, 15))
            ctk.CTkLabel(prev_frame, text=preview, font=("Consolas", 12), text_color=COLOR_ACCENT_CYAN, justify="left", anchor="w").pack(fill="x", padx=10, pady=10)

    def _copy_css(self, code, parent_btn):
        self.clipboard_clear()
        self.clipboard_append(code)
        # Visual feedback omitted for brevity, simple copy is fine

    def add_proj_css(self):
        def on_submit(data):
            self.controller.current_project.snippets.append(data)
            self.controller.current_project.save()
            self.refresh_css()
        CssSnippetFormDialog(self.controller, "Add CSS Snippet", on_submit=on_submit)

    def edit_proj_css(self, index):
        def on_submit(data):
            self.controller.current_project.snippets[index] = data
            self.controller.current_project.save()
            self.refresh_css()
        CssSnippetFormDialog(self.controller, "Edit CSS Snippet", initial_data=self.controller.current_project.snippets[index], on_submit=on_submit)

    def del_proj_css(self, index):
        if messagebox.askyesno("Confirm", "Delete this snippet?"):
            self.controller.current_project.snippets.pop(index)
            self.controller.current_project.save()
            self.refresh_css()

# ============================================================================
# GLOBAL MANAGERS (Modernized)
# ============================================================================

class GlobalShortlinkManagerDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Global Shortlinks")
        self.geometry("500x600")
        self.minsize(450, 500)
        self.attributes('-alpha', 0.98)
        self.configure(fg_color=COLOR_BG_MAIN)
        
        self.transient(parent)
        self.grab_set()
        
        self.shortlinks = GlobalShortlinkStore.load()
        
        header = ctk.CTkFrame(self, fg_color=COLOR_BG_SIDEBAR, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="🌐 Global Shortlinks", font=(FONT_FAMILY, 20, "bold"), text_color=COLOR_ACCENT_CYAN).pack(pady=(20, 5))
        ctk.CTkLabel(header, text="Accessible across all projects.", font=(FONT_FAMILY, 12), text_color=COLOR_TEXT_MUTED).pack(pady=(0, 20))
        
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkButton(self, text="＋ Add Global Shortlink", height=45, fg_color=COLOR_SUCCESS, hover_color="#444444", text_color="#FFFFFF", command=self._add).pack(fill="x", padx=20, pady=20)
        
        self._refresh()
        
    def _refresh(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        if not self.shortlinks:
            ctk.CTkLabel(self.scroll, text="No global shortlinks.", text_color=COLOR_TEXT_MUTED).pack(pady=20)
            return
        for i, sl in enumerate(self.shortlinks):
            card = ctk.CTkFrame(self.scroll, fg_color=COLOR_BG_CARD, corner_radius=8)
            card.pack(fill="x", pady=5)
            
            ctk.CTkLabel(card, text=sl.get("icon", "🔗"), font=("Segoe UI Emoji", 20)).pack(side="left", padx=15)
            
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, pady=10)
            ctk.CTkLabel(info, text=sl.get("name", "Link"), font=(FONT_FAMILY, 14, "bold"), text_color=COLOR_TEXT_LIGHT).pack(anchor="w")
            
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(side="right", padx=15)
            
            ctk.CTkButton(btn_frame, text="🌐", width=35, fg_color="transparent", text_color=COLOR_ACCENT_CYAN, hover_color=COLOR_BG_INPUT, command=lambda u=sl.get("url", ""): webbrowser.open(u)).pack(side="left", padx=2)
            ctk.CTkButton(btn_frame, text="✎", width=35, fg_color="transparent", text_color=COLOR_SUCCESS, hover_color=COLOR_BG_INPUT, command=lambda i=i: self._edit(i)).pack(side="left", padx=2)
            ctk.CTkButton(btn_frame, text="🗑", width=35, fg_color="transparent", text_color=COLOR_DANGER, hover_color=COLOR_BG_INPUT, command=lambda i=i: self._delete(i)).pack(side="left", padx=2)

    def _add(self):
        def on_submit(data):
            self.shortlinks.append(data)
            GlobalShortlinkStore.save(self.shortlinks)
            self._refresh()
        ShortlinkFormDialog(self, "Add Global Shortlink", on_submit=on_submit)

    def _edit(self, index):
        def on_submit(data):
            self.shortlinks[index] = data
            GlobalShortlinkStore.save(self.shortlinks)
            self._refresh()
        ShortlinkFormDialog(self, "Edit Global Shortlink", initial_data=self.shortlinks[index], on_submit=on_submit)

    def _delete(self, index):
        if messagebox.askyesno("Confirm", "Delete this global shortlink?"):
            self.shortlinks.pop(index)
            GlobalShortlinkStore.save(self.shortlinks)
            self._refresh()

class GlobalCssManagerDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Global CSS Snippets")
        self.geometry("600x650")
        self.minsize(500, 550)
        self.attributes('-alpha', 0.98)
        self.configure(fg_color=COLOR_BG_MAIN)
        
        self.transient(parent)
        self.grab_set()
        
        self.snippets = GlobalSnippetStore.load()
        
        header = ctk.CTkFrame(self, fg_color=COLOR_BG_SIDEBAR, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="💄 Global CSS Snippets", font=(FONT_FAMILY, 20, "bold"), text_color=COLOR_ACCENT_CYAN).pack(pady=(20, 5))
        ctk.CTkLabel(header, text="Accessible across all projects.", font=(FONT_FAMILY, 12), text_color=COLOR_TEXT_MUTED).pack(pady=(0, 20))
        
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkButton(self, text="＋ Add Global CSS", height=45, fg_color=COLOR_SUCCESS, hover_color="#444444", text_color="#FFFFFF", command=self._add).pack(fill="x", padx=20, pady=20)
        
        self._refresh()
        
    def _refresh(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        if not self.snippets:
            ctk.CTkLabel(self.scroll, text="No global snippets.", text_color=COLOR_TEXT_MUTED).pack(pady=20)
            return
        for i, sn in enumerate(self.snippets):
            card = ctk.CTkFrame(self.scroll, fg_color=COLOR_BG_CARD, corner_radius=8)
            card.pack(fill="x", pady=5)
            
            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=15, pady=(15, 5))
            
            ctk.CTkLabel(top, text=f"📋 {sn.get('name', '')}", font=(FONT_FAMILY, 16, "bold"), text_color=COLOR_TEXT_LIGHT).pack(side="left")
            
            btn_frame = ctk.CTkFrame(top, fg_color="transparent")
            btn_frame.pack(side="right")
            
            ctk.CTkButton(btn_frame, text="👁", width=35, fg_color="transparent", text_color=COLOR_TEXT_LIGHT, hover_color=COLOR_BG_INPUT, command=lambda s=sn: CssSnippetViewDialog(self, s)).pack(side="left", padx=2)
            ctk.CTkButton(btn_frame, text="✎", width=35, fg_color="transparent", text_color=COLOR_SUCCESS, hover_color=COLOR_BG_INPUT, command=lambda i=i: self._edit(i)).pack(side="left", padx=2)
            ctk.CTkButton(btn_frame, text="🗑", width=35, fg_color="transparent", text_color=COLOR_DANGER, hover_color=COLOR_BG_INPUT, command=lambda i=i: self._delete(i)).pack(side="left", padx=2)
            
            prev_frame = ctk.CTkFrame(card, fg_color=COLOR_BG_INPUT, corner_radius=4)
            prev_frame.pack(fill="x", padx=15, pady=(0, 15))
            code = sn.get("code", "")
            lines = code.split('\n')
            preview = '\n'.join(lines[:3]) + ("\n..." if len(lines) > 3 else "")
            ctk.CTkLabel(prev_frame, text=preview, font=("Consolas", 12), text_color=COLOR_ACCENT_TEAL, justify="left", anchor="w").pack(fill="x", padx=10, pady=10)

    def _add(self):
        def on_submit(data):
            self.snippets.append(data)
            GlobalSnippetStore.save(self.snippets)
            self._refresh()
        CssSnippetFormDialog(self, "Add Global CSS", on_submit=on_submit)

    def _edit(self, index):
        def on_submit(data):
            self.snippets[index] = data
            GlobalSnippetStore.save(self.snippets)
            self._refresh()
        CssSnippetFormDialog(self, "Edit Global CSS", initial_data=self.snippets[index], on_submit=on_submit)

    def _delete(self, index):
        if messagebox.askyesno("Confirm", "Delete this global snippet?"):
            self.snippets.pop(index)
            GlobalSnippetStore.save(self.snippets)
            self._refresh()