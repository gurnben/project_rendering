# cpaas-project-rendering

Python project to assist in rendering CPaaS pipeline objects

This is an alternative to creating the YAML files yourself directly

# Usage

This package can be easily run installed and run via `pipenv`.

```bash
$ pipenv install -e "git+https://github.com/arewm/project_rendering.git#egg=project_rendering"
Creating a virtualenv for this project...
[...]
Installing -e git+https://github.com/arewm/project_rendering.git#egg=project_rendering...
Adding project_rendering to Pipfile's [packages]...
✔ Installation Succeeded
Pipfile.lock (926f24) out of date, updating to (e1f8ae)...
Locking [dev-packages] dependencies...
Locking [packages] dependencies...
Building requirements...
Resolving dependencies...
✔ Success!
Updated Pipfile.lock (e1f8ae)!
Installing dependencies from Pipfile.lock (e1f8ae)...
  🐍   ▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉ 1/1 — 00:00:04
To activate this project's virtualenv, run pipenv shell.
Alternatively, run a command inside the virtualenv with pipenv run.
$ pipenv run run_render.py
usage: run_render.py [-h] [--version] [-t PRODUCT_JINJA_TEMPLATE_PATH] [-o PRODUCT_YAML_OUTPUT_PATH] PRODUCT_CONFIGURATION_YAML_PATH BUILDS_CONFIGURATION_YAML_PATH
run_render.py: error: the following arguments are required: PRODUCT_CONFIGURATION_YAML_PATH, BUILDS_CONFIGURATION_YAML_PATH
```

# Testing

There are currently three manual test cases that you can run to ensure that the scripts still work.
After running the following test cases, the output.yml file in each directory _should_ be unchanged.

```bash
$ python3 tests/test_runner.py tests/case_1/product-config.yaml tests/case_1/builds.yaml -o tests/case_1/output.yml
$ python3 tests/test_runner.py tests/case_2/product-config.yaml tests/case_2/builds.yaml -t tests/case_2/product.yaml.jinja -o tests/case_2/output.yml
$ python3 tests/test_runner.py tests/case_3/product-config.yaml tests/case_3/builds.yaml -o tests/case_3/output.yml
```