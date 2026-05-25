@echo on
title SISTEMA CNRT - INICIO

echo ======================================
echo    INICIANDO SISTEMA CNRT
echo ======================================

cd /d %~dp0

echo.
echo [1/3] Verificando Python...
python --version

if %errorlevel% neq 0 (
    echo ERROR: Python no encontrado en PATH
    pause
    exit
)

echo.
echo [2/3] Instalando dependencias (si faltan)...
pip install flask flask_sqlalchemy

echo.
echo [3/3] Iniciando servidor...
python app.py

echo.
echo Servidor cerrado
pause