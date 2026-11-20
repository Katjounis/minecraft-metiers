@echo off
rem Remplace le monde du labo par celui de la derniere sauvegarde de la prod (labo eteint)
rem Pense a lancer backup.bat sur la prod juste avant pour avoir un monde a jour
if exist "%~dp0local.cmd" call "%~dp0local.cmd"
echo Le monde actuel du labo va etre ECRASE.
pause
python "%~dp0outils\labo.py" sync
pause
