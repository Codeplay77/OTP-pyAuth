#!/usr/bin/env python3
"""
Script para recuperar chaves OTP do banco de dados criptografado
"""

import sqlite3
import os
from cryptography.fernet import Fernet
import base64

def load_encryption_key():
    """Carrega a chave de criptografia"""
    key_path = "key.key"
    
    if not os.path.exists(key_path):
        print("Arquivo key.key não encontrado!")
        return None
    
    try:
        with open(key_path, 'rb') as key_file:
            key = key_file.read()
        
        cipher = Fernet(key)
        print("Chave de criptografia carregada com sucesso")
        return cipher
    
    except Exception as e:
        print(f"Erro ao carregar chave: {e}")
        return None

def decrypt_secret(cipher, encrypted_secret):
    """Descriptografa uma chave secreta"""
    try:
        return cipher.decrypt(base64.b64decode(encrypted_secret.encode())).decode()
    except Exception as e:
        print(f"Erro ao descriptografar: {e}")
        return None

def recover_otp_keys():
    """Recupera todas as chaves OTP do banco de dados"""
    db_path = "authenticator.db"
    
    if not os.path.exists(db_path):
        print("Arquivo authenticator.db não encontrado!")
        return
    
    # Carregar chave de criptografia
    cipher = load_encryption_key()
    if not cipher:
        return
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Buscar todas as contas
        cursor.execute("SELECT id, name, secret, issuer, created_at FROM accounts ORDER BY name")
        accounts = cursor.fetchall()
        
        conn.close()
        
        if not accounts:
            print("Nenhuma conta encontrada no banco de dados")
            return
        
        print(f"\nEncontradas {len(accounts)} contas OTP:")
        print("=" * 80)
        
        for account in accounts:
            id_, name, encrypted_secret, issuer, created_at = account
            
            # Descriptografar chave secreta
            secret = decrypt_secret(cipher, encrypted_secret)
            
            if secret:
                print(f"\nConta #{id_}")
                print(f"   Nome: {name}")
                print(f"   Emissor: {issuer or 'N/A'}")
                print(f"   Chave OTP: {secret}")
                print(f"   Criado em: {created_at}")
                print(f"   URL Manual: otpauth://totp/{name}?secret={secret}&issuer={issuer}")
                print("-" * 50)
            else:
                print(f"Falha ao descriptografar conta: {name}")
        
        print(f"\nRecuperação concluída! {len(accounts)} contas processadas.")
        
    except Exception as e:
        print(f"Erro ao acessar banco de dados: {e}")

if __name__ == "__main__":
    print("Recuperador de Chaves OTP")
    print("=" * 40)
    recover_otp_keys()
    
    input("\nPressione Enter para sair...") 