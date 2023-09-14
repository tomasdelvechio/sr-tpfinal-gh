from github.Repository import Repository

def get_languages_list(repository: Repository):
    """
    Recupera los lenguajes involucrados en un repo y retorna solo sus 
    nombres en orden de utilización (descendente)
    """
    lang_dict = repository.get_languages()
    return list(lang_dict.keys())