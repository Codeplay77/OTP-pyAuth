import sqlite3
import os
import sys
from cryptography.fernet import Fernet
import base64

class Database:
    def __init__(self):
        # Determinar diretório correto para arquivos
        self.app_dir = self.get_app_directory()
        self.db_path = os.path.join(self.app_dir, "authenticator.db")
        self.key_path = os.path.join(self.app_dir, "key.key")
        
        self.setup_encryption()
        self.setup_database()
    
    def get_app_directory(self):
        """Determina o diretório correto para salvar os arquivos"""
        if getattr(sys, 'frozen', False):
            # Executável PyInstaller - usar diretório do executável
            return os.path.dirname(sys.executable)
        else:
            # Script Python normal - usar diretório do script
            return os.path.dirname(os.path.abspath(__file__))
    
    def setup_encryption(self):
        """Configura criptografia para as chaves secretas"""
        try:
            if not os.path.exists(self.key_path):
                print(f"Criando nova chave de criptografia em: {self.key_path}")
                key = Fernet.generate_key()
                with open(self.key_path, 'wb') as key_file:
                    key_file.write(key)
            else:
                print(f"Carregando chave existente de: {self.key_path}")
            
            with open(self.key_path, 'rb') as key_file:
                self.key = key_file.read()
            
            self.cipher = Fernet(self.key)
            print("Criptografia configurada com sucesso")
            
        except Exception as e:
            print(f"Erro ao configurar criptografia: {e}")
            raise
    
    def setup_database(self):
        """Cria a tabela se não existir"""
        try:
            print(f"Configurando banco de dados em: {self.db_path}")
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
            print("Banco de dados configurado com sucesso")
            
        except Exception as e:
            print(f"Erro ao configurar banco: {e}")
            raise
    
    def encrypt_secret(self, secret):
        """Criptografa a chave secreta"""
        return base64.b64encode(self.cipher.encrypt(secret.encode())).decode()
    
    def decrypt_secret(self, encrypted_secret):
        """Descriptografa a chave secreta"""
        return self.cipher.decrypt(base64.b64decode(encrypted_secret.encode())).decode()
    
    def add_account(self, name, secret, issuer=""):
        """Adiciona uma nova conta"""
        try:
            print(f"Adicionando conta: {name}")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            encrypted_secret = self.encrypt_secret(secret)
            
            cursor.execute("""
                INSERT INTO accounts (name, secret, issuer)
                VALUES (?, ?, ?)
            """, (name, encrypted_secret, issuer))
            
            account_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"Conta adicionada com ID: {account_id}")
            return account_id
            
        except Exception as e:
            print(f"Erro ao adicionar conta: {e}")
            raise
    
    def get_all_accounts(self):
        """Retorna todas as contas"""
        try:
            if not os.path.exists(self.db_path):
                print("Banco de dados não existe ainda")
                return []
                
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, name, secret, issuer FROM accounts ORDER BY name")
            accounts = cursor.fetchall()
            
            conn.close()
            
            # Descriptografa as chaves secretas
            decrypted_accounts = []
            for account in accounts:
                try:
                    id_, name, encrypted_secret, issuer = account
                    secret = self.decrypt_secret(encrypted_secret)
                    decrypted_accounts.append((id_, name, secret, issuer))
                except Exception as e:
                    print(f"Erro ao descriptografar conta {id_}: {e}")
                    continue
            
            print(f"Carregadas {len(decrypted_accounts)} contas")
            return decrypted_accounts
            
        except Exception as e:
            print(f"Erro ao carregar contas: {e}")
            return []
    
    def delete_account(self, account_id):
        """Remove uma conta"""
        try:
            print(f"Removendo conta ID: {account_id}")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
            
            conn.commit()
            conn.close()
            print("Conta removida com sucesso")
            
        except Exception as e:
            print(f"Erro ao remover conta: {e}")
            raise
    
    def update_account(self, account_id, name, secret, issuer=""):
        """Atualiza uma conta"""
        try:
            print(f"Atualizando conta ID: {account_id}")
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
            print("Conta atualizada com sucesso")
            
        except Exception as e:
            print(f"Erro ao atualizar conta: {e}")
            raise
    
    def get_database_info(self):
        """Retorna informações sobre o banco para debug"""
        return {
            'app_dir': self.app_dir,
            'db_path': self.db_path,
            'key_path': self.key_path,
            'db_exists': os.path.exists(self.db_path),
            'key_exists': os.path.exists(self.key_path),
            'app_dir_writable': os.access(self.app_dir, os.W_OK),
            'frozen': getattr(sys, 'frozen', False)
        }