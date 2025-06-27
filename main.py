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
        # Debug: mostrar informações do ambiente
        print("🔐 Iniciando Python Authenticator...")
        print("📱 Aplicativo similar ao Google Authenticator")
        print("✨ Suporte para TOTP (Time-based One-Time Password)")
        print("-" * 50)
        
        # Informações de debug
        print(f"Python executável: {sys.executable}")
        print(f"Diretório atual: {os.getcwd()}")
        print(f"Executável congelado: {getattr(sys, 'frozen', False)}")
        
        if getattr(sys, 'frozen', False):
            print(f"Diretório temporário: {sys._MEIPASS}")
            print(f"Executável: {sys.executable}")
        
        # Verifica dependências
        if not check_dependencies():
            sys.exit(1)
        
        # Importa e executa o app principal
        from authenticator_app import AuthenticatorApp
        
        # Criar instância do app
        app = AuthenticatorApp()
        
        # Debug: mostrar informações do banco
        db_info = app.database.get_database_info()
        print("\n📁 Informações do banco de dados:")
        for key, value in db_info.items():
            print(f"  {key}: {value}")
        print("-" * 50)
        
        # Executar aplicativo
        app.run()
        
    except KeyboardInterrupt:
        print("\n👋 Aplicativo encerrado pelo usuário")
        sys.exit(0)
    except Exception as e:
        error_msg = f"Erro fatal: {str(e)}"
        print(f"❌ {error_msg}")
        
        # Tentar mostrar messagebox se possível
        try:
            messagebox.showerror("Erro Fatal", error_msg)
        except:
            pass
            
        sys.exit(1)

if __name__ == "__main__":
    # NÃO mudar diretório de trabalho quando executável
    # Deixar que cada módulo determine onde salvar seus arquivos
    main()