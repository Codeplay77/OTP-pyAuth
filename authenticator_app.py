import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import sys
import os
from database import Database
from totp_generator import TOTPGenerator
from token_widget import TokenWidget
from add_account_dialog import AddAccountDialog
from config_manager import ConfigManager

# System tray imports
try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False

class AuthenticatorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.config_manager = ConfigManager()
        self.database = Database()
        self.totp_generator = TOTPGenerator()
        self.token_widgets = []
        self.update_thread_running = True
        self.is_hidden = False
        
        # System tray
        self.tray_icon = None
        self.tray_thread = None
        
        self.setup_ui()
        self.setup_styles()
        self.setup_hotkeys()
        self.setup_tray()
        self.load_accounts()
        self.start_update_thread()
    
    def setup_ui(self):
        """Configura a interface principal"""
        self.root.title("Python Authenticator")
        self.root.geometry("420x700")
        self.root.minsize(380, 500)
        self.root.configure(bg='#f0f2f5')
        
        # Interceptar fechamento da janela
        self.root.protocol("WM_DELETE_WINDOW", self.hide_to_tray)
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f2f5')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#f0f2f5', height=80)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Título
        title_label = tk.Label(
            header_frame,
            text="Python Authenticator",
            font=('Segoe UI', 22, 'bold'),
            fg='#1a73e8',
            bg='#f0f2f5'
        )
        title_label.pack(pady=(15, 5))
        
        subtitle_label = tk.Label(
            header_frame,
            text="TOTP Authentication Manager",
            font=('Segoe UI', 10),
            fg='#5f6368',
            bg='#f0f2f5'
        )
        subtitle_label.pack()
        
        # Botão adicionar
        add_button_frame = tk.Frame(main_frame, bg='#f0f2f5')
        add_button_frame.pack(fill='x', pady=(0, 20))
        
        self.add_btn = tk.Button(
            add_button_frame,
            text="Add Account",
            font=('Segoe UI', 11, 'bold'),
            fg='white',
            bg='#1a73e8',
            activebackground='#1557b0',
            activeforeground='white',
            relief='flat',
            bd=0,
            pady=12,
            cursor='hand2',
            command=self.add_account
        )
        self.add_btn.pack(fill='x')
        
        # Container para tokens
        self.setup_scrollable_frame(main_frame)
        
        # Status bar
        status_frame = tk.Frame(main_frame, bg='#f0f2f5', height=30)
        status_frame.pack(side='bottom', fill='x', pady=(15, 0))
        status_frame.pack_propagate(False)
        
        hotkey = self.config_manager.get('hotkeys.toggle_window', 'ctrl+shift+a')
        self.status_bar = tk.Label(
            status_frame,
            text=f"Ready - {hotkey.upper()} to toggle",
            font=('Segoe UI', 9),
            fg='#5f6368',
            bg='#f0f2f5'
        )
        self.status_bar.pack(pady=8)
    
    def setup_scrollable_frame(self, parent):
        """Configura área scrollável"""
        container = tk.Frame(parent, bg='#f0f2f5')
        container.pack(fill='both', expand=True)
        
        self.canvas = tk.Canvas(
            container,
            bg='#f0f2f5',
            highlightthickness=0,
            bd=0
        )
        
        scrollbar = tk.Scrollbar(
            container,
            orient='vertical',
            command=self.canvas.yview,
            bg='#dadce0',
            troughcolor='#e8eaed',
            width=12
        )
        
        self.scrollable_frame = tk.Frame(self.canvas, bg='#f0f2f5')
        
        def configure_scroll(event):
            self.canvas.configure(scrollregion=self.canvas.bbox('all'))
            
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            
        self.scrollable_frame.bind('<Configure>', configure_scroll)
        self.canvas.bind('<MouseWheel>', on_mousewheel)
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        
        self.canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        def configure_canvas(event):
            canvas_width = event.width
            self.canvas.itemconfig(canvas_frame, width=canvas_width)
            
        self.canvas.bind('<Configure>', configure_canvas)
    
    def setup_styles(self):
        """Aplica estilos"""
        self.root.configure(cursor='arrow')
        default_font = ('Segoe UI', 9)
        self.root.option_add('*Font', default_font)
    
    def setup_hotkeys(self):
        """Configura atalhos de teclado globais"""
        try:
            import keyboard
            
            hotkeys = self.config_manager.get_hotkeys()
            toggle_hotkey = hotkeys.get('toggle_window', 'ctrl+shift+a')
            add_account_hotkey = hotkeys.get('add_account', 'ctrl+shift+n')
            
            keyboard.add_hotkey(toggle_hotkey, self.toggle_window)
            
            if add_account_hotkey and add_account_hotkey != 'disabled':
                keyboard.add_hotkey(add_account_hotkey, self.add_account)
            
        except ImportError:
            pass
        except Exception as e:
            print(f"Error setting up hotkeys: {e}")
    
    def create_tray_icon(self):
        """Cria ícone para a bandeja do sistema"""
        width = height = 64
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        margin = 8
        draw.ellipse(
            [margin, margin, width-margin, height-margin],
            fill='#1a73e8',
            outline='#1557b0',
            width=2
        )
        
        text = "2FA"
        bbox = draw.textbbox((0, 0), text, font=None)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2 - 2
        
        draw.text((x, y), text, fill='white')
        
        return image
    
    def setup_tray(self):
        """Configura system tray"""
        if not TRAY_AVAILABLE or not self.config_manager.get('tray.enabled', True):
            return
        
        try:
            menu = pystray.Menu(
                pystray.MenuItem("Show/Hide", self.toggle_window, default=True),
                pystray.MenuItem("Add Account", self.add_account),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Exit", self.quit_app)
            )
            
            icon_image = self.create_tray_icon()
            tooltip = self.config_manager.get('tray.tooltip', 'Python Authenticator')
            
            self.tray_icon = pystray.Icon(
                "PythonAuthenticator",
                icon_image,
                tooltip,
                menu
            )
            
        except Exception as e:
            print(f"Error setting up system tray: {e}")
            self.tray_icon = None
    
    def start_tray(self):
        """Inicia system tray em thread separada"""
        if self.tray_icon and TRAY_AVAILABLE:
            def run_tray():
                try:
                    self.tray_icon.run()
                except Exception:
                    pass
            
            self.tray_thread = threading.Thread(target=run_tray, daemon=True)
            self.tray_thread.start()
    
    def hide_to_tray(self):
        """Minimiza para a bandeja do sistema"""
        if TRAY_AVAILABLE and self.tray_icon and self.config_manager.get('tray.hide_on_close', True):
            self.root.withdraw()
            self.is_hidden = True
            
            if not self.tray_thread or not self.tray_thread.is_alive():
                self.start_tray()
        else:
            self.root.iconify()
    
    def show_window(self):
        """Mostra a janela"""
        if self.is_hidden:
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            self.is_hidden = False
            self.position_window()
    
    def toggle_window(self):
        """Alterna entre mostrar e esconder"""
        if self.is_hidden or self.root.state() == 'withdrawn':
            self.show_window()
        else:
            self.hide_to_tray()
    
    def position_window(self, position=None):
        """Posiciona a janela conforme configuração"""
        self.root.update_idletasks()
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        window_width = 420
        window_height = screen_height - 50
        
        ui_config = self.config_manager.get_ui_config()
        position = position or ui_config.get('window_position', 'right')
        margin = ui_config.get('margin', 20)
        
        # Calcular posição
        if position == 'right':
            x = screen_width - window_width - margin
            y = margin
        elif position == 'left':
            x = margin
            y = margin
        elif position == 'center':
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
        elif position == 'top_right':
            x = screen_width - window_width - margin
            y = margin
        elif position == 'bottom_right':
            x = screen_width - window_width - margin
            y = screen_height - window_height - margin
        elif position == 'custom':
            x = ui_config.get('custom_x', 100)
            y = ui_config.get('custom_y', 100)
        else:
            x = screen_width - window_width - margin
            y = margin
        
        # Garantir que caiba na tela
        x = max(0, min(x, screen_width - window_width))
        y = max(0, min(y, screen_height - window_height))
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Always on top se configurado
        if ui_config.get('always_on_top', False):
            self.root.attributes('-topmost', True)
    
    def quit_app(self):
        """Sai completamente do aplicativo"""
        self.update_thread_running = False
        
        if self.tray_icon:
            self.tray_icon.stop()
        
        self.root.quit()
        self.root.destroy()
        sys.exit(0)
    
    def load_accounts(self):
        """Carrega contas"""
        self.clear_tokens()
        
        accounts = self.database.get_all_accounts()
        
        if not accounts:
            empty_frame = tk.Frame(self.scrollable_frame, bg='#f0f2f5')
            empty_frame.pack(expand=True, fill='both', pady=50)
            
            icon_label = tk.Label(
                empty_frame,
                text="🔒",
                font=('Segoe UI', 48),
                bg='#f0f2f5',
                fg='#dadce0'
            )
            icon_label.pack(pady=(0, 20))
            
            title_label = tk.Label(
                empty_frame,
                text="No accounts added",
                font=('Segoe UI', 16, 'bold'),
                fg='#5f6368',
                bg='#f0f2f5'
            )
            title_label.pack(pady=(0, 10))
            
            subtitle_label = tk.Label(
                empty_frame,
                text="Click 'Add Account' to start\nprotecting your accounts with 2FA",
                font=('Segoe UI', 11),
                fg='#9aa0a6',
                bg='#f0f2f5',
                justify='center'
            )
            subtitle_label.pack()
            
            self.token_widgets.append(empty_frame)
        else:
            for i, account in enumerate(accounts):
                self.create_token_widget(account, i == 0)
        
        self.update_status(f"{len(accounts)} account(s)", "success")
    
    def create_token_widget(self, account_data, is_first=False):
        """Cria widget para token"""
        margin_top = 0 if is_first else 15
        
        widget = TokenWidget(
            self.scrollable_frame,
            account_data,
            self.totp_generator,
            self.delete_account
        )
        widget.pack(fill='x', pady=(margin_top, 0))
        self.token_widgets.append(widget)
    
    def clear_tokens(self):
        """Remove todos os widgets"""
        for widget in self.token_widgets:
            widget.destroy()
        self.token_widgets.clear()
    
    def add_account(self):
        """Abre diálogo para adicionar conta"""
        if self.is_hidden:
            self.show_window()
        
        dialog = AddAccountDialog(self.root, self.totp_generator)
        result = dialog.show()
        
        if result:
            try:
                self.database.add_account(
                    result['name'],
                    result['secret'],
                    result['issuer']
                )
                self.load_accounts()
                self.update_status(f"Account '{result['name']}' added", "success")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error adding account: {e}")
                self.update_status("Error adding account", "error")
    
    def delete_account(self, account_id):
        """Remove conta"""
        try:
            self.database.delete_account(account_id)
            self.load_accounts()
            self.update_status("Account removed", "success")
        except Exception as e:
            messagebox.showerror("Error", f"Error removing account: {e}")
            self.update_status("Error removing account", "error")
    
    def refresh_tokens(self):
        """Atualiza todos os tokens"""
        for widget in self.token_widgets:
            if hasattr(widget, 'update_token'):
                widget.update_token()
    
    def update_status(self, message, status_type="info"):
        """Atualiza status com cores"""
        colors = {
            "success": "#137333",
            "error": "#d93025",
            "info": "#5f6368"
        }
        
        self.status_bar.configure(text=message, fg=colors.get(status_type, "#5f6368"))
        
        if status_type != "error":
            hotkey = self.config_manager.get('hotkeys.toggle_window', 'ctrl+shift+a')
            self.root.after(3000, lambda: self.status_bar.configure(
                text=f"Ready - {hotkey.upper()} to toggle", 
                fg="#5f6368"
            ))
    
    def start_update_thread(self):
        """Thread para atualização automática"""
        def update_loop():
            while self.update_thread_running:
                try:
                    self.root.after(0, self.refresh_tokens)
                    time.sleep(1)
                except:
                    break
        
        self.update_thread = threading.Thread(target=update_loop, daemon=True)
        self.update_thread.start()
    
    def run(self):
        """Executa o app"""
        self.position_window()
        self.root.mainloop()