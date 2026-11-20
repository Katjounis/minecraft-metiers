@echo off
rem Envoie des commandes au labo sans etre en jeu
rem   lab-cmd.bat "function metiers:version" "scoreboard players list"
rem   lab-cmd.bat < scenario.txt     (une commande par ligne, # = commentaire)
python "%~dp0outils\rcon.py" %*
