"""
Translation GUI - Modern GUI application for managing translations
"""

import sys
import os
import json
from pathlib import Path
from typing import Optional, List, Dict

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import tkinter.font as tkFont
from tkinter import scrolledtext

from translation_manager import TranslationManager, TranslationEntry, MinecraftFormatting


class MinecraftPreviewText(tk.Text):
    """Custom Text widget for displaying Minecraft formatting preview"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, height=3, wrap=tk.WORD, state=tk.DISABLED, **kwargs)
        self.setup_tags()
    
    def setup_tags(self):
        """Setup text tags for Minecraft formatting"""
        # Color tags
        for code, (name, color) in MinecraftFormatting.FORMATTING_CODES.items():
            if color:
                self.tag_configure(f"color_{code[1:]}", foreground=color)
        
        # Formatting tags
        self.tag_configure("bold", font=("TkDefaultFont", 10, "bold"))
        self.tag_configure("italic", font=("TkDefaultFont", 10, "italic"))
        self.tag_configure("underline", underline=True)
        self.tag_configure("strikethrough", overstrike=True)
    
    def update_preview(self, text: str, bg_color: str = "#ffffff"):
        """Update the preview with formatted text"""
        self.configure(state=tk.NORMAL, bg=bg_color)
        self.delete(1.0, tk.END)
        
        if not text.strip():
            self.insert(1.0, "Preview will appear here...")
            self.configure(state=tk.DISABLED)
            return
        
        segments = MinecraftFormatting.get_formatted_segments(text)
        
        for segment_text, color, bold, italic, underline, strikethrough in segments:
            if not segment_text:
                continue
            
            # Build list of tags to apply
            tags = []
            
            # Add color tag
            for code, (name, seg_color) in MinecraftFormatting.FORMATTING_CODES.items():
                if seg_color == color:
                    tags.append(f"color_{code[1:]}")
                    break
            
            # Add formatting tags
            if bold:
                tags.append("bold")
            if italic:
                tags.append("italic")
            if underline:
                tags.append("underline")
            if strikethrough:
                tags.append("strikethrough")
            
            # Insert text with tags
            start_pos = self.index(tk.INSERT)
            self.insert(tk.INSERT, segment_text)
            end_pos = self.index(tk.INSERT)
            
            # Apply tags
            for tag in tags:
                self.tag_add(tag, start_pos, end_pos)
        
        self.configure(state=tk.DISABLED)


class ModernStyle:
    """Modern styling for the GUI"""
    
    LIGHT_THEME = {
        'bg': '#ffffff',
        'fg': '#2c3e50',
        'select_bg': '#3498db',
        'select_fg': '#ffffff',
        'entry_bg': '#f8f9fa',
        'button_bg': '#ecf0f1',
        'button_hover': '#bdc3c7',
        'accent': '#3498db',
        'success': '#27ae60',
        'warning': '#f39c12',
        'error': '#e74c3c',
        'sidebar_bg': '#f1f2f6',
        'header_bg': '#34495e',
        'border': '#bdc3c7',
        'preview_bg': '#ffffff',
        'text_bg': '#ffffff'
    }
    
    DARK_THEME = {
        'bg': '#1e1e1e',
        'fg': '#ffffff',
        'select_bg': '#0078d4',
        'select_fg': '#ffffff',
        'entry_bg': '#2d2d30',
        'button_bg': '#3c3c3c',
        'button_hover': '#484848',
        'accent': '#0078d4',
        'success': '#16c60c',
        'warning': '#ffb900',
        'error': '#e81123',
        'sidebar_bg': '#252526',
        'header_bg': '#383838',
        'border': '#3c3c3c',
        'preview_bg': '#1e1e1e',
        'text_bg': '#1e1e1e'
    }


class FormatCodeDialog:
    """Dialog for inserting Minecraft formatting codes"""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Minecraft Formatting Codes")
        self.dialog.geometry("450x550")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Apply theme
        theme = ModernStyle.DARK_THEME if hasattr(parent, 'dark_mode') and parent.dark_mode.get() else ModernStyle.LIGHT_THEME
        self.dialog.configure(bg=theme['bg'])
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the formatting code dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Select Formatting Code", 
                               font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Instructions
        inst_label = ttk.Label(main_frame, text="Double-click to insert, or select and click Insert",
                              font=("Arial", 9))
        inst_label.pack(pady=(0, 10))
        
        # Create notebook for categories
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Color codes tab
        color_frame = ttk.Frame(notebook)
        notebook.add(color_frame, text="Colors")
        
        color_scroll = tk.Scrollbar(color_frame)
        color_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        color_listbox = tk.Listbox(color_frame, yscrollcommand=color_scroll.set)
        color_scroll.config(command=color_listbox.yview)
        
        for code, (name, color) in MinecraftFormatting.FORMATTING_CODES.items():
            if color:  # Only color codes
                # Create a colored display
                display_text = f"{code} - {name}"
                index = color_listbox.size()
                color_listbox.insert(tk.END, display_text)
                # Try to set the foreground color (may not work on all systems)
                try:
                    color_listbox.itemconfig(index, {'fg': color})
                except:
                    pass  # Fallback to default color if not supported
        
        color_listbox.pack(fill=tk.BOTH, expand=True)
        color_listbox.bind('<Double-Button-1>', lambda e: self.select_code(color_listbox))
        
        # Format codes tab
        format_frame = ttk.Frame(notebook)
        notebook.add(format_frame, text="Formatting")
        
        format_scroll = tk.Scrollbar(format_frame)
        format_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        format_listbox = tk.Listbox(format_frame, yscrollcommand=format_scroll.set)
        format_scroll.config(command=format_listbox.yview)
        
        for code, (name, color) in MinecraftFormatting.FORMATTING_CODES.items():
            if not color:  # Only formatting codes
                format_listbox.insert(tk.END, f"{code} - {name}")
        
        format_listbox.pack(fill=tk.BOTH, expand=True)
        format_listbox.bind('<Double-Button-1>', lambda e: self.select_code(format_listbox))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Insert", command=self.insert_selected).pack(side=tk.RIGHT)
        
        # Store references
        self.color_listbox = color_listbox
        self.format_listbox = format_listbox
        self.notebook = notebook
        
    def select_code(self, listbox):
        """Handle code selection"""
        selection = listbox.curselection()
        if selection:
            item = listbox.get(selection[0])
            code = item.split(' - ')[0]
            self.result = code
            self.dialog.destroy()
    
    def insert_selected(self):
        """Insert the currently selected code"""
        current_tab = self.notebook.select()
        tab_text = self.notebook.tab(current_tab, "text")
        
        if tab_text == "Colors":
            self.select_code(self.color_listbox)
        else:
            self.select_code(self.format_listbox)


class TranslationGUI:
    """Main GUI application for translation management"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("StarT Translations Manager")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Initialize variables
        self.translation_manager = None
        self.current_language = tk.StringVar()
        self.current_category = tk.StringVar()
        self.current_subcategory = tk.StringVar()
        self.search_var = tk.StringVar()
        self.dark_mode = tk.BooleanVar(value=False)
        
        # Apply modern styling
        self.setup_style()
        self.setup_ui()
        self.bind_events()
        
        # Try to load default workspace
        default_lang_path = Path(__file__).parent.parent / "lang"
        if default_lang_path.exists():
            self.load_workspace(str(default_lang_path))
    
    def setup_style(self):
        """Setup modern styling"""
        self.style = ttk.Style()
        
        # Configure ttk styles
        self.style.theme_use('clam')
        
        self.update_theme()
    
    def update_theme(self):
        """Update theme colors"""
        theme = ModernStyle.DARK_THEME if self.dark_mode.get() else ModernStyle.LIGHT_THEME
        
        # Configure root
        self.root.configure(bg=theme['bg'])
        
        # Configure ttk styles
        self.style.configure('TFrame', background=theme['bg'])
        self.style.configure('TLabel', background=theme['bg'], foreground=theme['fg'])
        self.style.configure('TButton', background=theme['button_bg'], foreground=theme['fg'])
        self.style.configure('TEntry', fieldbackground=theme['entry_bg'], foreground=theme['fg'])
        self.style.configure('TCombobox', fieldbackground=theme['entry_bg'], foreground=theme['fg'])
        
        # Treeview styling
        self.style.configure('Treeview', background=theme['entry_bg'], foreground=theme['fg'],
                           fieldbackground=theme['entry_bg'])
        self.style.configure('Treeview.Heading', background=theme['header_bg'], foreground=theme['fg'])
        self.style.configure('Treeview.Item', background=theme['entry_bg'], foreground=theme['fg'])
        
        # Scrolled text styling
        self.style.configure('TScrollbar', background=theme['button_bg'], 
                           troughcolor=theme['bg'], bordercolor=theme['border'])
        
        # Custom styles
        self.style.configure('Sidebar.TFrame', background=theme['sidebar_bg'])
        self.style.configure('Header.TLabel', background=theme['header_bg'], foreground=theme['fg'],
                           font=('Arial', 11, 'bold'))
        
        # Update existing text widgets
        if hasattr(self, 'english_text'):
            self.english_text.configure(bg=theme['text_bg'], fg=theme['fg'])
        if hasattr(self, 'translation_text'):
            self.translation_text.configure(bg=theme['text_bg'], fg=theme['fg'])
        if hasattr(self, 'preview_text'):
            self.preview_text.configure(bg=theme['preview_bg'], fg=theme['fg'])
            # Update preview with current theme
            current_text = ""
            if hasattr(self, 'translation_text'):
                current_text = self.translation_text.get(1.0, tk.END).strip()
            self.preview_text.update_preview(current_text, theme['preview_bg'])
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top toolbar
        self.setup_toolbar(main_container)
        
        # Main content area
        content_paned = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        content_paned.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Left sidebar
        self.setup_sidebar(content_paned)
        
        # Right main area
        self.setup_main_area(content_paned)
        
        # Status bar
        self.setup_status_bar(main_container)
    
    def setup_toolbar(self, parent):
        """Setup the top toolbar"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # File operations
        ttk.Button(toolbar, text="Open Workspace", command=self.open_workspace).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Save All", command=self.save_all).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Language operations
        ttk.Button(toolbar, text="Add Language", command=self.add_language).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Validate", command=self.validate_current_language).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Theme toggle
        ttk.Checkbutton(toolbar, text="Dark Mode", variable=self.dark_mode,
                       command=self.toggle_theme).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Search
        search_frame = ttk.Frame(toolbar)
        search_frame.pack(side=tk.RIGHT, padx=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=(5, 5))
        search_entry.bind('<KeyRelease>', self.on_search)
        
        ttk.Button(search_frame, text="Clear", command=self.clear_search).pack(side=tk.LEFT)
    
    def setup_sidebar(self, parent):
        """Setup the left sidebar"""
        sidebar = ttk.Frame(parent, style='Sidebar.TFrame', width=300)
        parent.add(sidebar, weight=0)
        
        # Language selection
        lang_frame = ttk.LabelFrame(sidebar, text="Language", padding="10")
        lang_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        self.language_combo = ttk.Combobox(lang_frame, textvariable=self.current_language, 
                                          state="readonly", width=25)
        self.language_combo.pack(fill=tk.X)
        self.language_combo.bind('<<ComboboxSelected>>', self.on_language_change)
        
        # Category selection
        cat_frame = ttk.LabelFrame(sidebar, text="Category", padding="10")
        cat_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.category_combo = ttk.Combobox(cat_frame, textvariable=self.current_category,
                                          state="readonly", width=25)
        self.category_combo.pack(fill=tk.X, pady=(0, 5))
        self.category_combo.bind('<<ComboboxSelected>>', self.on_category_change)
        
        self.subcategory_combo = ttk.Combobox(cat_frame, textvariable=self.current_subcategory,
                                             state="readonly", width=25)
        self.subcategory_combo.pack(fill=tk.X)
        self.subcategory_combo.bind('<<ComboboxSelected>>', self.refresh_translations)
        
        # Statistics
        stats_frame = ttk.LabelFrame(sidebar, text="Statistics", padding="10")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.stats_label = ttk.Label(stats_frame, text="No language selected", justify=tk.LEFT)
        self.stats_label.pack(fill=tk.X)
        
        # Filter options
        filter_frame = ttk.LabelFrame(sidebar, text="Filters", padding="10")
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.show_translated = tk.BooleanVar(value=True)
        self.show_untranslated = tk.BooleanVar(value=True)
        self.show_formatted = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(filter_frame, text="Show Translated", variable=self.show_translated,
                       command=self.refresh_translations).pack(anchor=tk.W)
        ttk.Checkbutton(filter_frame, text="Show Untranslated", variable=self.show_untranslated,
                       command=self.refresh_translations).pack(anchor=tk.W)
        ttk.Checkbutton(filter_frame, text="Show Formatted", variable=self.show_formatted,
                       command=self.refresh_translations).pack(anchor=tk.W)
    
    def setup_main_area(self, parent):
        """Setup the main content area"""
        main_area = ttk.Frame(parent)
        parent.add(main_area, weight=1)
        
        # Translation table
        table_frame = ttk.Frame(main_area)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Table with scrollbars
        table_container = ttk.Frame(table_frame)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        columns = ('Key', 'English', 'Translation', 'Status')
        self.tree = ttk.Treeview(table_container, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.tree.heading('Key', text='Key')
        self.tree.heading('English', text='English Text')
        self.tree.heading('Translation', text='Translation')
        self.tree.heading('Status', text='Status')
        
        # Column widths
        self.tree.column('Key', width=200, minwidth=150)
        self.tree.column('English', width=300, minwidth=200)
        self.tree.column('Translation', width=300, minwidth=200)
        self.tree.column('Status', width=100, minwidth=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        table_container.rowconfigure(0, weight=1)
        table_container.columnconfigure(0, weight=1)
        
        # Bind tree selection
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.tree.bind('<Double-1>', self.edit_selected_translation)
        
        # Translation editor
        editor_frame = ttk.LabelFrame(main_area, text="Translation Editor", padding="10")
        editor_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Key and English text (read-only)
        info_frame = ttk.Frame(editor_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(info_frame, text="Key:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.key_label = ttk.Label(info_frame, text="", foreground="blue")
        self.key_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(info_frame, text="English:").grid(row=1, column=0, sticky=tk.NW, padx=(0, 5))
        self.english_text = scrolledtext.ScrolledText(info_frame, height=3, state=tk.DISABLED, wrap=tk.WORD)
        self.english_text.grid(row=1, column=1, sticky='ew', pady=(2, 0))
        
        info_frame.columnconfigure(1, weight=1)
        
        # Translation input
        trans_frame = ttk.Frame(editor_frame)
        trans_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(trans_frame, text="Translation:").pack(anchor=tk.W)
        
        # Text area with formatting buttons
        text_frame = ttk.Frame(trans_frame)
        text_frame.pack(fill=tk.X)
        
        self.translation_text = scrolledtext.ScrolledText(text_frame, height=4, wrap=tk.WORD)
        self.translation_text.pack(fill=tk.BOTH, expand=True)
        self.translation_text.bind('<KeyRelease>', self.on_translation_change)
        
        # Formatting toolbar
        format_frame = ttk.Frame(trans_frame)
        format_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(format_frame, text="Add Format Code", command=self.add_format_code).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(format_frame, text="Strip Formatting", command=self.strip_formatting).pack(side=tk.LEFT, padx=(0, 5))
        
        # Quick color buttons
        quick_colors = [
            ('§4', 'Red', '#AA0000'),
            ('§c', 'Light Red', '#FF5555'),
            ('§6', 'Gold', '#FFAA00'),
            ('§e', 'Yellow', '#FFFF55'),
            ('§2', 'Green', '#00AA00'),
            ('§a', 'Light Green', '#55FF55'),
            ('§b', 'Aqua', '#55FFFF'),
            ('§9', 'Blue', '#5555FF'),
            ('§d', 'Pink', '#FF55FF'),
            ('§5', 'Purple', '#AA00AA'),
            ('§f', 'White', '#FFFFFF'),
            ('§7', 'Gray', '#AAAAAA'),
            ('§r', 'Reset', None)
        ]
        
        # Create quick color frame
        color_frame = ttk.Frame(format_frame)
        color_frame.pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Label(color_frame, text="Quick:").pack(side=tk.LEFT, padx=(0, 5))
        
        for code, name, color in quick_colors[:6]:  # Show first 6 colors
            btn = tk.Button(color_frame, text=code[1:], width=2, height=1,
                           command=lambda c=code: self.insert_quick_format(c))
            if color:
                try:
                    btn.configure(bg=color, fg='white' if code in ['§4', '§2', '§9', '§5'] else 'black')
                except:
                    pass  # Fallback if color not supported
            btn.pack(side=tk.LEFT, padx=1)
        
        # Preview
        preview_frame = ttk.Frame(trans_frame)
        preview_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(preview_frame, text="Preview:").pack(anchor=tk.W)
        self.preview_text = MinecraftPreviewText(preview_frame)
        self.preview_text.pack(fill=tk.X)
        
        # Action buttons
        button_frame = ttk.Frame(editor_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Save Translation", command=self.save_current_translation).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Reset", command=self.reset_current_translation).pack(side=tk.LEFT, padx=(5, 0))
        
    def setup_status_bar(self, parent):
        """Setup the status bar"""
        self.status_bar = ttk.Label(parent, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def bind_events(self):
        """Bind keyboard and other events"""
        self.root.bind('<Control-o>', lambda e: self.open_workspace())
        self.root.bind('<Control-s>', lambda e: self.save_all())
        self.root.bind('<Control-f>', lambda e: self.focus_search())
        self.root.bind('<F5>', lambda e: self.refresh_translations())
        self.root.bind('<Control-m>', lambda e: self.add_format_code())  # Ctrl+M for format codes
    
    def focus_search(self):
        """Focus on search entry"""
        # Find search entry and focus
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Frame):
                        for grandchild in child.winfo_children():
                            if isinstance(grandchild, ttk.Entry):
                                grandchild.focus_set()
                                return
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.update_theme()
        self.status_bar.config(text=f"Switched to {'Dark' if self.dark_mode.get() else 'Light'} mode")
    
    def open_workspace(self):
        """Open a translation workspace"""
        folder = filedialog.askdirectory(title="Select Language Folder")
        if folder:
            self.load_workspace(folder)
    
    def load_workspace(self, folder_path: str):
        """Load translations from a workspace folder"""
        try:
            self.translation_manager = TranslationManager(folder_path)
            self.translation_manager.scan_translations()
            
            # Update UI
            self.update_language_list()
            self.update_category_list()
            self.status_bar.config(text=f"Loaded workspace: {folder_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load workspace: {e}")
            self.status_bar.config(text="Failed to load workspace")
    
    def update_language_list(self):
        """Update the language combobox"""
        if not self.translation_manager:
            return
        
        languages = self.translation_manager.get_available_languages()
        self.language_combo['values'] = languages
        
        # Select first non-English language if available
        for lang in languages:
            if lang != 'en_us':
                self.current_language.set(lang)
                break
        else:
            if languages:
                self.current_language.set(languages[0])
        
        self.on_language_change()
    
    def update_category_list(self):
        """Update the category combobox"""
        if not self.translation_manager:
            return
        
        categories = self.translation_manager.get_categories()
        self.category_combo['values'] = categories
        
        if categories:
            self.current_category.set(categories[0])
            self.on_category_change()
    
    def on_language_change(self, event=None):
        """Handle language selection change"""
        self.update_stats()
        self.refresh_translations()
    
    def on_category_change(self, event=None):
        """Handle category selection change"""
        if not self.translation_manager:
            return
        
        category = self.current_category.get()
        subcategories = ['All'] + self.translation_manager.get_subcategories(category)
        self.subcategory_combo['values'] = subcategories
        self.current_subcategory.set('All')
        self.refresh_translations()
    
    def update_stats(self):
        """Update translation statistics"""
        if not self.translation_manager:
            self.stats_label.config(text="No workspace loaded")
            return
        
        language = self.current_language.get()
        if not language:
            self.stats_label.config(text="No language selected")
            return
        
        stats = self.translation_manager.get_translation_stats(language)
        if stats:
            text = f"Total: {stats['total']}\n"
            text += f"Translated: {stats['translated']}\n"
            text += f"Untranslated: {stats['untranslated']}\n"
            text += f"Progress: {stats['percentage']}%"
            self.stats_label.config(text=text)
        else:
            self.stats_label.config(text="No data available")
    
    def refresh_translations(self, event=None):
        """Refresh the translation table"""
        if not self.translation_manager:
            return
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        language = self.current_language.get()
        category = self.current_category.get()
        subcategory = self.current_subcategory.get()
        
        if not language:
            return
        
        # Get translations
        translations = self.translation_manager.get_translations(
            language,
            category if category else None,
            subcategory if subcategory != 'All' else None
        )
        
        # Apply filters
        filtered_translations = []
        for entry in translations:
            has_translation = bool(entry.translated_text.strip())
            
            if not has_translation and not self.show_untranslated.get():
                continue
            if has_translation and not self.show_translated.get():
                continue
            if entry.has_formatting and not self.show_formatted.get():
                continue
            
            # Apply search filter
            search_query = self.search_var.get().lower()
            if search_query:
                if (search_query not in entry.key.lower() and
                    search_query not in entry.english_text.lower() and
                    search_query not in entry.translated_text.lower()):
                    continue
            
            filtered_translations.append(entry)
        
        # Populate tree
        for entry in filtered_translations:
            status = "Translated" if entry.translated_text.strip() else "Untranslated"
            if entry.has_formatting:
                status += " (Formatted)"
            
            # Truncate long text for display
            english_display = entry.english_text[:100] + "..." if len(entry.english_text) > 100 else entry.english_text
            trans_display = entry.translated_text[:100] + "..." if len(entry.translated_text) > 100 else entry.translated_text
            
            self.tree.insert('', tk.END, values=(
                entry.key,
                english_display,
                trans_display,
                status
            ), tags=(entry.key,))
        
        self.status_bar.config(text=f"Showing {len(filtered_translations)} translations")
    
    def on_search(self, event=None):
        """Handle search input"""
        self.refresh_translations()
    
    def clear_search(self):
        """Clear search and refresh"""
        self.search_var.set("")
        self.refresh_translations()
    
    def on_tree_select(self, event=None):
        """Handle tree selection"""
        selection = self.tree.selection()
        if not selection:
            self.clear_editor()
            return
        
        item = self.tree.item(selection[0])
        key = item['values'][0]
        
        if not self.translation_manager:
            return
        
        language = self.current_language.get()
        if language in self.translation_manager.translations:
            entry = self.translation_manager.translations[language].get(key)
            if entry:
                self.load_editor(entry)
    
    def clear_editor(self):
        """Clear the translation editor"""
        self.key_label.config(text="")
        self.english_text.config(state=tk.NORMAL)
        self.english_text.delete(1.0, tk.END)
        self.english_text.config(state=tk.DISABLED)
        self.translation_text.delete(1.0, tk.END)
        theme = ModernStyle.DARK_THEME if self.dark_mode.get() else ModernStyle.LIGHT_THEME
        self.preview_text.update_preview("", theme['preview_bg'])
    
    def load_editor(self, entry: TranslationEntry):
        """Load a translation entry into the editor"""
        self.key_label.config(text=entry.key)
        
        self.english_text.config(state=tk.NORMAL)
        self.english_text.delete(1.0, tk.END)
        self.english_text.insert(1.0, entry.english_text)
        self.english_text.config(state=tk.DISABLED)
        
        self.translation_text.delete(1.0, tk.END)
        self.translation_text.insert(1.0, entry.translated_text)
        
        self.update_preview()
    
    def on_translation_change(self, event=None):
        """Handle translation text change"""
        self.update_preview()
    
    def update_preview(self):
        """Update the formatting preview"""
        text = self.translation_text.get(1.0, tk.END).strip()
        theme = ModernStyle.DARK_THEME if self.dark_mode.get() else ModernStyle.LIGHT_THEME
        self.preview_text.update_preview(text, theme['preview_bg'])
    
    def add_format_code(self):
        """Open dialog to add formatting code"""
        dialog = FormatCodeDialog(self.root)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            # Insert at cursor position
            cursor_pos = self.translation_text.index(tk.INSERT)
            self.translation_text.insert(cursor_pos, dialog.result)
            self.update_preview()
    
    def insert_quick_format(self, code: str):
        """Insert a quick formatting code at cursor position"""
        cursor_pos = self.translation_text.index(tk.INSERT)
        self.translation_text.insert(cursor_pos, code)
        self.translation_text.focus_set()
        self.update_preview()
    
    def strip_formatting(self):
        """Remove all formatting codes from current translation"""
        text = self.translation_text.get(1.0, tk.END).strip()
        stripped = MinecraftFormatting.strip_formatting(text)
        self.translation_text.delete(1.0, tk.END)
        self.translation_text.insert(1.0, stripped)
        self.update_preview()
    
    def save_current_translation(self):
        """Save the currently edited translation"""
        key = self.key_label.cget("text")
        if not key or not self.translation_manager:
            return
        
        language = self.current_language.get()
        translation = self.translation_text.get(1.0, tk.END).strip()
        
        if self.translation_manager.update_translation(language, key, translation):
            self.refresh_translations()
            self.update_stats()
            self.status_bar.config(text=f"Saved translation for: {key}")
        else:
            messagebox.showerror("Error", "Failed to save translation")
    
    def reset_current_translation(self):
        """Reset current translation to original value"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        key = item['values'][0]
        
        if not self.translation_manager:
            return
        
        language = self.current_language.get()
        if language in self.translation_manager.translations:
            entry = self.translation_manager.translations[language].get(key)
            if entry:
                self.load_editor(entry)
    
    def edit_selected_translation(self, event=None):
        """Focus translation editor when double-clicking tree item"""
        self.translation_text.focus_set()
    
    def add_language(self):
        """Add a new language"""
        if not self.translation_manager:
            messagebox.showerror("Error", "No workspace loaded")
            return
        
        language_code = simpledialog.askstring("Add Language", "Enter language code (e.g., fr_fr, de_de):")
        if language_code:
            language_code = language_code.lower()
            if self.translation_manager.add_language(language_code):
                self.update_language_list()
                self.current_language.set(language_code)
                self.status_bar.config(text=f"Added language: {language_code}")
            else:
                messagebox.showerror("Error", "Language already exists or no base language found")
    
    def save_all(self):
        """Save all translations"""
        if not self.translation_manager:
            messagebox.showerror("Error", "No workspace loaded")
            return
        
        try:
            self.translation_manager.save_translations()
            messagebox.showinfo("Success", "All translations saved successfully")
            self.status_bar.config(text="All translations saved")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save translations: {e}")
    
    def validate_current_language(self):
        """Validate current language translations"""
        if not self.translation_manager:
            messagebox.showerror("Error", "No workspace loaded")
            return
        
        language = self.current_language.get()
        if not language:
            messagebox.showerror("Error", "No language selected")
            return
        
        issues = self.translation_manager.validate_translations(language)
        if issues:
            issue_text = "\n".join([f"{key}: {issue}" for key, issue in issues[:20]])  # Show first 20
            if len(issues) > 20:
                issue_text += f"\n... and {len(issues) - 20} more issues"
            
            messagebox.showwarning("Validation Issues", f"Found {len(issues)} issues:\n\n{issue_text}")
        else:
            messagebox.showinfo("Validation", "No issues found!")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    app = TranslationGUI()
    app.run()


if __name__ == "__main__":
    main()
