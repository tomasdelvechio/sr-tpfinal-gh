"""
Convierte los 3 dfs en tablas de una base SQLite
"""

import sys
import json
import uuid
import shutil
from pathlib import Path

import pandas as pd
import sqlite3

import helpers as hp

########################################################################
#   Configs section
BASEDIR         = Path(__file__).resolve().parent
CFGFILE         = BASEDIR / "configs.json"
DATADIR         = BASEDIR / "datasets"
REPOCSV         = DATADIR / "repositories.csv"
INTERACTIONCSV  = DATADIR / "interactions.csv"
USERSCSV        = DATADIR / "users.csv"
OUTPUTDIR       = BASEDIR / "output/20-df-to-sql"

FIELDSEPARATOR  = '\t'
TOPICSEPARATOR  = ';'

DBPATH = DATADIR / "data.db"
#
########################################################################

# Cargamos la configuracion
cfg = json.load(open(CFGFILE))

# backup de todo lo que toca este script por las dudas
if cfg["backups"]:
    suffix = "".join(str(uuid.uuid4()).split("-"))
    
    # Backup del directorio de salida
    OUTPUTDIR_BKP = BASEDIR / f"output/20-df-to-sql{suffix}"
    shutil.copytree(str(OUTPUTDIR), str(OUTPUTDIR_BKP))
    
    # Backup del dataset
    DATADIR_BKP = BASEDIR / f"datasets-{suffix}"
    shutil.copytree(str(DATADIR), str(DATADIR_BKP))

# Levantamos lo ya escaneado mientras nos de la RAM para poder retomar cuando se corta
#try:
dfrepos = pd.read_csv(REPOCSV, sep=FIELDSEPARATOR)
dfinter = pd.read_csv(INTERACTIONCSV, sep=FIELDSEPARATOR)
dfusers = pd.read_csv(USERSCSV, sep=FIELDSEPARATOR)
#except ValueError as e:
#    pass

conn = sqlite3.connect(DBPATH)
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS users (
                id          text    PRIMARY KEY,
                gh_id       text,
                name        text,
                bio         text,
                blog        text,
                company     text,
                location    text,
                creacion    text,
                email       text,
                following   text,
                followers   text,
                avatar_url  text)""")

c.execute("""CREATE TABLE IF NOT EXISTS repositories (
                id          text,
                es_fork     text,
                forks       text,
                stars       text,
                watchers    text,
                issues      text,
                about       text,
                subscribers text,
                archived    text,
                topics      text,
                language    text,
                PRIMARY KEY(id))""")

c.execute("""CREATE TABLE IF NOT EXISTS interactions (
        repository  text,
        user        text,
        date        text,
        PRIMARY KEY(repository,user))""")

conn.commit()

# nos aseguramos que no haya duplicados en la base generada
dfusers = dfusers.drop_duplicates(subset=['id'], ignore_index=True)
dfrepos = dfrepos.drop_duplicates(subset=['id'], ignore_index=True)

# pandas to_sql function no SABE crear PKs lo cual rompe todo
#   https://stackoverflow.com/a/31045044
# Por eso, lo mejor es crear la estructura y que no sea pisada por 
#   pandas, sino que falle. Elimina la base de datos o no bajo tu
#   propio riesgo.
dfrepos.to_sql('repositories', conn, if_exists='append', index=False)
dfusers.to_sql('users', conn, if_exists='append', index=False)
dfinter.to_sql('interactions', conn, if_exists='append', index=False)

conn.close()
