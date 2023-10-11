#!/usr/bin/env bash

mkdir -p output/01-repositories/
python make_backup.py datasets/
python make_backup.py output/01-repositories/
python 01-get_repositories.py &> output/01-repositories/output.log

mkdir -p output/02-users/
python make_backup.py datasets/
python make_backup.py output/02-users/
python 02-get_users.py &> output/02-users/output.log

mkdir -p output/03-check/
python make_backup.py datasets/
python make_backup.py output/03-check/
python 03-check_dataset_consistency.py &> output/03-check/output.log

mkdir -p output/04-extra-data/
python make_backup.py datasets/
python make_backup.py output/04-extra-data/
python 04-users_extra_data.py &> output/04-extra-data/output.log