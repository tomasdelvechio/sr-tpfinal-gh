"""
A partir de la DDBB generada en SQLite por 20-... buscar repos que esten presentes
en interacciones pero no tengan información en la tabla de repositorios.
"""

import sys
import json
import sqlite3
import pandas as pd
import helpers as hp
from github import Auth
from pathlib import Path
from github import Github
from github import enable_console_debug_logging


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

conn = sqlite3.connect(DBPATH)
c = conn.cursor()
c.execute("""SELECT DISTINCT i.repository
                FROM interactions i
                LEFT JOIN repositories r
                    ON i.repository = r.id
                WHERE r.id IS NULL""")

repos = c.fetchall()
c.close()

if len(repos) == 0:
    print("No existen interacciones de repos sin datos. No hay nada para hacer. Terminando script.")
    sys.exit(0)

# Tenemos repos con interacciones pero sin data
print(f"Existen {len(repos)} con interacciones pero sin información de los mismos. Se va a recuperar dicha información.")
print("Si el repo ya no existe, se eliminará la interacción de la tabla correspondiente")

# Cargamos la configuracion
cfg = json.load(open(CFGFILE))

# auth con github
auth = Auth.Token(cfg["access_token"])
g = Github(auth=auth)

# imprime por consola las llamadas a la API
if cfg["debug"]:
    enable_console_debug_logging()

conn = sqlite3.connect(DBPATH)
c = conn.cursor()

i = 0
repo_records = []
for repo in repos:
    hp.esperar()
    data_repo = g.get_repo(repo[0])
    
    i += 1
    print(f"{i} [R]: {data_repo.full_name}")
    
    lista_de_lenguajes = hp.get_languages_list(data_repo) # esto llama a la API
    hp.esperar()
    
    repo_records.append({
        "id": data_repo.full_name,
        "es_fork": data_repo.fork,
        "forks": data_repo.forks_count,
        "stars": data_repo.stargazers_count,
        "watchers": data_repo.watchers_count,
        "issues": data_repo.open_issues_count, # issues + prs
        "about": hp.cleantxt(data_repo.description),
        "subscribers": data_repo.subscribers_count,
        "archived": data_repo.archived,
        "topics": TOPICSEPARATOR.join(data_repo.topics),
        "language": TOPICSEPARATOR.join(lista_de_lenguajes),
    })
    
    #print(data_repo)
    #break
    #print(repo[0])
    # Descargar la info del repo
    # insertarla en la base

c.close()

dfrepos = pd.DataFrame.from_dict(repo_records, orient='columns') #pd.read_csv(REPOCSV, sep=FIELDSEPARATOR)
dfrepos.to_sql('repositories', conn, if_exists='append', index=False)