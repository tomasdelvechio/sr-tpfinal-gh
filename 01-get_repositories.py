import json
from pathlib import Path
import time

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
USRSCSV         = DATADIR / "users.csv"
#OUTPUTDIR = Path(cfg("output")) / "01-SCRAPING-CATEGORIES"
#
########################################################################

# Cargamos la configuracion
cfg = json.load(open(CFGFILE))

# imprime por consola las llamadas a la API
if cfg["debug"]:
    enable_console_debug_logging()

# auth con github
auth = Auth.Token(cfg["access_token"])
g = Github(auth=auth)

#for repo in g.get_user().get_repos():
#    print(repo.name)

with open(REPOCSV, 'a') as f_repos:
    i = 0
    header = True
    for repo in g.search_repositories("python", sort='stars', order='desc', topic="machine-learning"):
        # Primero traemos información extra del repo (cada linea es un nuevo pedido a la API)
        lista_de_lenguajes = hp.get_languages_list(repo)
        time.sleep(1)
        
        repo_data = {
            "id": repo.full_name,
            "es_fork": repo.fork,
            "forks": repo.forks_count,
            "stars": repo.stargazers_count,
            "watchers": repo.watchers_count,
            "issues": repo.open_issues_count, # issues + prs
            "about": repo.description,
            "subscribers": repo.subscribers_count,
            "archived": repo.archived,
            "topics": ",".join(repo.topics),
            "language": ",".join(lista_de_lenguajes),
        }
        time.sleep(1)
        if header:
            f_repos.write(",".join(repo_data.keys()) + "\n")
            header = False
        f_repos.write(",".join([str(item) for item in repo_data.values()]) + "\n")
        i += 1
        if i > 10:
            break
