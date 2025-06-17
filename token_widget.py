import tkinter as tk
from tkinter import messagebox
import time

class TokenWidget(tk.Frame):
    def __init__(self, parent, account_data, totp_generator, on_delete_callback):
        super().__init__(parent, bg='#f0f2f5')
        
        self.account_id, self.name, self.secret, self.issuer = account_data
        self.totp_generator = totp_generator
        self.on_delete_callback = on_delete_callback
        
        self.setup_ui()
        self.update_token()
    
    def setup_ui(self):
        """Interface moderna do token"""
        # Card container com sombra
        self.card = tk.Frame(
            self,
            bg='white',
            relief='flat',
            bd=0
        )
        self.card.pack(fill='x', padx=2, pady=2)
        
        # Adicionar efeito de sombra simulado
        shadow = tk.Frame(self, bg='#e0e0e0', height=2)
        shadow.pack(fill='x', padx=4)
        
        # Padding interno
        content_frame = tk.Frame(self.card, bg='white')
        content_frame.pack(fill='x', padx=20, pady=20)
        
        # Header com nome e botão delete
        header_frame = tk.Frame(content_frame, bg='white')
        header_frame.pack(fill='x', pady=(0, 15))
        
        # Nome da conta
        display_name = f"{self.issuer}" if self.issuer else "Conta"
        account_name = self.name if self.name else "Sem nome"
        
        # Emissor em destaque
        if self.issuer:
            issuer_label = tk.Label(
                header_frame,
                text=display_name,
                font=('Segoe UI', 11, 'bold'),
                fg='#202124',
                bg='white'
            )
            issuer_label.pack(anchor='w')
            
            # Nome da conta menor
            name_label = tk.Label(
                header_frame,
                text=account_name,
                font=('Segoe UI', 9),
                fg='#5f6368',
                bg='white'
            )
            name_label.pack(anchor='w')
        else:
            # Só o nome se não tiver emissor
            name_label = tk.Label(
                header_frame,
                text=account_name,
                font=('Segoe UI', 11, 'bold'),
                fg='#202124',
                bg='white'
            )
            name_label.pack(anchor='w')
        
        # Botão delete moderno
        self.delete_btn = tk.Button(
            header_frame,
            text="×",
            font=('Segoe UI', 16, 'bold'),
            fg='#9aa0a6',
            bg='white',
            activebackground='#fce8e6',
            activeforeground='#d93025',
            relief='flat',
            bd=0,
            width=2,
            height=1,
            cursor='hand2',
            command=self.confirm_delete
        )
        self.delete_btn.place(relx=1.0, rely=0.0, anchor='ne')
        
        # Hover effects para delete
        def on_delete_enter(e):
            self.delete_btn.configure(bg='#fce8e6', fg='#d93025')
        def on_delete_leave(e):
            self.delete_btn.configure(bg='white', fg='#9aa0a6')
            
        self.delete_btn.bind('<Enter>', on_delete_enter)
        self.delete_btn.bind('<Leave>', on_delete_leave)
        
        # Token frame
        token_frame = tk.Frame(content_frame, bg='white')
        token_frame.pack(fill='x', pady=(0, 15))
        
        # Token grande e destacado
        self.token_label = tk.Label(
            token_frame,
            text="000 000",
            font=('JetBrains Mono', 28, 'bold'),
            fg='#1a73e8',
            bg='white',
            cursor='hand2'
        )
        self.token_label.pack(side='left')
        
        # Click para copiar no token
        self.token_label.bind('<Button-1>', lambda e: self.copy_token())
        
        # Botão copiar estilizado
        self.copy_btn = tk.Button(
            token_frame,
            text="📋",
            font=('Segoe UI', 14),
            fg='#5f6368',
            bg='white',
            activebackground='#e8f0fe',
            activeforeground='#1a73e8',
            relief='flat',
            bd=0,
            width=3,
            height=1,
            cursor='hand2',
            command=self.copy_token
        )
        self.copy_btn.pack(side='right', padx=(10, 0))
        
        # Hover effects para copy
        def on_copy_enter(e):
            self.copy_btn.configure(bg='#e8f0fe', fg='#1a73e8')
        def on_copy_leave(e):
            self.copy_btn.configure(bg='white', fg='#5f6368')
            
        self.copy_btn.bind('<Enter>', on_copy_enter)
        self.copy_btn.bind('<Leave>', on_copy_leave)
        
        # Barra de progresso moderna
        progress_container = tk.Frame(content_frame, bg='white', height=6)
        progress_container.pack(fill='x', pady=(0, 10))
        progress_container.pack_propagate(False)
        
        # Background da barra
        self.progress_bg = tk.Frame(progress_container, bg='#e8eaed', height=4)
        self.progress_bg.pack(fill='x', pady=1)
        
        # Barra de progresso
        self.progress_bar = tk.Frame(self.progress_bg, bg='#1a73e8', height=4)
        self.progress_bar.pack(side='left', fill='y')
        
        # Tempo restante
        time_frame = tk.Frame(content_frame, bg='white')
        time_frame.pack(fill='x')
        
        self.time_label = tk.Label(
            time_frame,
            text="30s",
            font=('Segoe UI', 9),
            fg='#5f6368',
            bg='white'
        )
        self.time_label.pack(side='left')
        
        # Status do token
        self.status_label = tk.Label(
            time_frame,
            text="✓ Ativo",
            font=('Segoe UI', 9),
            fg='#137333',
            bg='white'
        )
        self.status_label.pack(side='right')
    
    def update_token(self):
        """Atualiza token e interface"""
        try:
            # Gera token
            token = self.totp_generator.generate_token(self.secret)
            
            if token != "ERROR" and len(token) == 6:
                # Formata token (000 000)
                formatted_token = f"{token[:3]} {token[3:]}"
                self.token_label.configure(text=formatted_token, fg='#1a73e8')
                self.status_label.configure(text="✓ Ativo", fg='#137333')
            else:
                self.token_label.configure(text="ERROR", fg='#d93025')
                self.status_label.configure(text="✗ Erro", fg='#d93025')
            
            # Atualiza barra de progresso
            remaining = self.totp_generator.get_time_remaining()
            progress = ((30 - remaining) / 30)
            
            # Largura da barra baseada no progresso
            try:
                container_width = self.progress_bg.winfo_width()
                if container_width > 1:  # Evita erro quando ainda não foi renderizado
                    bar_width = int(container_width * progress)
                    self.progress_bar.configure(width=bar_width)
            except:
                pass
            
            # Muda cor quando está acabando
            if remaining <= 5:
                self.progress_bar.configure(bg='#ea4335')
                self.time_label.configure(fg='#ea4335')
            else:
                self.progress_bar.configure(bg='#1a73e8')
                self.time_label.configure(fg='#5f6368')
            
            # Atualiza tempo
            self.time_label.configure(text=f"{remaining}s")
            
        except Exception as e:
            self.token_label.configure(text="ERROR", fg='#d93025')
            self.status_label.configure(text="✗ Erro", fg='#d93025')
            print(f"Erro ao atualizar token: {e}")
    
    def copy_token(self):
        """Copia token para clipboard"""
        try:
            token = self.totp_generator.generate_token(self.secret)
            if token != "ERROR":
                # Limpa clipboard e adiciona token
                self.clipboard_clear()
                self.clipboard_append(token)
                
                # Feedback visual
                original_text = self.copy_btn['text']
                original_color = self.copy_btn['fg']
                
                self.copy_btn.configure(text="✓", fg='#137333')
                self.after(1500, lambda: self.copy_btn.configure(
                    text=original_text, 
                    fg=original_color
                ))
                
                # Atualiza status temporariamente
                self.status_label.configure(text="📋 Copiado", fg='#137333')
                self.after(2000, lambda: self.status_label.configure(
                    text="✓ Ativo", 
                    fg='#137333'
                ))
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao copiar: {e}")
    
    def confirm_delete(self):
        """Confirma exclusão com diálogo moderno"""
        # Criar diálogo customizado
        dialog = tk.Toplevel(self)
        dialog.title("Confirmar exclusão")
        dialog.geometry("350x200")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg='white')
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (350 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"350x200+{x}+{y}")
        
        # Conteúdo
        content = tk.Frame(dialog, bg='white', padx=30, pady=30)
        content.pack(fill='both', expand=True)
        
        # Ícone
        icon_label = tk.Label(
            content,
            text="⚠️",
            font=('Segoe UI', 24),
            bg='white'
        )
        icon_label.pack(pady=(0, 15))
        
        # Título
        title_label = tk.Label(
            content,
            text="Excluir conta?",
            font=('Segoe UI', 14, 'bold'),
            fg='#202124',
            bg='white'
        )
        title_label.pack(pady=(0, 10))
        
        # Mensagem
        display_name = self.issuer if self.issuer else self.name
        msg_label = tk.Label(
            content,
            text=f"A conta '{display_name}' será removida\npermanentemente.",
            font=('Segoe UI', 10),
            fg='#5f6368',
            bg='white',
            justify='center'
        )
        msg_label.pack(pady=(0, 20))
        
        # Botões
        button_frame = tk.Frame(content, bg='white')
        button_frame.pack(fill='x')
        
        def cancel():
            dialog.destroy()
            
        def confirm():
            dialog.destroy()
            self.on_delete_callback(self.account_id)
        
        # Botão cancelar
        cancel_btn = tk.Button(
            button_frame,
            text="Cancelar",
            font=('Segoe UI', 10),
            fg='#1a73e8',
            bg='white',
            activebackground='#e8f0fe',
            activeforeground='#1a73e8',
            relief='flat',
            bd=1,
            padx=20,
            pady=8,
            cursor='hand2',
            command=cancel
        )
        cancel_btn.pack(side='right', padx=(10, 0))
        
        # Botão excluir
        delete_btn = tk.Button(
            button_frame,
            text="Excluir",
            font=('Segoe UI', 10, 'bold'),
            fg='white',
            bg='#d93025',
            activebackground='#b52d20',
            activeforeground='white',
            relief='flat',
            bd=0,
            padx=20,
            pady=8,
            cursor='hand2',
            command=confirm
        )
        delete_btn.pack(side='right')