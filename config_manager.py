import json
import os
import sys

class ConfigManager:
    def __init__(self):
        self.config_file = self.get_config_path()
        self.config = self.load_config()
    
    def get_config_path(self):
        """Determina caminho do arquivo de configuração"""
        if getattr(sys, 'frozen', False):
            # Executável - usar diretório do executável
            config_dir = os.path.dirname(sys.executable)
        else:
            # Desenvolvimento - usar diretório do script
            config_dir = os.path.dirname(os.path.abspath(__file__))
        
        return os.path.join(config_dir, 'config.json')
    
    def get_default_config(self):
        """Configuração padrão"""
        return {
            "hotkeys": {
                "toggle_window": "ctrl+shift+a",
                "add_account": "ctrl+shift+n"
            },
            "ui": {
                "window_position": "right",
                "margin": 20,
                "always_on_top": False,
                "custom_x": 100,
                "custom_y": 100
            },
            "tray": {
                "enabled": True,
                "hide_on_close": True,
                "tooltip": "Python Authenticator"
            },
            "update": {
                "auto_refresh": True,
                "refresh_interval": 1,
                "show_progress_bar": True
            }
        }
    
    def load_config(self):
        """Carrega configuração do arquivo JSON"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # Merge com padrões para garantir todas as chaves
                default = self.get_default_config()
                self.merge_config(default, config)
                return default
            else:
                # Criar arquivo padrão
                config = self.get_default_config()
                self.save_config(config)
                return config
        except Exception as e:
            print(f"Erro ao carregar config: {e}")
            return self.get_default_config()
    
    def merge_config(self, default, user):
        """Merge configuração do usuário com padrões"""
        for key, value in user.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self.merge_config(default[key], value)
                else:
                    default[key] = value
    
    def save_config(self, config=None):
        """Salva configuração no arquivo JSON"""
        try:
            config_to_save = config or self.config
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao salvar config: {e}")
            return False
    
    def get(self, path, default=None):
        """Obtém valor da configuração usando path (ex: 'ui.window_position')"""
        keys = path.split('.')
        value = self.config
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, path, value):
        """Define valor na configuração"""
        keys = path.split('.')
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        self.save_config()
    
    def get_hotkeys(self):
        """Retorna configuração de atalhos"""
        return self.config.get('hotkeys', {})
    
    def get_ui_config(self):
        """Retorna configuração de UI"""
        return self.config.get('ui', {})
    
    def get_tray_config(self):
        """Retorna configuração do system tray"""
        return self.config.get('tray', {})
    
    def get_update_config(self):
        """Retorna configuração de atualização"""
        return self.config.get('update', {})