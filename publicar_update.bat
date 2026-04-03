@echo off
setlocal ENABLEDELAYEDEXPANSION

echo ==========================================
echo   PUBLICADOR DE ATUALIZACAO - UNREAL CORE
echo ==========================================
echo.

REM =============================
REM CONFERE SE ESTA EM UM REPO GIT
REM =============================
git rev-parse --is-inside-work-tree >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Esta pasta nao e um repositorio Git.
    pause
    exit /b
)

echo Repositorio Git encontrado.
echo.

REM =============================
REM PEDIR VERSAO
REM =============================
set /p UC_VERSION=Digite a nova versao do Unreal Core (ex: 1.0.5): 

if "%UC_VERSION%"=="" (
    echo Versao invalida.
    pause
    exit /b
)

echo.
echo Publicando versao %UC_VERSION%...
echo.

REM =============================
REM ATUALIZAR version.json
REM =============================
if exist version.json (
    powershell -Command "(Get-Content version.json | ConvertFrom-Json | ForEach-Object { $_.app_release='%UC_VERSION%'; $_ }) | ConvertTo-Json -Depth 10 | Set-Content version.json"
    echo version.json atualizado.
)

REM =============================
REM ADD TUDO (incluindo o .exe)
REM =============================
git add . >nul 2>&1

REM =============================
REM COMMIT
REM =============================
git diff --cached --quiet
if %ERRORLEVEL%==0 (
    echo Nenhuma alteracao detectada. Nada para commitar.
) else (
    git commit -m "Update Unreal Core para versao %UC_VERSION%" >nul 2>&1
    echo Commit criado com sucesso.
)

REM =============================
REM PUSH
REM =============================
echo.
echo Enviando para o GitHub...
git push

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERRO ao enviar para o GitHub.
    echo Execute: git pull --rebase
    echo e rode este BAT novamente.
    pause
    exit /b
)

echo.
echo ==========================================
echo  Publicacao concluida - v%UC_VERSION%
echo ==========================================
pause
endlocal
