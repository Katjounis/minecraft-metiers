@echo off
rem Regenere les packs depuis leurs sources, recharge le labo et affiche les erreurs
rem   lab-reload.bat          -> /reload (fonctions, tags, loot tables...)
rem   lab-reload.bat complet  -> redemarrage (necessaire si un menu / dialogue a change)
if exist "%~dp0local.cmd" call "%~dp0local.cmd"
if /i "%1"=="complet" (python "%~dp0outils\labo.py" reload --complet) else (python "%~dp0outils\labo.py" reload)
pause
