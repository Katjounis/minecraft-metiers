@echo off
rem Cree le serveur du labo dans labo\serveur (server.jar, monde de la prod, jonctions vers les packs)
rem   installer.bat                       installation neuve (a partir de LABO_PROD)
rem   installer.bat D:\Servers\lab        recupere un ancien labo (monde, reglages, joueurs)
if exist "%~dp0local.cmd" call "%~dp0local.cmd"
if "%~1"=="" (python "%~dp0outils\labo.py" installer) else (python "%~dp0outils\labo.py" installer --depuis "%~1")
pause
