import os
import json
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict, Optional

from config import (
    DATABASE_DIR, FONT_FAMILY, COLOR_PRIMARY, COLOR_PRIMARY_DARK,
    COLOR_BG_LIGHT, COLOR_TEXT_DARK, COLOR_SUCCESS, COLOR_INFO,
    COLOR_DANGER, COLOR_DARK_BOX
)
from utils import ColorConverter
from models import Project
from components import ScrollableFrame, ModernButton, ModernEntry


class HomeView(tk.Frame):
    """Main view"""
    def __init__(self, parent, controller) -> None:
        super().__init__(parent, bg=COLOR_PRIMARY)
        self.controller = controller
        
        t_frame = tk.Frame(self, bg=COLOR_PRIMARY)
        t_frame.pack(fill="x", pady=(15, 5))
        tk.Label(t_frame, text="Efficiweb v.01", font=(FONT_FAMILY, 20, "bold"), fg="#FFFFFF", bg=COLOR_PRIMARY).pack()
        tk.Label(t_frame, text="webdev tools & utilities", font=(FONT_FAMILY, 10, "italic"), fg="#E6DADA", bg=COLOR_PRIMARY).pack()
        
        list_outer = tk.Frame(self, bg="#E0D6D6", padx=2, pady=2)
        list_outer.pack(fill="both", expand=True, padx=20, pady=(10, 10))
        
        self.project_listbox = tk.Listbox(
            list_outer, font=(FONT_FAMILY, 11, "bold"), fg=COLOR_TEXT_DARK, bg="#DCD1D1",
            relief="flat", bd=0, selectbackground=COLOR_PRIMARY_DARK, selectforeground="#FFFFFF",
            highlightthickness=0, activestyle="none"
        )
        self.project_listbox.pack(side="left", fill="both", expand=True)
        
        list_scroll = tk.Scrollbar(list_outer, orient="vertical", command=self.project_listbox.yview)
        list_scroll.pack(side="right", fill="y")
        self.project_listbox.configure(yscrollcommand=list_scroll.set)
        
        btn_frame = tk.Frame(self, bg=COLOR_PRIMARY)
        btn_frame.pack(fill="x", side="bottom", pady=(0, 15), padx=20)
        for i in range(3): 
            btn_frame.columnconfigure(i, weight=1)
        
        self.btn_new = ModernButton(btn_frame, text="NEW PROJECT", bg_color=COLOR_SUCCESS, font=(FONT_FAMILY, 8, "bold"), command=self.open_new_project_dialog)
        self.btn_new.grid(row=0, column=0, padx=(0, 4), sticky="ew")
        self.btn_load = ModernButton(btn_frame, text="LOAD", bg_color=COLOR_INFO, font=(FONT_FAMILY, 8, "bold"), command=self.load_selected_project)
        self.btn_load.grid(row=0, column=1, padx=2, sticky="ew")
        self.btn_delete = ModernButton(btn_frame, text="DELETE", bg_color=COLOR_DANGER, font=(FONT_FAMILY, 8, "bold"), command=self.delete_selected_project)
        self.btn_delete.grid(row=0, column=2, padx=(4, 0), sticky="ew")
        
        self.refresh_projects()
        
    def refresh_projects(self) -> None:
        self.project_listbox.delete(0, tk.END)
        if os.path.exists(DATABASE_DIR):
            for file in os.listdir(DATABASE_DIR):
                if file.endswith('.json'):
                    try:
                        with open(os.path.join(DATABASE_DIR, file), 'r', encoding='utf-8') as f:
                            self.project_listbox.insert(tk.END, json.load(f).get("name", file[:-5]))
                    except Exception: 
                        pass

    def open_new_project_dialog(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("Create New Project")
        dialog.geometry("360x450")
        dialog.configure(bg=COLOR_BG_LIGHT)
        dialog.resizable(False, False)
        dialog.transient(self.controller)
        dialog.grab_set()
        
        tk.Label(dialog, text="New Project Form", font=(FONT_FAMILY, 12, "bold"), bg=COLOR_BG_LIGHT, fg=COLOR_PRIMARY_DARK).pack(pady=(15, 10))
        entry_name = ModernEntry(dialog, "PROJECT NAME")
        entry_name.pack(fill="x", padx=20, pady=5)
        entry_sdesc = ModernEntry(dialog, "DESCRIPTION")
        entry_sdesc.pack(fill="x", padx=20, pady=5)
        tk.Label(dialog, text="INFO", font=(FONT_FAMILY, 8, "bold"), fg=COLOR_TEXT_DARK, bg=COLOR_BG_LIGHT, anchor="w").pack(fill="x", padx=20, pady=(5, 2))
        
        txt_frame = tk.Frame(dialog, bg="#CCCCCC", bd=1)
        txt_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        entry_fdesc = tk.Text(txt_frame, font=(FONT_FAMILY, 9), bg="#FFFFFF", relief="flat", height=4)
        entry_fdesc.pack(fill="both", expand=True, padx=1, pady=1)
        
        def submit_form():
            p_name, s_desc, f_desc = entry_name.get(), entry_sdesc.get(), entry_fdesc.get("1.0", tk.END).strip()
            if not p_name: 
                return messagebox.showerror("Error", "The project name cannot be empty!", parent=dialog)
            if os.path.exists(os.path.join(DATABASE_DIR, f"{p_name.lower().replace(' ', '_')}.json")):
                return messagebox.showerror("Error", "Project name already in use!", parent=dialog)
            try:
                Project(name=p_name, short_desc=s_desc, full_desc=f_desc).save()
                dialog.destroy()
                self.refresh_projects()
                messagebox.showinfo("Success", f"Project '{p_name}' created!", parent=self.controller)
            except Exception as e: 
                messagebox.showerror("Error", f"Failed to create project: {e}", parent=dialog)
                
        ModernButton(dialog, "SUBMIT", bg_color=COLOR_SUCCESS, command=submit_form).pack(fill="x", padx=20, pady=(0, 15))

    def load_selected_project(self) -> None:
        sel = self.project_listbox.curselection()
        if not sel: 
            return messagebox.showwarning("Warning", "Please select one project first!")
        self.controller.open_project(self.project_listbox.get(sel[0]))

    def delete_selected_project(self) -> None:
        sel = self.project_listbox.curselection()
        if not sel: 
            return messagebox.showwarning("Warning", "Please select one project first!")
        p_name = self.project_listbox.get(sel[0])
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete the project? '{p_name}'?"):
            if Project(name=p_name).delete():
                self.refresh_projects()
                messagebox.showinfo("Success", "Project has been successfully deleted!")
            else: 
                messagebox.showerror("Error", "Failed to delete project file!")


class DashboardView(tk.Frame):
    """Pallet dashboard"""
    def __init__(self, parent, controller) -> None:
        super().__init__(parent, bg=COLOR_PRIMARY)
        self.controller = controller
        self.active_edit_idx: Optional[int] = None
        
        header_frame = tk.Frame(self, bg=COLOR_PRIMARY)
        header_frame.pack(fill="x", padx=10, pady=5)
        
        self.lbl_project_name = tk.Label(header_frame, text="project_example", font=(FONT_FAMILY, 12, "bold"), fg="#000000", bg=COLOR_PRIMARY)
        self.lbl_project_name.pack(side="left")
        
        nav_frame = tk.Frame(header_frame, bg=COLOR_PRIMARY)
        nav_frame.pack(side="right")
        ModernButton(nav_frame, text="Home", bg_color="#D1C0C0", fg_color="#1E1E1E", font=(FONT_FAMILY, 8, "bold"), command=self.controller.go_home).pack(side="left", padx=2)
        ModernButton(nav_frame, text="Exit", bg_color="#D1C0C0", fg_color="#1E1E1E", font=(FONT_FAMILY, 8, "bold"), command=self.controller.quit).pack(side="left", padx=2)
        
        content_frame = tk.Frame(self, bg=COLOR_PRIMARY)
        content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        content_frame.columnconfigure(0, weight=1)
        for i, w in enumerate([4, 3, 3]): 
            content_frame.rowconfigure(i, weight=w, uniform="dash_rows")
        
        palette_outer = tk.Frame(content_frame, bg="#332222", bd=1)
        palette_outer.grid(row=0, column=0, sticky="nsew", pady=(0, 4))
        self.palette_scroll_frame = ScrollableFrame(palette_outer)
        self.palette_scroll_frame.pack(fill="both", expand=True)
        
        self.init_add_panel(content_frame)
        self.add_panel.grid(row=1, column=0, sticky="nsew", pady=(4, 4))
        
        self.init_edit_panel(content_frame)
        self.edit_panel_empty.grid(row=2, column=0, sticky="nsew", pady=(4, 0))
        
    def init_add_panel(self, parent: tk.Frame) -> None:
        self.add_panel = tk.Frame(parent, bg=COLOR_BG_LIGHT, bd=1, relief="solid")
        tk.Label(self.add_panel, text="ADD COLOR", font=(FONT_FAMILY, 9, "bold"), bg=COLOR_BG_LIGHT, fg=COLOR_TEXT_DARK).pack(anchor="w", padx=10, pady=(3, 1))
        
        form_wrap = tk.Frame(self.add_panel, bg=COLOR_BG_LIGHT)
        form_wrap.pack(fill="both", expand=True, padx=10)
        
        self.add_name_entry = ModernEntry(form_wrap, "COLOR NAME")
        self.add_name_entry.pack(fill="x", pady=(0, 2))
        
        row_fields = tk.Frame(form_wrap, bg=COLOR_BG_LIGHT)
        row_fields.pack(fill="x", pady=(0, 2))
        
        fmt_frame = tk.Frame(row_fields, bg=COLOR_BG_LIGHT)
        fmt_frame.pack(side="left", fill="x", expand=True, padx=(0, 4))
        tk.Label(fmt_frame, text="FORMAT", font=(FONT_FAMILY, 8, "bold"), fg=COLOR_TEXT_DARK, bg=COLOR_BG_LIGHT, anchor="w").pack(fill="x", pady=(0, 1))
        
        self.add_fmt_var = tk.StringVar(value="HEX")
        self.add_fmt_menu = ttk.Combobox(fmt_frame, textvariable=self.add_fmt_var, values=["HEX", "RGBA", "HSL"], state="readonly", font=(FONT_FAMILY, 9))
        self.add_fmt_menu.pack(fill="x", ipady=1)
        
        self.add_val_entry = ModernEntry(row_fields, "COLOR VALUE")
        self.add_val_entry.pack(side="right", fill="x", expand=True, padx=(4, 0))
        
        action_row = tk.Frame(form_wrap, bg=COLOR_BG_LIGHT)
        action_row.pack(fill="x", pady=(2, 2))
        
        self.add_preview_box = tk.Frame(action_row, width=30, height=25, bg="#DCD1D1", bd=1, relief="solid")
        self.add_preview_box.pack_propagate(False)
        self.add_preview_box.pack(side="left", padx=(0, 5))
        
        ModernButton(action_row, text="PREVIEW", bg_color=COLOR_PRIMARY_DARK, font=(FONT_FAMILY, 7, "bold"), command=self.preview_add_color).pack(side="left", padx=2)
        ModernButton(action_row, text="SUBMIT", bg_color=COLOR_SUCCESS, font=(FONT_FAMILY, 7, "bold"), command=self.submit_add_color).pack(side="right", padx=2)

    def init_edit_panel(self, parent: tk.Frame) -> None:
        self.edit_panel = tk.Frame(parent, bg=COLOR_BG_LIGHT, bd=1, relief="solid")
        self.edit_panel_empty = tk.Frame(parent, bg="#967474", bd=1, relief="solid")
        tk.Label(self.edit_panel_empty, text="EDIT COLOR\n\n(Select the color on the left\nClick the Edit button)", font=(FONT_FAMILY, 8, "bold"), bg="#967474", fg="#FFFFFF").pack(expand=True)
        
        tk.Label(self.edit_panel, text="EDIT COLOR", font=(FONT_FAMILY, 9, "bold"), bg=COLOR_BG_LIGHT, fg=COLOR_TEXT_DARK).pack(anchor="w", padx=10, pady=(3, 1))
        form_wrap = tk.Frame(self.edit_panel, bg=COLOR_BG_LIGHT)
        form_wrap.pack(fill="both", expand=True, padx=10)
        
        self.edit_name_entry = ModernEntry(form_wrap, "EDIT COLORNAME")
        self.edit_name_entry.pack(fill="x", pady=(0, 2))
        
        row_fields = tk.Frame(form_wrap, bg=COLOR_BG_LIGHT)
        row_fields.pack(fill="x", pady=(0, 2))
        
        fmt_frame = tk.Frame(row_fields, bg=COLOR_BG_LIGHT)
        fmt_frame.pack(side="left", fill="x", expand=True, padx=(0, 4))
        tk.Label(fmt_frame, text="INPUT FORMAT", font=(FONT_FAMILY, 8, "bold"), fg=COLOR_TEXT_DARK, bg=COLOR_BG_LIGHT, anchor="w").pack(fill="x", pady=(0, 1))
        
        self.edit_fmt_var = tk.StringVar(value="HEX")
        self.edit_fmt_menu = ttk.Combobox(fmt_frame, textvariable=self.edit_fmt_var, values=["HEX", "RGBA", "HSL"], state="readonly", font=(FONT_FAMILY, 9))
        self.edit_fmt_menu.pack(fill="x", ipady=1)
        
        self.edit_val_entry = ModernEntry(row_fields, "NEW COLOR VALUE")
        self.edit_val_entry.pack(side="right", fill="x", expand=True, padx=(4, 0))
        
        action_row = tk.Frame(form_wrap, bg=COLOR_BG_LIGHT)
        action_row.pack(fill="x", pady=(2, 2))
        
        self.edit_preview_box = tk.Frame(action_row, width=30, height=25, bg="#DCD1D1", bd=1, relief="solid")
        self.edit_preview_box.pack_propagate(False)
        self.edit_preview_box.pack(side="left")
        
        self.edit_val_entry.entry.bind("<KeyRelease>", self.on_edit_key_release)
        ModernButton(action_row, text="SAVE", bg_color=COLOR_SUCCESS, font=(FONT_FAMILY, 7, "bold"), command=self.save_edit_color).pack(side="right", padx=2)
        ModernButton(action_row, text="CANCEL", bg_color=COLOR_DANGER, font=(FONT_FAMILY, 7, "bold"), command=self.cancel_edit_mode).pack(side="right", padx=2)

    def load_project_details(self) -> None:
        proj = self.controller.current_project
        if proj:
            self.lbl_project_name.configure(text=proj.name)
            self.refresh_color_list()
            self.cancel_edit_mode()

    def refresh_color_list(self) -> None:
        for w in self.palette_scroll_frame.scrollable_frame.winfo_children(): 
            w.destroy()
        proj = self.controller.current_project
        if not proj or not proj.colors:
            tk.Label(self.palette_scroll_frame.scrollable_frame, text="There is no color yet.", font=(FONT_FAMILY, 8), fg="#FFF", bg=COLOR_PRIMARY_DARK, pady=10).pack(fill="x", padx=5)
        else:
            for i, item in enumerate(proj.colors): 
                self.create_color_item_widget(i, item)

    def copy_to_clipboard(self, widget: tk.Label, text: str) -> None:
        self.clipboard_clear()
        self.clipboard_append(text)
        widget.configure(text="Copied!", fg=COLOR_SUCCESS)
        self.after(1000, lambda: widget.configure(text=text, fg="#FFF"))

    def create_color_item_widget(self, index: int, color_item: Dict[str, str]) -> None:
        card_bg = "#8E6363"
        item_frame = tk.Frame(self.palette_scroll_frame.scrollable_frame, bg=card_bg, bd=1, relief="ridge")
        item_frame.pack(fill="x", padx=5, pady=3)
        
        color_preview_box = tk.Frame(item_frame, width=32, height=32, bg=color_item.get("hex", "#FFF"), bd=0)
        color_preview_box.pack_propagate(False)
        color_preview_box.pack(side="left", padx=5, pady=5)
        
        data_pane = tk.Frame(item_frame, bg=card_bg)
        data_pane.pack(side="left", fill="both", expand=True, pady=5)
        
        title_row = tk.Frame(data_pane, bg=card_bg)
        title_row.pack(fill="x", anchor="w")
        tk.Label(title_row, text=color_item.get("name", "Unnamed"), font=(FONT_FAMILY, 8, "bold"), fg="#FFFFFF", bg="#000000", padx=4).pack(side="left")
        
        formats_row = tk.Frame(data_pane, bg=card_bg)
        formats_row.pack(fill="x", anchor="w", pady=(4, 0))
        
        for fmt in ["hex", "rgba", "hsl"]:
            grp = tk.Frame(formats_row, bg=card_bg)
            grp.pack(fill="x", pady=1)
            tk.Label(grp, text=f"{fmt}: ", font=(FONT_FAMILY, 7, "bold"), fg="#E6DADA", bg=card_bg).pack(side="left")
            val_lbl = tk.Label(grp, text=color_item.get(fmt, ""), font=(FONT_FAMILY, 8), fg="#FFF", bg=COLOR_DARK_BOX, padx=4, pady=1, cursor="hand2")
            val_lbl.pack(side="left", fill="x", expand=True)
            val_lbl.bind("<Button-1>", lambda e, w=val_lbl, t=color_item.get(fmt, ""): self.copy_to_clipboard(w, t))
            
        action_wrap = tk.Frame(item_frame, bg=card_bg)
        action_wrap.pack(side="right", padx=5)
        tk.Button(action_wrap, text="✎", bg=COLOR_SUCCESS, fg="#FFFFFF", relief="flat", bd=0, font=(FONT_FAMILY, 9, "bold"), width=2, height=1, cursor="hand2", command=lambda i=index: self.enter_edit_mode(i)).pack(side="top", pady=1)
        tk.Button(action_wrap, text="🗑", bg=COLOR_DANGER, fg="#FFFFFF", relief="flat", bd=0, font=(FONT_FAMILY, 9, "bold"), width=2, height=1, cursor="hand2", command=lambda i=index: self.delete_color_item(i)).pack(side="top", pady=1)

    def preview_add_color(self) -> None:
        res = ColorConverter.convert_any_to_all(self.add_val_entry.get(), self.add_fmt_var.get())
        if res: 
            self.add_preview_box.configure(bg=res["hex"])
        else: 
            messagebox.showerror("Error", "Invalid color format!", parent=self)

    def submit_add_color(self) -> None:
        name = self.add_name_entry.get()
        if not name: 
            return messagebox.showerror("Error", "Color names cannot be empty!", parent=self)
        res = ColorConverter.convert_any_to_all(self.add_val_entry.get(), self.add_fmt_var.get())
        if not res: 
            return messagebox.showerror("Error", "Invalid color value!", parent=self)
        
        proj = self.controller.current_project
        if proj:
            proj.colors.append({"name": name, "hex": res["hex"], "rgba": res["rgba"], "hsl": res["hsl"]})
            proj.save()
            self.refresh_color_list()
            self.add_name_entry.set("")
            self.add_val_entry.set("")
            self.add_preview_box.configure(bg="#DCD1D1")

    def enter_edit_mode(self, index: int) -> None:
        proj = self.controller.current_project
        if not proj or index >= len(proj.colors): 
            return
        self.active_edit_idx = index
        color_item = proj.colors[index]
        self.edit_name_entry.set(color_item.get("name", ""))
        self.edit_val_entry.set(color_item.get("hex", ""))
        self.edit_fmt_var.set("HEX")
        self.edit_preview_box.configure(bg=color_item.get("hex", "#DCD1D1"))
        self.edit_panel_empty.grid_forget()
        self.edit_panel.grid(row=2, column=0, sticky="nsew", pady=(4, 0))

    def cancel_edit_mode(self) -> None:
        self.active_edit_idx = None
        self.edit_panel.grid_forget()
        self.edit_panel_empty.grid(row=2, column=0, sticky="nsew", pady=(4, 0))

    def on_edit_key_release(self, event) -> None:
        res = ColorConverter.convert_any_to_all(self.edit_val_entry.get(), self.edit_fmt_var.get())
        if res: 
            self.edit_preview_box.configure(bg=res["hex"])

    def save_edit_color(self) -> None:
        if self.active_edit_idx is None: 
            return
        name = self.edit_name_entry.get()
        if not name: 
            return messagebox.showerror("Error", "Color names cannot be empty!", parent=self)
        res = ColorConverter.convert_any_to_all(self.edit_val_entry.get(), self.edit_fmt_var.get())
        if not res: 
            return messagebox.showerror("Error", "Invalid color value!", parent=self)
        
        proj = self.controller.current_project
        if proj and self.active_edit_idx < len(proj.colors):
            proj.colors[self.active_edit_idx] = {"name": name, "hex": res["hex"], "rgba": res["rgba"], "hsl": res["hsl"]}
            proj.save()
            self.refresh_color_list()
            self.cancel_edit_mode()

    def delete_color_item(self, index: int) -> None:
        proj = self.controller.current_project
        if proj and messagebox.askyesno("Confirm", "Are you sure you want to remove this color?"):
            proj.colors.pop(index)
            proj.save()
            self.refresh_color_list()
            self.cancel_edit_mode()