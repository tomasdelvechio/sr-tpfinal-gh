"""

"""

import json
import uuid
import shutil
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
INPUTDIR        = BASEDIR / "output/03-check-dataset-consistency"
OUTPUTDIR       = BASEDIR / "output/04-users-extra-data"

FIELDSEPARATOR  = '\t'
TOPICSEPARATOR  = ';'

INTERACTION_PER_REPO_LIMIT  = None # None for iterate all users
REPOSITORIES_LIMIT          = None # None for iterate all repos

FLUSH_BATCH = 20    # number of registers to flush data to disk - None for no flush
#
########################################################################

# Cargamos la configuracion
cfg = json.load(open(CFGFILE))

# imprime por consola las llamadas a la API
if cfg["debug"]:
    enable_console_debug_logging()

# backup de todo lo que toca este script por las dudas
if cfg["backups"]:
    suffix = "".join(str(uuid.uuid4()).split("-"))
    
    # Backup del directorio de salida
    try:
        OUTPUTDIR_BKP = BASEDIR / f"output/02-users-{suffix}"
        shutil.copytree(str(OUTPUTDIR), str(OUTPUTDIR_BKP))
    except FileNotFoundError:
        # no existe, lo creamos
        OUTPUTDIR.mkdir(parents=True, exist_ok=True)
    # Backup del dataset generado
    DATADIR_BKP = BASEDIR / f"datasets-{suffix}"
    shutil.copytree(str(DATADIR), str(DATADIR_BKP))

    print("Directorios de Backups: ")
    print(f"    Datasets: {DATADIR_BKP}")
    print(f"     Salidas:  {OUTPUTDIR_BKP}")

# auth con github
auth = Auth.Token(cfg["access_token"])
g = Github(auth=auth)

df_users = pd.read_csv(USERSCSV, sep=FIELDSEPARATOR, header=0)
df_users["avatar_url"] = None

usernames = df_users.id.unique()

for username in usernames:
    user = g.get_user(username)
    df_users.loc[df_users["id"] == username, ["avatar_url"]] = user.avatar_url

df_users.to_csv(USERSCSV, sep=FIELDSEPARATOR, header=True)
