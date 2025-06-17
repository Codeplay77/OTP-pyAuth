#!/usr/bin/env python3
"""
Python Authenticator - App similar ao Google Authenticator
Autor: Claude AI
Data: 2025

Aplicativo para gerar tokens TOTP (Time-based One-Time Password)
compatível com serviços que usam autenticação de dois fatores.
"""

import sys
import os
from tkinter import messagebox

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    required_modules = ['pyotp', 'cryptography', 'PIL']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        error_msg = f"""
Módulos necessários não encontrados: {', '.join(missing_modules)}

Para instalar, execute:
pip install -r requirements.txt

Ou instale individualmente:
pip install pyotp cryptography Pillow
        """
        messagebox.showerror("Dependências Faltando", error_msg)
        return False
    
    return True

def main():
    """Função principal do aplicativo"""
    try:
        # Verifica dependências
        if not check_dependencies():
            sys.exit(1)
        
        # Importa e executa o app principal
        from authenticator_app import AuthenticatorApp
        
        print("🔐 Iniciando Python Authenticator...")
        print("📱 Aplicativo similar ao Google Authenticator")
        print("✨ Suporte para TOTP (Time-based One-Time Password)")
        print("-" * 50)
        
        app = AuthenticatorApp()
        app.run()
        
    except KeyboardInterrupt:
        print("\n👋 Aplicativo encerrado pelo usuário")
        sys.exit(0)
    except Exception as e:
        error_msg = f"Erro fatal: {str(e)}"
        print(f"❌ {error_msg}")
        messagebox.showerror("Erro Fatal", error_msg)
        sys.exit(1)

if __name__ == "__main__":
    # Configura o diretório de trabalho
    if hasattr(sys, '_MEIPASS'):
        # Executando como executável PyInstaller
        os.chdir(sys._MEIPASS)
    else:
        # Executando como script Python
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    main()