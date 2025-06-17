import sqlite3
import os
from cryptography.fernet import Fernet
import base64

class Database:
    def __init__(self):
        self.db_path = "authenticator.db"
        self.key_path = "key.key"
        self.setup_encryption()
        self.setup_database()
    
    def setup_encryption(self):
        """Configura criptografia para as chaves secretas"""
        if not os.path.exists(self.key_path):
            key = Fernet.generate_key()
            with open(self.key_path, 'wb') as key_file:
                key_file.write(key)
        
        with open(self.key_path, 'rb') as key_file:
            self.key = key_file.read()
        
        self.cipher = Fernet(self.key)
    
    def setup_database(self):
        """Cria a tabela se não existir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                secret TEXT NOT NULL,
                issuer TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def encrypt_secret(self, secret):
        """Criptografa a chave secreta"""
        return base64.b64encode(self.cipher.encrypt(secret.encode())).decode()
    
    def decrypt_secret(self, encrypted_secret):
        """Descriptografa a chave secreta"""
        return self.cipher.decrypt(base64.b64decode(encrypted_secret.encode())).decode()
    
    def add_account(self, name, secret, issuer=""):
        """Adiciona uma nova conta"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        encrypted_secret = self.encrypt_secret(secret)
        
        cursor.execute("""
            INSERT INTO accounts (name, secret, issuer)
            VALUES (?, ?, ?)
        """, (name, encrypted_secret, issuer))
        
        conn.commit()
        conn.close()
        return cursor.lastrowid
    
    def get_all_accounts(self):
        """Retorna todas as contas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, secret, issuer FROM accounts ORDER BY name")
        accounts = cursor.fetchall()
        
        conn.close()
        
        # Descriptografa as chaves secretas
        decrypted_accounts = []
        for account in accounts:
            id_, name, encrypted_secret, issuer = account
            secret = self.decrypt_secret(encrypted_secret)
            decrypted_accounts.append((id_, name, secret, issuer))
        
        return decrypted_accounts
    
    def delete_account(self, account_id):
        """Remove uma conta"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
        
        conn.commit()
        conn.close()
    
    def update_account(self, account_id, name, secret, issuer=""):
        """Atualiza uma conta"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        encrypted_secret = self.encrypt_secret(secret)
        
        cursor.execute("""
            UPDATE accounts 
            SET name = ?, secret = ?, issuer = ?
            WHERE id = ?
        """, (name, encrypted_secret, issuer, account_id))
        
        conn.commit()
        conn.close()