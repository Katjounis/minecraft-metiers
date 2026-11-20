@echo off
rem Labo de datapacks : serveur local (localhost:25566), redemarre tout seul apres un "stop"
rem Pour l'arreter vraiment : fermer cette fenetre, ou Ctrl+C pendant l'attente
if exist "%~dp0local.cmd" call "%~dp0local.cmd"
if not defined LABO_JAVA set "LABO_JAVA=java"
if not exist "%~dp0serveur\server.jar" (echo Serveur absent : lance d'abord installer.bat & pause & exit /b 1)
title LABO Minecraft (localhost:25566)
cd /d "%~dp0serveur"
:boucle
"%LABO_JAVA%" -Xms1G -Xmx3G -jar server.jar nogui
echo.
echo Serveur du labo arrete. Redemarrage dans 3 s (Ctrl+C pour quitter)...
timeout /t 3 >nul
goto boucle
