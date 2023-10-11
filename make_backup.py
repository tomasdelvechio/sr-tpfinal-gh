"""
Backup de un directorio pasado por parametro

Ejemplo:

    python make_backup.py dir_origen/
"""

import json
import uuid
import shutil
import sys
from pathlib import Path

import helpers as hp

########################################################################
#   Configs section
BASEDIR   = Path(__file__).resolve().parent
CFGFILE   = BASEDIR / "configs.json"
OUTPUTDIR = BASEDIR / "output"
BACKUPDIR = BASEDIR / "backups"
#
########################################################################

cfg = json.load(open(CFGFILE))

if not cfg["backups"]:
    print("No está habilitado el hacer los backups. Por favor, revise la variable 'backups' en el archivo configs.json")
    sys.exit(1)

if len(sys.argv) < 2:
    print("Falta el directorio a ser copiado.")
    print("Forma de uso:")
    print("     python make_backup.py dir_to_backup")
    sys.exit(1)

BACKUPDIR.mkdir(parents=True, exist_ok=True)
dir_to_backup = BASEDIR / Path(sys.argv[1])

if not dir_to_backup.is_dir():
    print("El directorio pasado como parámetro no existe:")
    print(f"    {dir_to_backup}")
    sys.exit(1)

suffix = "".join(str(uuid.uuid4()).split("-"))
target_dir = Path(f"{BACKUPDIR}/{dir_to_backup.name}-{suffix}")

# Backup del directorio de salida
shutil.copytree(str(dir_to_backup), str(target_dir))

print("Backup: ")
print(f"     Origen: {dir_to_backup}")
print(f"    Destino: {target_dir}")
