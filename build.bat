@echo off
echo ========================================
echo    Compilando Python Authenticator
echo ========================================

:: Verificar se PyInstaller está instalado
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Instalando PyInstaller...
    pip install pyinstaller
)

:: Criar diretório de build se não existir
if not exist "build" mkdir build
if not exist "dist" mkdir dist

:: Compilar o executável
echo.
echo Compilando executável...
pyinstaller --onefile ^
    --windowed ^
    --name "PythonAuthenticator" ^
    --icon=icon.ico ^
    --add-data "icon.ico;." ^
    --hidden-import=PIL ^
    --hidden-import=PIL.Image ^
    --hidden-import=cryptography ^
    --hidden-import=pyotp ^
    --hidden-import=sqlite3 ^
    --clean ^
    main.py

:: Verificar se compilação foi bem-sucedida
if exist "dist\PythonAuthenticator.exe" (
    echo.
    echo ========================================
    echo   COMPILAÇÃO CONCLUÍDA COM SUCESSO!
    echo ========================================
    echo.
    echo Executável criado em: dist\PythonAuthenticator.exe
    echo Tamanho aproximado: 15-25 MB
    echo.
    echo Para testar: dist\PythonAuthenticator.exe
    echo.
    pause
) else (
    echo.
    echo ========================================
    echo      ERRO NA COMPILAÇÃO
    echo ========================================
    echo.
    echo Verifique as mensagens de erro acima
    echo.
    pause
)