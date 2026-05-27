@echo off
title SISTEMA CNRT - INICIO

echo ======================================
echo    INICIANDO SISTEMA CNRT
echo ======================================

cd /d "%~dp0"

echo.
echo [1/4] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python no encontrado en PATH.
        echo Asegurate de tener Python instalado y que el ejecutable este accesible.
        pause
        exit /b 1
    ) else (
        set "PYTHON=py"
    )
) else (
    set "PYTHON=python"
)

if not exist ".venv\Scripts\python.exe" (
    echo.
    echo [2/4] Creando entorno virtual .venv...
    %PYTHON% -m venv .venv
    if errorlevel 1 (
        echo ERROR: No se pudo crear el entorno virtual.
        goto install_global
    )
)

echo.
echo [3/4] Instalando dependencias...
.venv\Scripts\python.exe -m pip install --upgrade pip >nul 2>&1
.venv\Scripts\python.exe -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar las dependencias en el entorno virtual.
    goto install_global
)

echo.
echo [4/4] Iniciando servidor...
.venv\Scripts\python.exe app.py
goto end

:install_global
echo.
echo Instalando dependencias en Python global...
%PYTHON% -m pip install --upgrade pip
%PYTHON% -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar las dependencias globalmente.
    pause
    exit /b 1
)

echo.
echo Iniciando servidor...
%PYTHON% app.py

:end
echo.
echo Servidor cerrado
pause