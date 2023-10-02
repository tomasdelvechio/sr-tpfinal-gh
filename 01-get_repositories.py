"""
Script que parte de una busqueda de repositorios y recopila usuarios, repos e interacciones
"""

import sys
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
OUTPUTDIR       = BASEDIR / "output/01-repositories"

FIELDSEPARATOR  = '\t'
TOPICSEPARATOR  = ';'

INTERACTION_PER_REPO_LIMIT  = 50 # None for iterate all users
REPOSITORIES_LIMIT          = 100 # None for iterate all repos

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
    OUTPUTDIR_BKP = BASEDIR / f"output/01-repositories-{suffix}"
    shutil.copytree(str(OUTPUTDIR), str(OUTPUTDIR_BKP))
    
    # Backup del dataset generado
    DATADIR_BKP = BASEDIR / f"datasets-{suffix}"
    shutil.copytree(str(DATADIR), str(DATADIR_BKP))

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
    header = hp.writeheader(REPOCSV)
    for repo in g.search_repositories("python", sort='stars', order='desc', topic="machine-learning"):
        # Cada iteración del for es un nuevo pedido a la API
        hp.esperar()
        
        if scanned_repos is not None and repo.full_name in scanned_repos:
            print(f"[R]: {repo.full_name} already scanned. Skipping...")
        else:
            # Entra acá si no tiene el repo, para bajarlo y guardarlo
            scanned_repos.add(repo.full_name)
            i += 1
            print(f"{i} [R]: {repo.full_name}")
            
            ################################################################
            # Parte 1 - Armamos el dataset del repo 
            lista_de_lenguajes = hp.get_languages_list(repo) # esto llama a la API
            hp.esperar()
            
            repo_data = {
                "id": repo.full_name,
                "es_fork": repo.fork,
                "forks": repo.forks_count,
                "stars": repo.stargazers_count,
                "watchers": repo.watchers_count,
                "issues": repo.open_issues_count, # issues + prs
                "about": hp.cleantxt(repo.description),
                "subscribers": repo.subscribers_count,
                "archived": repo.archived,
                "topics": TOPICSEPARATOR.join(repo.topics),
                "language": TOPICSEPARATOR.join(lista_de_lenguajes),
            }
            if header:
                # primer pasada, escribo el header
                f_repos.write(FIELDSEPARATOR.join(repo_data.keys()) + "\n")
                header = False
            f_repos.write(FIELDSEPARATOR.join([str(item) for item in repo_data.values()]) + "\n")
        
        ################################################################
        # Parte 2 - Armamos el dataset de interacciones
        stars = repo.get_stargazers_with_dates() # llamada a la api
        hp.esperar()
        
        j = 0
        header = hp.writeheader(INTERACTIONCSV)
        for interaction in stars:
            interaction_data = {
                "repository": repo.full_name,
                "user": interaction.user.login, # llamada a la api
                "date": interaction.starred_at,
            }
            hp.esperar()

            if header:
                # primer pasada, escribo el header
                f_inter.write(FIELDSEPARATOR.join(interaction_data.keys()) + "\n")
                f_users.write(FIELDSEPARATOR.join(users_data.keys()) + "\n")
                header = False

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

            if scanned_users is not None and interaction.user.login in scanned_users:
                print(f"  [U]: {interaction.user.login} already scanned. Skipping...")
            else:
                # Es un usuario que no tengo, escanearlo
                user = interaction.user
                users_data = {
                    "id": user.login,
                    "gh_id": user.id,
                    "name": user.name,
                    "bio": hp.cleantxt(user.bio),
                    "blog": user.blog,
                    "company": user.company,
                    "location": user.location,
                    "creacion": user.created_at,
                    "email": user.email,
                    "following": user.following,
                    "followers": user.followers,
                }
                f_users.write(FIELDSEPARATOR.join([str(item) for item in users_data.values()]) + "\n")

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