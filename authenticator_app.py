import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from database import Database
from totp_generator import TOTPGenerator
from token_widget import TokenWidget
from add_account_dialog import AddAccountDialog

class AuthenticatorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.database = Database()
        self.totp_generator = TOTPGenerator()
        self.token_widgets = []
        self.update_thread_running = True
        
        self.setup_ui()
        self.setup_styles()
        self.load_accounts()
        self.start_update_thread()
    
    def setup_ui(self):
        """Configura a interface principal"""
        self.root.title("🔐 Python Authenticator")
        self.root.geometry("420x700")
        self.root.minsize(380, 500)
        self.root.configure(bg='#f0f2f5')
        
        # Frame principal com gradiente
        main_frame = tk.Frame(self.root, bg='#f0f2f5')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Header moderno
        header_frame = tk.Frame(main_frame, bg='#f0f2f5', height=80)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Título principal
        title_label = tk.Label(
            header_frame,
            text="🔐 Authenticator",
            font=('Segoe UI', 22, 'bold'),
            fg='#1a73e8',
            bg='#f0f2f5'
        )
        title_label.pack(pady=(15, 5))
        
        subtitle_label = tk.Label(
            header_frame,
            text="Códigos de verificação seguros",
            font=('Segoe UI', 10),
            fg='#5f6368',
            bg='#f0f2f5'
        )
        subtitle_label.pack()
        
        # Botão adicionar estilizado
        add_button_frame = tk.Frame(main_frame, bg='#f0f2f5')
        add_button_frame.pack(fill='x', pady=(0, 20))
        
        self.add_btn = tk.Button(
            add_button_frame,
            text="+ Adicionar conta",
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
        
        # Efeito hover no botão
        def on_enter(e):
            self.add_btn.configure(bg='#1557b0')
        def on_leave(e):
            self.add_btn.configure(bg='#1a73e8')
            
        self.add_btn.bind('<Enter>', on_enter)
        self.add_btn.bind('<Leave>', on_leave)
        
        # Container para tokens
        self.setup_scrollable_frame(main_frame)
        
        # Status bar moderno
        status_frame = tk.Frame(main_frame, bg='#f0f2f5', height=30)
        status_frame.pack(side='bottom', fill='x', pady=(15, 0))
        status_frame.pack_propagate(False)
        
        self.status_bar = tk.Label(
            status_frame,
            text="✓ Pronto",
            font=('Segoe UI', 9),
            fg='#5f6368',
            bg='#f0f2f5'
        )
        self.status_bar.pack(pady=8)
    
    def setup_scrollable_frame(self, parent):
        """Configura área scrollável moderna"""
        # Container principal
        container = tk.Frame(parent, bg='#f0f2f5')
        container.pack(fill='both', expand=True)
        
        # Canvas com scrollbar customizada
        self.canvas = tk.Canvas(
            container,
            bg='#f0f2f5',
            highlightthickness=0,
            bd=0
        )
        
        # Scrollbar customizada
        scrollbar_frame = tk.Frame(container, bg='#f0f2f5', width=10)
        scrollbar_frame.pack(side='right', fill='y')
        
        self.scrollbar = tk.Scale(
            scrollbar_frame,
            orient='vertical',
            showvalue=False,
            bd=0,
            highlightthickness=0,
            troughcolor='#e8eaed',
            bg='#dadce0',
            activebackground='#9aa0a6',
            width=8,
            sliderlength=20
        )
        self.scrollbar.pack(fill='y', padx=2)
        
        # Frame scrollável
        self.scrollable_frame = tk.Frame(self.canvas, bg='#f0f2f5')
        
        # Configuração do scroll
        def configure_scroll(event):
            self.canvas.configure(scrollregion=self.canvas.bbox('all'))
            
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            
        self.scrollable_frame.bind('<Configure>', configure_scroll)
        self.canvas.bind('<MouseWheel>', on_mousewheel)
        
        # Vincular scrollbar
        def on_scroll(*args):
            self.canvas.yview(*args)
            
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.configure(command=on_scroll)
        
        # Criar janela no canvas
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        self.canvas.pack(side='left', fill='both', expand=True)
        
        # Ajustar largura do frame
        def configure_canvas(event):
            canvas_width = event.width
            self.canvas.itemconfig(self.canvas.find_all()[0], width=canvas_width)
            
        self.canvas.bind('<Configure>', configure_canvas)
    
    def setup_styles(self):
        """Aplica estilos modernos"""
        # Configurar cursor padrão
        self.root.configure(cursor='arrow')
        
        # Configurações globais de fonte
        default_font = ('Segoe UI', 9)
        self.root.option_add('*Font', default_font)
    
    def load_accounts(self):
        """Carrega contas com interface moderna"""
        self.clear_tokens()
        
        accounts = self.database.get_all_accounts()
        
        if not accounts:
            # Tela vazia estilizada
            empty_frame = tk.Frame(self.scrollable_frame, bg='#f0f2f5')
            empty_frame.pack(expand=True, fill='both', pady=50)
            
            # Ícone grande
            icon_label = tk.Label(
                empty_frame,
                text="🔒",
                font=('Segoe UI', 48),
                bg='#f0f2f5',
                fg='#dadce0'
            )
            icon_label.pack(pady=(0, 20))
            
            # Texto principal
            title_label = tk.Label(
                empty_frame,
                text="Nenhuma conta adicionada",
                font=('Segoe UI', 16, 'bold'),
                fg='#5f6368',
                bg='#f0f2f5'
            )
            title_label.pack(pady=(0, 10))
            
            # Subtexto
            subtitle_label = tk.Label(
                empty_frame,
                text="Clique em 'Adicionar conta' para começar\na proteger suas contas com 2FA",
                font=('Segoe UI', 11),
                fg='#9aa0a6',
                bg='#f0f2f5',
                justify='center'
            )
            subtitle_label.pack()
            
            self.token_widgets.append(empty_frame)
        else:
            # Criar widgets para cada conta
            for i, account in enumerate(accounts):
                self.create_token_widget(account, i == 0)
        
        self.update_status(f"{len(accounts)} conta(s)", "success")
    
    def create_token_widget(self, account_data, is_first=False):
        """Cria widget moderno para token"""
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
                self.update_status(f"✓ Conta '{result['name']}' adicionada", "success")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao adicionar conta: {e}")
                self.update_status("✗ Erro ao adicionar conta", "error")
    
    def delete_account(self, account_id):
        """Remove conta"""
        try:
            self.database.delete_account(account_id)
            self.load_accounts()
            self.update_status("✓ Conta removida", "success")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao remover conta: {e}")
            self.update_status("✗ Erro ao remover", "error")
    
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
        
        # Limpa após 3 segundos se não for erro
        if status_type != "error":
            self.root.after(3000, lambda: self.status_bar.configure(text="✓ Pronto", fg="#5f6368"))
    
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
    
    def on_closing(self):
        """Fecha aplicação"""
        self.update_thread_running = False
        self.root.destroy()
    
    def run(self):
        """Executa o app"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Centralizar janela
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (420 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"420x700+{x}+{y}")
        
        self.root.mainloop()