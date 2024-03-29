import time
from pathlib import Path
from github.Repository import Repository

def get_languages_list(repository: Repository):
    """
    Recupera los lenguajes involucrados en un repo y retorna solo sus 
    nombres en orden de utilización (descendente)
    """
    lang_dict = repository.get_languages()
    return list(lang_dict.keys())

def esperar(segundos=1):
    """
    Función util para esperar entre una petición y la siguiente, para
    evitar ser baneado del sitio.
    
    TODO: Buscar la manera de deshabilitar esto globalmente
    """
    time.sleep(segundos)

def cleantxt(txt):
    """
    Clean the text removing the next characters:
    
      * blank chars at start and end of text
      * new lines chars in betweens of text
    """
    if txt is None:
        return ""
    
    # remove spaces and newlines at start and end
    txt = txt.strip()
    
    # remove newlines in between of text
    txt = " ".join([part.strip() for part in txt.splitlines() if len(part.strip())>0])
    return txt

def writeheader(file: Path) -> bool:
    """
    Determina si el archivo existe y está vacio.
    
    En dicho caso, el header debería ser escrito. En cualquier otro caso, no.
    """
    return file.is_file() and file.stat().st_size == 0

def save_repo(repo, f_repos, field_sep='\t', topic_sep=';', write_header=False):
    lista_de_lenguajes = get_languages_list(repo) # esto llama a la API
    esperar()

    repo_data = {
        "id": repo.full_name,
        "es_fork": repo.fork,
        "forks": repo.forks_count,
        "stars": repo.stargazers_count,
        "watchers": repo.watchers_count,
        "issues": repo.open_issues_count, # issues + prs
        "about": cleantxt(repo.description),
        "subscribers": repo.subscribers_count,
        "archived": repo.archived,
        "topics": topic_sep.join(repo.topics),
        "language": topic_sep.join(lista_de_lenguajes),
    }
    if write_header:
        f_repos.write(field_sep.join(repo_data.keys()) + "\n")
    f_repos.write(field_sep.join([str(item) for item in repo_data.values()]) + "\n")