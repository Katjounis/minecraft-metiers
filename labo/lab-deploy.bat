@echo off
rem Installe un pack teste sur la PRODUCTION : sauvegarde, zip, remplacement dans world\datapacks
rem   lab-deploy.bat metiers
if exist "%~dp0local.cmd" call "%~dp0local.cmd"
if "%1"=="" (python "%~dp0outils\labo.py" packs & echo Usage : lab-deploy.bat ^<pack^> & pause & exit /b 1)
python "%~dp0outils\labo.py" deploy %1
pause
