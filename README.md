# Sistema de Recomendación - Constructor del dataset

Scripts que construyen el dataset con los usuario, los ítems (repositorios de github) y las interacciones (likes o estrellas), que luego serán utilizados por [este sistema web](https://github.com/tomasdelvechio/sr-tpfinal-gh-web).

Una versión ya construida y lista para ser utilizada en el sistema web [puede encontrarse en este link](https://drive.google.com/file/d/1OmUjuhX0G-z35IbDKfVdkd_JOF8sC19A/view?usp=sharing). No es necesario clonar ni ejecutar este repositorio, a menos que se desee generar mayor cantidad de interacciones, usuarios y/o ítems.

## Instalación y Ejecución

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp configs.json.example configs.json
vim configs.json # ver detalles en sección configuraciones
python 01-get_repositories.py
python 02-get_users.py
python 03-check_dataset_consistency.py
python 04-users_extra_data.py
python 20-df_to_sql.py
python 30-get_repo_data.py
```

Al finalizar, el archivo `datasets/data.db` contiene la base de datos tal y como se utilizará en el sistema web.

## Configuraciones

El archivo `config.json` tiene el siguiente formato:

```json
{
    "access_token": "some_random_string_from_personal_access_token_on_github",
    "debug": false,
    "backups": false
}
```

Donde:

 * `access_token` es un personal access token otorgado por github con permisos de usuario y repositorio. [Ver documentación oficial](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic).
 * `debug` En caso de estar en `true`, imprime por consola de forma agresiva la salida para permitir una depuración ante problemas en la ejecución.
 * `backups` En caso de estar en `true`, respalda las salidas intermedias de cada script en el directorio `backups` para evitar perdida de datos entre diferentes ejecuciones de un mismo script.

# Estadísticas básicas del dataset

Todas las estadísticas reportadas a continuación corresponden a [este dataset](https://drive.google.com/file/d/1OmUjuhX0G-z35IbDKfVdkd_JOF8sC19A/view?usp=drive_link).

Las estadisticas pueden observarse en el [notebook correspondiente](analisis_dataset_final.ipynb).

# Enlaces

- [API PyGithub](https://pygithub.readthedocs.io/en/stable/apis.html)
- [Repo PyGithub](https://github.com/PyGithub/PyGithub)
- [Ejemplo API GitHub endpoint Repositorio](https://docs.github.com/en/free-pro-team@latest/rest/repos/repos?apiVersion=2022-11-28#get-a-repository)
- [Doc API Github busqueda de repositorios](https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories)
