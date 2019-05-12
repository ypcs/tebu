#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Template Builder (tebu)

This tool builds Jinja2 templates using user-provided variables.

You can eg. create configuration templates, then provide some local or
environment-specific variables, and compile full configuration files.

Requires jinja2 and YAML libraries for Python 3, on Debian/Ubuntu

    apt-get install python3-jinja2 python3-yaml

License: MIT.
"""

import argparse
import json
import logging
import os
import sys
import yaml

from jinja2 import Template


class OrderedAction(argparse.Action):
    """Store information about ordering of args in argparse

    Source: <https://stackoverflow.com/a/9028031>
    """
    def __call__(self, parser, namespace, values, option_string=None):
        if 'ordered_args' not in namespace:
            setattr(namespace, 'ordered_args', [])
        previous = namespace.ordered_args
        previous.append((self.dest, values))
        setattr(namespace, 'ordered_args', previous)
        setattr(namespace, self.dest, values)


class BooleanOrderedAction(OrderedAction):
    def __call__(self, parser, namespace, values, option_string=None):
        values = [bool(x) for x in values]
        super().__call__(parser=parser, namespace=namespace, values=values,
                         option_string=option_string)


class KeyValueOrderedAction(OrderedAction):
    def __call__(self, parser, namespace, values, option_string=None):
        super().__call__(parser=parser, namespace=namespace, values=values,
                         option_string=option_string)


class TemplateBuilder(object):
    def __init__(self, values=None):
        self.logger = logging.getLogger(__name__)
        if values:
            self.values = values
        else:
            self.values = {}

    def compile(self, template, filename=None, outdir=None, write_file=True):
        out = None
        tm = Template(template.read())
        out = tm.render(**self.values)
        if filename is None:
            fn = os.path.basename(template.name).replace('.j2', '')
            if outdir is None:
                outdir = os.path.dirname(template.name)
            filename = os.path.join(outdir, fn)
        if filename and write_file:
            dn = os.path.dirname(filename)
            os.makedirs(dn, exist_ok=True)
            with open(filename, 'w') as ofile:
                ofile.write(out)
        return out

    def __str__(self):
        return self.compile()


def from_json(filename):
    return json.load(filename)


def from_yaml(filename):
    return yaml.load(filename)


def from_var(s):
    if not isinstance(s, list) or len(s) != 1:
        raise ValueError
    parts = s[0].split('=', 1)
    if len(parts) != 2:
        raise ValueError
    k = parts[0].strip().lower()
    v = parts[1]
    return {k: v}


def parse_values(args):
    values = {}
    for arg in args:
        if arg[0] == 'env':
            values.update(os.environ)
        elif arg[0] == 'json':
            for f in arg[1]:
                values.update(from_json(f))
        elif arg[0] == 'yaml':
            for f in arg[1]:
                values.update(from_yaml(f))
        elif arg[0] == 'variables':
            values.update(from_var(arg[1]))
        else:
            raise ValueError
    return values


def main(argv=sys.argv):
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-s', '--set-variable', nargs='*', dest='variables',
                        action=KeyValueOrderedAction,
                        help="Set variable, (key=value).")
    parser.add_argument('-j', '--from-json', nargs='*', dest='json',
                        action=OrderedAction,
                        help="Read variables from JSON file.",
                        type=argparse.FileType('r', encoding='utf-8'))
    parser.add_argument('-y', '--from-yaml', nargs='*', dest='yaml',
                        action=OrderedAction,
                        help="Read variables from YAML file.",
                        type=argparse.FileType('r', encoding='utf-8'))
    parser.add_argument('-e', '--from-env', dest='env',
                        action=BooleanOrderedAction,
                        help="Read variables from environment.")
    parser.add_argument('-t', '--templates', dest='templates', nargs='+',
                        help="Path to template file(s).",
                        type=argparse.FileType('r', encoding='utf-8'))
    parser.add_argument('-o', '--outdir', dest='outdir', required=True,
                        help='Directory to save compiled files in.')

    args = parser.parse_args()
    logger.debug("Args: {}".format(args))
    values = parse_values(args.ordered_args)

    tb = TemplateBuilder(values=values)
    for template in args.templates:
        tb.compile(template=template, outdir=args.outdir)


if __name__ == '__main__':
    sys.exit(main())
