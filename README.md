# TP Final SR 2023 - Maestria DM UBA

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp configs.json.example configs.json
vim configs.json
python 01-get_repositories.py
```

## Enlaces

- [API PyGithub](https://pygithub.readthedocs.io/en/stable/apis.html)
- [Repo PyGithub](https://github.com/PyGithub/PyGithub)
- [Ejemplo API GitHub endpoint Repositorio](https://docs.github.com/en/free-pro-team@latest/rest/repos/repos?apiVersion=2022-11-28#get-a-repository)
- [Doc API Github busqueda de repositorios](https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories)
