@echo off
title Instalador DAF - XENOMA
color 0B

echo .
echo   Instalando DAF - Sistema de Apoyo Clinico...
echo ------------------------------------------------
echo.

:: Definir rutas
set "TARGET_DIR=%LocalAppData%\DAF_APP"
set "ORIGEN=%~dp0"

if exist "%TARGET_DIR%" (
    echo [!] Version anterior detectada. Limpiando archivos viejos...
    rd /s /q "%TARGET_DIR%"
    
    :: Buscamos el escritorio real (incluso si tiene OneDrive) y borramos el icono viejo
    for /f "usebackq tokens=*" %%d in (`powershell -NoProfile -Command "[Environment]::GetFolderPath('Desktop')"`) do set "REAL_DESKTOP=%%d"
    if exist "%REAL_DESKTOP%\DAF - XENOMA.lnk" del /f /q "%REAL_DESKTOP%\DAF - XENOMA.lnk"
)

echo [1/3] Copiando archivos al sistema...
xcopy ".\DAF_APP" "%TARGET_DIR%\" /E /I /H /Y /Q

echo [2/3] Creando acceso directo profesional...
powershell -NoProfile -Command "$WS = New-Object -ComObject WScript.Shell; $Desktop = [Environment]::GetFolderPath('Desktop'); $S = $WS.CreateShortcut(\"$Desktop\DAF - XENOMA.lnk\"); $S.TargetPath = \"$env:LocalAppData\DAF_APP\Lanzador.vbs\"; $S.IconLocation = \"$env:LocalAppData\DAF_APP\logo.ico\"; $S.WorkingDirectory = \"$env:LocalAppData\DAF_APP\"; $S.Save()"

echo [3/3] Finalizando instalacion...
echo.
echo.
echo   ¡INSTALACION COMPLETADA CON EXITO!
echo.
echo   Se ha creado el acceso directo en tu escritorio.
echo ----------------------------------------------------
echo.

:: Pregunta interactiva al usuario
echo Nota: Esta carpeta de instalacion (el ZIP extraido) ya no es 
echo necesaria para que XENOMA funcione, ya que se ha copiado al sistema.
echo.
set /p LIMPIAR="¿Deseas eliminar esta carpeta de instalacion ahora? (S/N): "

:: Logica de decision (La /I hace que no importe si escribe en mayuscula o minuscula)
if /I "%LIMPIAR%"=="S" (
    echo.
    echo Eliminando archivos temporales... ¡Disfruta de XENOMA!
    
    :: Nos movemos a otra carpeta para no bloquear el borrado
    cd /d %TEMP%
    :: Lanzamos el borrado fantasma y cerramos
    start /b "" cmd /c "timeout /t 2 >nul & rd /s /q "%ORIGEN%""
    exit
) else (
    echo.
    echo La carpeta se conservara. Puedes borrarla manualmente mas adelante.
    echo ¡Disfruta de DAF!
    echo.
    pause
    exit
)