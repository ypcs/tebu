# tebu
Template Builder (tebu) - Build Jinja2 templates &amp; read variables from env, YAML, JSON &amp; command line


## Usage
To merge values from some JSON and YAML files + command line parameters, and then to compile example template, run

    python3 tebu.py \
        --json examples/values1.json \
        --yaml examples/values2.yaml \
        -s myruntimevalue=something \
        --template examples/template2.conf.j2

You can pass multiple sources files and runtime values. You must pass at last one template.


## Dependencies
This app depends on Python libraries `jinja2` and `pyyaml`. You can install those with

    pip install -r requirements.txt

or

    apt-get install python3-jinja2 python3-yaml


## Contributing
Patches welcome, Travis tests must pass (see `.travis.yml`, basically PEP8).
