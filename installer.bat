@echo off
chcp 65001 > nul
setlocal EnableDelayedExpansion

echo.
echo +--------------------------------------------------------------+
echo   AGENTE B3 -- Instalador v2.0
echo   Letras Financeiras -- Configuracao do ambiente
echo +--------------------------------------------------------------+
echo.

:: Verificar Python
python --version > nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado. Instale em https://python.org
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo Python encontrado: %PYVER%

:: Criar ambiente virtual
if not exist ".venv" (
    echo Criando ambiente virtual...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERRO] Falha ao criar ambiente virtual.
        pause
        exit /b 1
    )
)

:: Ativar e instalar dependencias
echo Instalando dependencias...
call .venv\Scripts\activate.bat
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias.
    pause
    exit /b 1
)

:: Criar pastas necessarias
echo Criando pastas de trabalho...
if not exist "presets" mkdir presets
if not exist "outputs" mkdir outputs
if not exist "logs" mkdir logs
if not exist "assets" mkdir assets

:: Criar pasta de relatórios no Documents
set RELATORIOS=%USERPROFILE%\Documents\Relatorios LF
if not exist "%RELATORIOS%" (
    mkdir "%RELATORIOS%"
    echo Pasta de relatórios criada: %RELATORIOS%
)

:: Gerar ícone
echo Gerando icone...
python build_icon.py

:: Criar atalho no Desktop
echo Criando atalho na área de trabalho...
set LAUNCHER=%CD%\launcher.py
set PYTHON_EXE=%CD%\.venv\Scripts\pythonw.exe
set DESKTOP=%USERPROFILE%\Desktop
set SHORTCUT=%DESKTOP%\Agente B3.lnk
set ICON=%CD%\assets\icon.ico

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = '%PYTHON_EXE%'; $s.Arguments = '\"'%LAUNCHER%'\"'; $s.WorkingDirectory = '%CD%'; $s.IconLocation = '%ICON%'; $s.Description = 'Agente B3 - Letras Financeiras'; $s.Save()"

if exist "%SHORTCUT%" (
    echo Atalho criado: %SHORTCUT%
) else (
    echo [AVISO] Nao foi possivel criar o atalho automaticamente.
)

echo.
echo +--------------------------------------------------------------+
echo   Instalacao concluida com sucesso!
echo.
echo   Para abrir a interface grafica:
echo     - Clique no atalho "Agente B3" na area de trabalho, ou
echo     - Execute: python launcher.py
echo.
echo   Para gerar um .exe distribuivel:
echo     - Execute: python build.py
echo +--------------------------------------------------------------+
echo.
pause
