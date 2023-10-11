"""
Este script repara todas las inconsistencias que aparezcan en los datasets
generados por los scripts 01- y 02-.
"""

import json
from pathlib import Path

import pandas as pd

########################################################################
#   Configs section
BASEDIR         = Path(__file__).resolve().parent
CFGFILE         = BASEDIR / "configs.json"
DATADIR         = BASEDIR / "datasets"
REPOCSV         = DATADIR / "repositories.csv"
INTERACTIONCSV  = DATADIR / "interactions.csv"
USERSCSV        = DATADIR / "users.csv"
INPUTDIR        = BASEDIR / "output/02-users"
OUTPUTDIR       = BASEDIR / "output/03-check"

FIELDSEPARATOR  = '\t'
TOPICSEPARATOR  = ';'
#
########################################################################

# Cargamos la configuracion
cfg = json.load(open(CFGFILE))

# Para cada dataset
#   - Verificar que no existan items repetidos

def drop_duplicates(filepath: Path, sep=FIELDSEPARATOR):
    df = pd.read_csv(filepath, sep=sep)
    cant_duplicados = df.duplicated(keep='first').sum()
    if cant_duplicados > 0:
        df = df.drop_duplicates()
        df.to_csv(filepath, sep=FIELDSEPARATOR)
    return cant_duplicados

for repopath in [REPOCSV, USERSCSV, INTERACTIONCSV]:
    cantidad_duplicados = drop_duplicates(repopath)
    print(f"Para el archivo {repopath.name} se encontraron {cantidad_duplicados} registros duplicados.")
    print(f"Los mismos fueron eliminados y el archivo se guardó nuevamente.")
