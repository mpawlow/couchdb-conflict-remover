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
   - `_reader` (for scanning)
   - `_writer` (for deletion)

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

### (2.1) Help

```shell
$ python index.py --help
usage: index.py [-h] -n DATABASE_NAME [-d] [-r RESULTS_DIR] [-t THRESHOLD]

optional arguments:
  -h, --help            show this help message and exit
  -n DATABASE_NAME, --database-name DATABASE_NAME
                        The name of the target CouchDB / Cloudant database.
  -d, --delete          Enable deletion mode. Default: False.
  -r RESULTS_DIR, --results-dir RESULTS_DIR
                        The directory name to use for storing results. Default: results/conflicts_results_2021-03-31_01-03-46.
  -t THRESHOLD, --threshold THRESHOLD
                        The maximum threshold of revisions used to determine whether a conflicted document is included during the deletion phase. Default: 5000.

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

### (2.2) Sample Output

```
================================================================================
Overview
================================================================================

- Cloudant Account:                   dataai
- Cloudant Database:                  projects-api_prod-dallas
- Total Documents:                    5163
- Elapsed Time:                       0:05:46.245396

================================================================================
Scan Details
================================================================================

- Total Conflicted Documents:         291
- Total Conflicted Revisions:         2127

================================================================================
Deletion Details
================================================================================

- Total Conflicted Documents:         291
- Total Resolved Documents:           291
- Total Conflicted Revisions:         2127
- Total Deleted Revisions:            2127
```

### (2.3) Output Files

- (a) Creates a CSV file containing details from the scan phase
   - e.g. `conflicts_deletion_details_2021-03-28_19-03-31.csv`
- (b) Creates a CSV file containing details from the deletion phase
   - e.g. `conflicts_scan_details_2021-03-28_19-03-31.csv`
- (c) Creates a text file containing summary information for all phases (as shown in the `Sample Output` section)
   - e.g. `conflicts_summary_2021-03-28_19-03-31.txt`
