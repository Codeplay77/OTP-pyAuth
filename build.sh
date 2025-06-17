#!/bin/bash

echo "========================================"
echo "   Compilando Python Authenticator"
echo "========================================"

# Verificar se PyInstaller está instalado
python3 -c "import PyInstaller" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Instalando PyInstaller..."
    pip3 install pyinstaller
fi

# Criar diretórios se não existirem
mkdir -p build
mkdir -p dist

# Compilar o executável
echo ""
echo "Compilando executável..."
pyinstaller --onefile \
    --windowed \
    --name "PythonAuthenticator" \
    --add-data "icon.ico:." \
    --hidden-import=PIL \
    --hidden-import=PIL.Image \
    --hidden-import=cryptography \
    --hidden-import=pyotp \
    main.py

# Verificar resultado
if [ -f "dist/PythonAuthenticator" ]; then
    echo ""
    echo "========================================"
    echo "  COMPILAÇÃO CONCLUÍDA COM SUCESSO!"
    echo "========================================"
    echo ""
    echo "Executável criado em: dist/PythonAuthenticator"
    echo "Para testar: ./dist/PythonAuthenticator"
    echo ""
else
    echo ""
    echo "========================================"
    echo "      ERRO NA COMPILAÇÃO"
    echo "========================================"
    echo ""
    echo "Verifique as mensagens de erro acima"
    echo ""
fi