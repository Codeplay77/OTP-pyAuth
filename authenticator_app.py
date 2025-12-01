"""
Python Authenticator - Main Application Module

This module implements the main GUI application for managing TOTP-based
two-factor authentication codes, similar to Google Authenticator.

Author: Codeplay
Date: June 2025
License: See LICENSE file
Python Version: 3.8+

Dependencies:
    - tkinter: GUI framework
    - threading: Background token updates
    - keyboard: Global hotkey support (optional)
    - pystray: System tray integration (optional)
"""

# Standard library imports
import sys
import os
import time
import threading
from typing import Optional, List

# Third-party imports - GUI
import tkinter as tk
from tkinter import ttk, messagebox

# Local application imports
from database import Database
from totp_generator import TOTPGenerator
from token_widget import TokenWidget
from add_account_dialog import AddAccountDialog
from config_manager import ConfigManager

# Optional system tray support
try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False


class AuthenticatorApp:
    """
    Main application class for Python Authenticator.
    
    This class manages the entire lifecycle of the application including:
    - GUI initialization and management
    - TOTP token generation and display
    - Database operations for account storage
    - System tray integration
    - Global hotkey registration
    - Background thread for token updates
    
    Attributes:
        root (tk.Tk): Main application window
        config_manager (ConfigManager): Application configuration handler
        database (Database): Database interface for account storage
        totp_generator (TOTPGenerator): TOTP token generation engine
        token_widgets (List[TokenWidget]): List of active token display widgets
        update_thread_running (bool): Flag to control background update thread
        is_hidden (bool): Window visibility state
        dialog_open (bool): Prevents multiple dialog instances
        tray_icon (Optional[pystray.Icon]): System tray icon instance
        tray_thread (Optional[threading.Thread]): System tray thread
        keyboard_module: Reference to keyboard module for hotkey cleanup
        hotkeys_registered (List[str]): List of registered global hotkeys
        
    Thread Safety:
        - Uses root.after() for thread-safe GUI updates
        - Background thread only schedules work on main thread
        - Widget existence validated before operations
    """
    
    def __init__(self) -> None:
        """
        Initialize the authenticator application.
        
        Sets up all necessary components including GUI, database connection,
        configuration management, and optional features like system tray
        and global hotkeys.
        
        Raises:
            Exception: If critical components fail to initialize
        """
        # Core Tkinter setup
        self.root = tk.Tk()
        
        # Application components
        self.config_manager = ConfigManager()
        self.database = Database()
        self.totp_generator = TOTPGenerator()
        
        # UI state management
        self.token_widgets: List[TokenWidget] = []
        self.update_thread_running = True
        self.is_hidden = False
        self.dialog_open = False  # Prevents multiple dialog instances
        
        # System tray components (optional feature)
        self.tray_icon: Optional[pystray.Icon] = None
        self.tray_thread: Optional[threading.Thread] = None
        
        # Global hotkey management (optional feature)
        self.keyboard_module = None
        self.hotkeys_registered: List[str] = []
        
        # Initialize application components in order
        self.setup_ui()
        self.setup_styles()
        self.setup_hotkeys()
        self.setup_tray()
        self.load_accounts()
        self.start_update_thread()
    
    def setup_ui(self) -> None:
        """Configure the main user interface.
        
        Sets up the main window with:
        - Window properties (title, size, colors)
        - Header section with branding
        - Add account button
        - Scrollable token container
        - Status bar with hotkey information
        
        Design follows Material Design principles with Google-like aesthetics.
        """
        self.root.title("Python Authenticator")
        self.root.geometry("420x700")
        self.root.minsize(380, 500)
        self.root.configure(bg='#f0f2f5')
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind('<Escape>', lambda e: None)
        main_frame = tk.Frame(self.root, bg='#f0f2f5')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        header_frame = tk.Frame(main_frame, bg='#f0f2f5', height=80)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
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
        self.setup_scrollable_frame(main_frame)
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
    
    def setup_hotkeys(self) -> None:
        """Configure global keyboard shortcuts.
        
        Registers system-wide hotkeys for:
        - Toggle window visibility (default: Ctrl+Shift+A)
        - Add new account (default: Ctrl+Shift+N)
        
        Uses the 'keyboard' module which requires elevated permissions
        on some systems. Gracefully handles ImportError if module unavailable.
        
        All hotkeys are thread-safe and use root.after() to schedule
        actions on the main GUI thread.
        
        Note:
            On Linux, this may require running as sudo.
            On Windows, may trigger UAC prompts.
        """
        try:
            import keyboard
            self.keyboard_module = keyboard
            
            hotkeys = self.config_manager.get_hotkeys()
            toggle_hotkey = hotkeys.get('toggle_window', 'ctrl+shift+a')
            add_account_hotkey = hotkeys.get('add_account', 'ctrl+shift+n')
            
            if toggle_hotkey and toggle_hotkey != 'disabled':
                try:
                    keyboard.add_hotkey(toggle_hotkey, self._hotkey_toggle_window)
                    self.hotkeys_registered.append(toggle_hotkey)
                    print(f"✓ Hotkey registrado: {toggle_hotkey} (toggle window)")
                except Exception as e:
                    print(f"✗ Erro ao registrar hotkey {toggle_hotkey}: {e}")
            
            if add_account_hotkey and add_account_hotkey != 'disabled':
                try:
                    keyboard.add_hotkey(add_account_hotkey, self._hotkey_add_account)
                    self.hotkeys_registered.append(add_account_hotkey)
                    print(f"✓ Hotkey registrado: {add_account_hotkey} (add account)")
                except Exception as e:
                    print(f"✗ Erro ao registrar hotkey {add_account_hotkey}: {e}")
            
        except ImportError:
            print("⚠ Módulo 'keyboard' não encontrado. Atalhos globais desabilitados.")
            print("  Instale com: pip install keyboard")
            self.keyboard_module = None
        except Exception as e:
            print(f"✗ Erro ao configurar hotkeys: {e}")
            self.keyboard_module = None
    
    def _hotkey_toggle_window(self):
        """Wrapper thread-safe para atalho de toggle"""
        try:
            self.root.after(0, self.toggle_window)
        except Exception as e:
            print(f"Erro no hotkey toggle: {e}")
    
    def _hotkey_add_account(self):
        """Wrapper thread-safe para atalho de adicionar conta"""
        try:
            self.root.after(0, self.add_account)
        except Exception as e:
            print(f"Erro no hotkey add account: {e}")
    
    def cleanup_hotkeys(self):
        """Remove todos os atalhos registrados"""
        if self.keyboard_module and self.hotkeys_registered:
            try:
                for hotkey in self.hotkeys_registered:
                    try:
                        self.keyboard_module.remove_hotkey(hotkey)
                        print(f"✓ Hotkey removido: {hotkey}")
                    except Exception as e:
                        print(f"✗ Erro ao remover hotkey {hotkey}: {e}")
                self.hotkeys_registered.clear()
            except Exception as e:
                print(f"Erro ao limpar hotkeys: {e}")
    
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
    
    def on_closing(self):
        """Chamado quando usuário tenta fechar a janela"""
        try:
            if self.config_manager.get('tray.enabled', True) and TRAY_AVAILABLE:
                self.hide_to_tray()
            else:
                from tkinter import messagebox
                if messagebox.askyesno("Confirmar saída", 
                                      "Deseja realmente sair do aplicativo?",
                                      parent=self.root):
                    self.quit_app()
        except Exception as e:
            print(f"Erro ao fechar: {e}")
            self.quit_app()
    
    def hide_to_tray(self):
        """Minimiza para a bandeja do sistema"""
        if TRAY_AVAILABLE and self.tray_icon and self.config_manager.get('tray.hide_on_close', True):
            self.root.withdraw()
            self.is_hidden = True
            if not self.tray_thread or not self.tray_thread.is_alive():
                self.start_tray()
        else:
            self.root.iconify()
            self.is_hidden = False
    
    def show_window(self):
        """Mostra a janela"""
        try:
            if self.is_hidden or self.root.state() == 'withdrawn':
                self.root.deiconify()
                self.is_hidden = False
            
            if self.root.state() == 'iconic':
                self.root.deiconify()
        
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.after(100, lambda: self.root.attributes('-topmost', 
                           self.config_manager.get('ui.always_on_top', False)))
            self.root.focus_force()
            self.position_window()
        except Exception as e:
            print(f"Erro ao mostrar janela: {e}")
    
    def toggle_window(self):
        """Alterna entre mostrar e esconder"""
        try:
            current_state = self.root.state()
            
            if self.is_hidden or current_state == 'withdrawn':
                self.show_window()
            elif current_state == 'iconic':
                self.show_window()
            else:
                self.hide_to_tray()
        except Exception as e:
            print(f"Erro ao alternar janela: {e}")
            try:
                self.show_window()
            except:
                pass
    
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
        
        x = max(0, min(x, screen_width - window_width))
        y = max(0, min(y, screen_height - window_height))
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        if ui_config.get('always_on_top', False):
            self.root.attributes('-topmost', True)
    
    def quit_app(self):
        """Sai completamente do aplicativo"""
        print("\n🔄 Encerrando aplicativo...")

        self.update_thread_running = False
        if hasattr(self, 'update_thread') and self.update_thread.is_alive():
            print("  ⏳ Aguardando thread de atualização...")
            self.update_thread.join(timeout=2)
        print("  🎹 Removendo hotkeys...")
        self.cleanup_hotkeys()
        if self.tray_icon:
            print("  📱 Parando system tray...")
            try:
                self.tray_icon.stop()
            except Exception as e:
                print(f"  ⚠ Erro ao parar tray: {e}")
        print("  🪟 Fechando janela...")
        try:
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            print(f"  ⚠ Erro ao fechar janela: {e}")
        
        print("✓ Aplicativo encerrado")
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
        if self.dialog_open:
            print("⚠ Diálogo já está aberto")
            return
        
        if self.is_hidden:
            self.show_window()
        
        self.dialog_open = True
        try:
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
        finally:
            self.dialog_open = False
    
    def delete_account(self, account_id):
        """Remove conta"""
        try:
            accounts = self.database.get_all_accounts()
            if not any(acc[0] == account_id for acc in accounts):
                messagebox.showwarning("Aviso", "Conta não encontrada.")
                self.load_accounts()
                return
            
            self.database.delete_account(account_id)
            self.load_accounts()
            self.update_status("Account removed", "success")
        except Exception as e:
            error_msg = f"Error removing account: {str(e)}"
            print(f"✗ {error_msg}")
            messagebox.showerror("Error", error_msg)
            self.update_status("Error removing account", "error")
    
    def refresh_tokens(self):
        """Atualiza todos os tokens"""
        try:
            widgets_copy = self.token_widgets.copy()
            
            for widget in widgets_copy:
                if widget and hasattr(widget, 'update_token'):
                    try:
                        if widget.winfo_exists():
                            widget.update_token()
                    except tk.TclError:
                        if widget in self.token_widgets:
                            self.token_widgets.remove(widget)
                    except Exception as e:
                        print(f"Erro ao atualizar widget: {e}")
        except Exception as e:
            print(f"Erro ao atualizar tokens: {e}")
    
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
                    if self.root and self.root.winfo_exists():
                        self.root.after(0, self.refresh_tokens)
                    else:
                        break
                    time.sleep(1)
                except tk.TclError:
                    break
                except Exception as e:
                    print(f"Erro na thread de atualização: {e}")
                    break
        
        self.update_thread = threading.Thread(target=update_loop, daemon=True)
        self.update_thread.start()
    
    def run(self):
        """Executa o app"""
        self.position_window()
        self.root.mainloop()