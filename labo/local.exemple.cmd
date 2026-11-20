@echo off
rem Reglages propres a ce PC. Copier ce fichier en local.cmd (ignore par git) et l'adapter.
rem Java 25 ou plus recent
set "LABO_JAVA=D:\Servers\minecraft\runtime\jdk\bin\java.exe"
rem Serveur de production (sauvegardes, server.jar, deploiement). Laisser vide si pas de prod sur ce PC.
set "LABO_PROD=D:\Servers\minecraft"
rem Packs developpes hors du depot, branches eux aussi dans le labo : nom=dossier;nom2=dossier2
set "LABO_PACKS_EXTERNES="
