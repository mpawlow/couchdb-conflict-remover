# CouchDB Conflict Remover

A Python application that scans and removes all document conflicts from a CouchDB / Cloudant database.

## (1) Local Setup

### (1.1) Install prerequisites

- Install [Python 3.9.x](https://www.python.org/downloads/) or higher.

### (1.2) Clone source

```shell
git@github.com:mpawlow/github-milestone-generator.git
```

### (1.3) Directory location

```shell
cd couchdb-conflict-remover
```

### (1.4) Generate an API key and password

- Select the target CouchDB / Cloudant database.
- Generate an API key and password with the following permissions:
   - `_reader`
   - `_writer`

### (1.5) Create a conflicts view

- Select the target CouchDB / Cloudant database.
- Create a new `conflicts` design document with a `conflicts` view.
   - Use the [conflicts.js](./design_docs/conflicts.js) design document.

### (1.6) Create an environment script

- In the `./scripts` directory, copy `setup-environment.sh.template` to `setup-environment.sh`.
- In `setup-environment.sh`, specify values for the following environment variables:
   - `CLOUDANT_ACCOUNT`
   - `CLOUDANT_API_KEY`
   - `CLOUDANT_PASSWORD`

### (1.7) Run the environment script

```shell
. ./scripts/setup-environment.sh
```

### (1.8) Create a Python environment

```shell
. ./scripts/python/create-venv.sh
```

### (1.9) Activate the Python environment

```shell
. ./scripts/python/activate-venv.sh
```

### (1.10) Install the Python libraries

```shell
make install
```

### (1.11) Verify the installation

*(Optional)*

```shell
make verify
```

## (2) Usage

```shell
$ python index.py --help
usage: index.py [-h] -n DATABASE_NAME [-d] [-r RESULTS_DIR] [-c CSV_FILE] [-s SUMMARY_FILE]

optional arguments:
  -h, --help            show this help message and exit
  -n DATABASE_NAME, --database-name DATABASE_NAME
                        The name of the target Cloudant database.
  -d, --delete          Enable deletion mode. Default: False.
  -r RESULTS_DIR, --results-dir RESULTS_DIR
                        The directory name to use for storing results. Default: results/conflicts_results_2021-03-25_11-36-57.
  -c CSV_FILE, --csv-file CSV_FILE
                        The CSV filename to use for outlining Cloudant database conflicts. Default: conflicts_details_2021-03-25_11-36-57.csv.
  -s SUMMARY_FILE, --summary-file SUMMARY_FILE
                        The summary filename to use for outlining Cloudant database conflicts. Default: conflicts_summary_2021-03-25_11-36-57.txt.

=== Environment Variables ===

CLOUDANT_ACCOUNT : Cloudant account name.
CLOUDANT_API_KEY : Cloudant API key.
CLOUDANT_PASSWORD : Cloudant password.

=== Examples ===

export CLOUDANT_ACCOUNT=account_name
export CLOUDANT_API_KEY=api_key
export CLOUDANT_PASSWORD=password

python index.py -d -n projects-api_prod-dallas
```
