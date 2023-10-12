"""
Script que anexa extra data a la base de usuarios.

Este script solo itera sobre los usuarios que faltan, por lo cual
se puede ejecutar n veces sobre el archivo y solo agregará a quien 
corresponda
"""

import json
import uuid
import shutil
import pandas as pd
import helpers as hp
from github import Auth
from pathlib import Path
from github import Github
from github.GithubException import UnknownObjectException, RateLimitExceededException
from github import enable_console_debug_logging
import sys

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

# auth con github
auth = Auth.Token(cfg["access_token"])
g = Github(auth=auth)

df_users = pd.read_csv(USERSCSV, sep=FIELDSEPARATOR, header=0)
try:
    _ = df_users["avatar_url"]
except KeyError:
    # col no existe, se crea
    df_users["avatar_url"] = None

# solo usernames que le falta el avatar
usernames = df_users[df_users["avatar_url"].isnull()].id.unique()

print(f"Comenzando la recuperación de datos extras sobre {len(usernames)} usuarios")
cantidad_usuarios_eliminados = 0
for username in usernames:
    try:
        user = g.get_user(username)
    except UnknownObjectException:
        print(f"Usuario no existente: {username}")
        df_users.loc[df_users["id"] == username, ["avatar_url"]] = False
        cantidad_usuarios_eliminados += 1
        continue
    except RateLimitExceededException:
        print(f"Limite de peticiones alcanzado. Se guardan los usuarios recuperados y continue mas tarde con el script")
        break
    df_users.loc[df_users["id"] == username, ["avatar_url"]] = user.avatar_url

print(f"Finalizada la recuperación. Usuarios encontrados: {len(usernames)-cantidad_usuarios_eliminados}")
print(f"Usuarios eliminados: {cantidad_usuarios_eliminados}")

if cantidad_usuarios_eliminados > 0:
    df_users.to_csv(USERSCSV, sep=FIELDSEPARATOR, header=True, index=False)
