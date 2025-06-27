@echo off
echo ========================================
echo    Building Python Authenticator
echo ========================================

:: Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

:: Create build directories
if not exist "build" mkdir build
if not exist "dist" mkdir dist

:: Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del "*.spec"

:: Build main executable
echo.
echo Building main executable...
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
    --hidden-import=pystray ^
    --hidden-import=keyboard ^
    --clean ^
    main.py

:: Verify build success
if exist "dist\PythonAuthenticator.exe" (
    echo.
    echo ========================================
    echo   BUILD COMPLETED SUCCESSFULLY!
    echo ========================================
    echo.
    echo Executable: dist\PythonAuthenticator.exe
    echo.
    echo DATA STORAGE:
    echo   - All files created in same folder as executable
    echo   - config.json: Application settings
    echo   - authenticator.db: Encrypted account data  
    echo   - key.key: Encryption key
    echo.
    echo PORTABLE SETUP:
    echo   - Copy entire dist\ folder to move application
    echo   - No registry or AppData usage
    echo   - Clean and portable installation
    echo.
    echo To run: dist\PythonAuthenticator.exe
    echo.
    pause
) else (
    echo.
    echo ========================================
    echo      BUILD FAILED
    echo ========================================
    echo.
    echo Check error messages above
    echo.
    pause
)