# ------------------------------------------------------------------------------
# Copyright 2021 Mike Pawlowski
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

define USAGE

Usage: make [task [task ...]]

Targets:
   help
   outdated
   pip_verify
   python_verify
   pylint_verify
   yamllint_verify
   verify
   install
   yamllint
   pylint
   lint

Examples:
   make outdated
   make verify
   make install
   make lint

endef

export USAGE

.PHONY: help \
	outdated \
	pip_verify \
	python_verify \
	pylint_verify \
	yamllint_verify \
	verify \
	install \
	yamllint \
	pylint \
	lint
.DEFAULT: help

# Variables ------------------------------------------------------------------->

# Targets --------------------------------------------------------------------->

help:
	@echo "$$USAGE"

outdated:
	@echo "[outdated]"
	python -m pip list --outdated

pip_verify:
	@echo "[pip_verify]"
	which pip
	pip --version

python_verify:
	@echo "[python_verify]"
	which python
	python --version

pylint_verify:
	@echo "[pylint_verify]"
	which pylint
	pylint --version

yamllint_verify:
	@echo "[yamllint_verify]"
	which yamllint
	yamllint --version

verify: pip_verify python_verify pylint_verify yamllint_verify
	@echo "[verify]"

install:
	@echo "[install]"
	python -m pip install -r requirements.txt

yamllint:
	@echo "[yamllint]"
	yamllint ./.travis.yml ./.yamllint

pylint:
	@echo "[pylint]"
	python -m pylint lib index.py

lint: yamllint pylint
	@echo "[lint]"
