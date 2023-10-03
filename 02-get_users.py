"""
Este script es el complemento de 01-get_repositories.py

Toma todos los usuarios levantados por el anterior en el dataset de usuarios, 
y obtengo los repos a los que le puso estrella.

Entonces, si el repo no fue agregado anteriormente al datasets de repos, lo agrego
y ademas agrego la interacción.

Lamentablemente para llegar a una estrella a un repo desde el usuario, hay que
hacer el camino user -> repo -> estrelas del repo (todas) y luego iterar para
encontrar el usuario en cuestión

Una idea es aprovechar que voy a descargar todas las interacciones y buscar
la de los usuarios que ya tengo pero no tengo la interacción, para guardarla
y no tener que descargarla adelante.
"""

import json
import uuid
import shutil
from pathlib import Path

import pandas as pd

from github import enable_console_debug_logging
from github import Github
from github import Auth

import helpers as hp

########################################################################
#   Configs section
BASEDIR         = Path(__file__).resolve().parent
CFGFILE         = BASEDIR / "configs.json"
DATADIR         = BASEDIR / "datasets"
REPOCSV         = DATADIR / "repositories.csv"
INTERACTIONCSV  = DATADIR / "interactions.csv"
USERSCSV        = DATADIR / "users.csv"
INPUTDIR        = BASEDIR / "output/01-repositories"
OUTPUTDIR       = BASEDIR / "output/02-users"

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

# Levantamos lo ya escaneado mientras nos de la RAM para poder retomar cuando se corta
scanned_repos = None
scanned_interactions = None
scanned_users = None
if REPOCSV.is_file() and INTERACTIONCSV.is_file():
    try:
        scanned_repos = set(pd.read_csv(REPOCSV, usecols=['id'], sep=FIELDSEPARATOR, header=0).id.unique())
        scanned_interactions = set(pd.read_csv(INTERACTIONCSV, usecols=['repository', 'user'], sep=FIELDSEPARATOR, header=0).to_records(index=False).tolist())
        scanned_users = set(pd.read_csv(USERSCSV, usecols=['id'], sep=FIELDSEPARATOR, header=0).id.unique())
    except ValueError as e:
        pass

with open(REPOCSV, 'a') as f_repos, open(INTERACTIONCSV, 'a') as f_inter, open(USERSCSV, 'a') as f_users:
    i = 0
    for username in scanned_users:
        user = g.get_user(username)
        
        # Para cada user recuperar todos los repos favs por el
        repos_stars_from_user = user.get_starred()
        for repo in repos_stars_from_user:
            if scanned_repos is not None and repo.full_name in scanned_repos:
                print(f"[R]: {repo.full_name} already scanned. Skipping...")
            else:
                # Si el repo no está en el repo nuestro
                # Guardar el repo (agregarlo tmb a scanned_repos)
                scanned_repos.add(repo.full_name)
                i += 1
                print(f"{i} [R]: {repo.full_name}")
                
                hp.save_repo(repo, f_repos)
            
            # Para cada repo fav del user i, recuperar todas las stars
            # necesito recuperar la interaccion desde los repos porque desde el usuario no obtengo la fecha
            stars = repo.get_stargazers_with_dates() # llamada a la api
            hp.esperar()
            
            j = 0
            for interaction in stars:
                if scanned_users is not None and interaction.user.login not in scanned_users:
                    # Si el usuario no está en la base, ignoro la interacción
                    print(f"  [U]: {interaction.user.login} not in base. Skipping...")
                    continue
                else:
                    print(f"  [U]: {interaction.user.login} present. Check interaction...")

                interaction_data = {
                    "repository": repo.full_name,
                    "user": interaction.user.login, # llamada a la api
                    "date": interaction.starred_at,
                }
                hp.esperar()

                # Maneja la cantidad de interacciones a recuperar por cada repositorio
                if scanned_interactions is not None and (repo.full_name, interaction.user.login) in scanned_interactions:
                    print(f"  [I]: [R] {repo.full_name} -> [U] {interaction.user.login} already scanned. Skipping...")
                else:
                    # Es una interacción que no tengo, escanearla
                    scanned_interactions.add((repo.full_name, interaction.user.login))
                    j += 1
                    print(f"  {i}.{j} [I]: [R] {repo.full_name} -> [U] {interaction.user.login}")
                    f_inter.write(FIELDSEPARATOR.join([str(item) for item in interaction_data.values()]) + "\n")
                    hp.esperar()

                if j % FLUSH_BATCH == 0:
                    f_inter.flush()
                    f_users.flush()

                if INTERACTION_PER_REPO_LIMIT is not None and j > INTERACTION_PER_REPO_LIMIT:
                    break
                
            if i % FLUSH_BATCH == 0:
                f_repos.flush()
            # Maneja la cantidad de repos a recuperar
            if REPOSITORIES_LIMIT is not None and i > REPOSITORIES_LIMIT:
                break

# Al finalizar este script, esperamos que para TODOS los usuarios de nuestra base
#   tengamos TODOS los repos con los que interactuaron