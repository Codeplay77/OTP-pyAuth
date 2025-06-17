import pyotp
import time
import re

class TOTPGenerator:
    def __init__(self):
        self.period = 30  # Período padrão de 30 segundos
    
    def clean_secret(self, secret):
        """Remove espaços e caracteres especiais da chave secreta"""
        return re.sub(r'[^A-Z2-7]', '', secret.upper())
    
    def validate_secret(self, secret):
        """Valida se a chave secreta está no formato correto"""
        cleaned_secret = self.clean_secret(secret)
        
        # Verifica se tem o tamanho mínimo e se contém apenas caracteres válidos
        if len(cleaned_secret) < 8:
            return False, "Chave muito curta (mínimo 8 caracteres)"
        
        if not re.match(r'^[A-Z2-7]+$', cleaned_secret):
            return False, "Chave contém caracteres inválidos"
        
        try:
            # Tenta criar um objeto TOTP para validar
            pyotp.TOTP(cleaned_secret)
            return True, "Chave válida"
        except Exception as e:
            return False, f"Erro na validação: {str(e)}"
    
    def generate_token(self, secret):
        """Gera o token TOTP atual (igual ao Google Authenticator)"""
        try:
            cleaned_secret = self.clean_secret(secret)
            totp = pyotp.TOTP(cleaned_secret)
            # Gera token com 6 dígitos e padding de zeros
            token = totp.now()
            return f"{int(token):06d}"
        except Exception as e:
            return "ERROR"
    
    def get_time_remaining(self):
        """Retorna o tempo restante até o próximo token"""
        return self.period - (int(time.time()) % self.period)
    
    def get_progress_percentage(self):
        """Retorna a porcentagem de progresso do token atual"""
        remaining = self.get_time_remaining()
        return ((self.period - remaining) / self.period) * 100
    
    def parse_otpauth_url(self, url):
        """Analisa uma URL otpauth:// e extrai as informações"""
        try:
            if not url.startswith('otpauth://'):
                return None, "URL deve começar com otpauth://"
            
            # Remove o prefixo otpauth://totp/
            if 'otpauth://totp/' in url:
                url = url.replace('otpauth://totp/', '')
            else:
                return None, "URL deve ser do tipo TOTP"
            
            # Separa o nome da conta dos parâmetros
            if '?' in url:
                account_part, params_part = url.split('?', 1)
            else:
                return None, "URL malformada"
            
            # Extrai o nome da conta
            account_name = account_part
            
            # Analisa os parâmetros
            params = {}
            for param in params_part.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = value
            
            if 'secret' not in params:
                return None, "Chave secreta não encontrada na URL"
            
            result = {
                'name': account_name,
                'secret': params['secret'],
                'issuer': params.get('issuer', '')
            }
            
            return result, "URL analisada com sucesso"
            
        except Exception as e:
            return None, f"Erro ao analisar URL: {str(e)}"