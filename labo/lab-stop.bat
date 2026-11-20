@echo off
rem Arrete le labo (la fenetre lab-start le relance : la fermer pour un arret definitif)
python "%~dp0outils\rcon.py" stop
