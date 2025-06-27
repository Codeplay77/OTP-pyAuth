@echo off
echo ========================================
echo   Instalando Dependências do Sistema
echo ========================================

echo.
echo Instalando bibliotecas necessárias...

:: Instalar dependências básicas
pip install pyotp
pip install cryptography
pip install Pillow
pip install qrcode[pil]

:: Instalar dependências do system tray
echo.
echo Instalando dependências para system tray...
pip install pystray

:: Instalar dependências para hotkeys globais
echo.
echo Instalando dependências para atalhos globais...
pip install keyboard

:: Instalar PyInstaller para compilação
echo.
echo Instalando PyInstaller...
pip install pyinstaller

echo.
echo ========================================
echo    INSTALAÇÃO CONCLUÍDA!
echo ========================================
echo.
echo Recursos disponíveis:
echo   ✓ Geração de tokens TOTP
echo   ✓ System tray (bandeja do sistema)
echo   ✓ Hotkey global: Ctrl+Shift+A
echo   ✓ Compilação para executável
echo.
echo Para compilar: build.bat
echo Para executar: python main.py
echo.
pause