# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the BSD 3-Clause License:
# http://opensource.org/licenses/BSD-3-Clause
#

'''
Perform simple Python decoding benchmarks for JSON, BespON, YAML, and TOML,
using whatever packages are available.  Formats are omitted if
standard/popular packages aren't found.

Benchmark results should be interpreted with the understanding that they
may be highly dependent on the form of the benchmark data.  In formats where
data may have multiple representations, the exact representation used may
also play a significant role.

Benchmarks may be customized simply by editing the templates and re-executing.
'''


import sys
import os
import timeit
import platform
import argparse




parser = argparse.ArgumentParser()
parser.add_argument('--bespon_py', help='Use bespon package at specified path, rather than installed bespon package')
parser.add_argument('--timeit_number', type=int, default=1,
                    help='Number of times to load test data for each package per timed run')
parser.add_argument('--timeit_repeat', type=int, default=10,
                    help='Number of times to measure performance of each package (min is reported)')
parser.add_argument('--template_number', type=int, default=1000,
                    help='Number of times to concatenate the template for each language in creating the decoding dataset')
parser.add_argument('--py_out', default=False, action='store_true',
                    help='Print results formatted as a Python dict')
args = parser.parse_args()


if args.bespon_py is not None:
    sys.path.insert(1, os.path.abspath(os.path.expanduser(os.path.expandvars(args.bespon_py))))




# Python and system information
py_info = 'Python {0}.{1} ({2}, {3})'.format(sys.version_info.major,
                                             sys.version_info.minor,
                                             platform.python_implementation(),
                                             platform.system())




class Package(object):
    '''
    Information needed to run benchmarks with a given package.
    '''
    def __init__(self, *args, **kwargs):
        if args:
            raise TypeError('Explicit keyword arguments are required')
        self.name = kwargs.pop('name')
        self.variant = kwargs.pop('variant', None)
        self.language = kwargs.pop('language')
        self.loads_method = kwargs.pop('loads_method', 'loads')
        self.loads_args = kwargs.pop('loads_args', None)
        self.import_template = kwargs.pop('import_template', 'import {0}'.format(self.name))
        self.data_template = kwargs.pop('data_template').replace('"""', '\\"""')
        if kwargs:
            raise TypeError('Unknown keyword arguments')




# Templates.  These are duplicated `args.template_number` times to assemble a
# dataset.
#
# json template must always be a complete, self-contained dict or list.  The
# outermost `[]` or `{}` are stripped off during data generation, and then
# re-inserted around the final dataset.
json_template = '''\
{{
"key{num}": {{
    "first_subkey{num}": "Some text that goes on for a while {num}",
    "second_subkey{num}": "Some more text that also goes on and on {num}",
    "third_subkey{num}": [
        "first list item {num}",
        "second list item {num}",
        "third list item {num}"
    ]
}}
}}
'''

bespon_template = '''\
key{num} =
    first_subkey{num} = "Some text that goes on for a while {num}"
    second_subkey{num} = "Some more text that also goes on and on {num}"
    third_subkey{num} =
      * "first list item {num}"
      * "second list item {num}"
      * "third list item {num}"
'''

yaml_template = '''\
key{num}:
    first_subkey{num}: "Some text that goes on for a while {num}"
    second_subkey{num}: "Some more text that also goes on and on {num}"
    third_subkey{num}:
      - "first list item {num}"
      - "second list item {num}"
      - "third list item {num}"
'''

toml_template = '''\
[key{num}]
first_subkey{num} = "Some text that goes on for a while {num}"
second_subkey{num} = "Some more text that also goes on and on {num}"
third_subkey{num} = [
    "first list item {num}",
    "second list item {num}",
    "third list item {num}"
]
'''




# Define packages that will be benchmarked (if installed).  The PyYAML CLoader
# is run separately if available.  It uses LibYAML (C implementation) for
# much higher performance.  Both TOML implementations for Python that are
# listed at https://github.com/toml-lang/toml/ are used if installed.
# However, it should be noted that pytoml is in maintentance-only mode
# (https://github.com/avakar/pytoml/issues/15), although it may serve as the
# basis for a future TOML implementation for PEP 518
# (https://www.python.org/dev/peps/pep-0518/).
packages = [Package(name='json', language='JSON', data_template=json_template),
            Package(name='bespon', language='BespON', data_template=bespon_template),
            Package(name='yaml', language='YAML', loads_method='load', data_template=yaml_template),
            Package(name='yaml', language='YAML', variant='CLoader',
                    loads_method='load', loads_args=['Loader=CLoader'],
                    data_template=yaml_template,
                    import_template='import yaml; from yaml import CLoader'),
            Package(name='toml', language='TOML', data_template=toml_template),
            Package(name='pytoml', language='TOML', data_template=toml_template)]


# Create a list of available packages
available_packages = []
for pkg in packages:
    try:
        exec(pkg.import_template)
        available_packages.append(pkg)
    except ImportError:
        pass


# Test to make sure that all templates produce identical data
test_data = []
for pkg in available_packages:
    template = pkg.data_template.format(num=1)
    if pkg.loads_args is None:
        exec('data = {package}.{loads}("""{template}""")'.format(package=pkg.name, loads=pkg.loads_method, template=template))
    else:
        exec('data = {package}.{loads}("""{template}""", {args})'.format(package=pkg.name, loads=pkg.loads_method, template=template, args=','.join(pkg.loads_args)))
    test_data.append(data)
if len(test_data) > 1 and not all([test_data[0] == test_data_n for test_data_n in test_data[1:]]):
    raise ValueError('Data templates do not all yield the same data')


# Perform actual benchmark runs
benchmark_results = {}
for pkg in available_packages:
    if pkg.language.lower() == 'json':
        data_template = pkg.data_template.strip()
        if data_template[0] == '[' and data_template[-1] == ']':
            data_template == data_template[1:-1]
            data_string = '[\n{0}\n]\n'.format(',\n'.join(data_template.format(num=num) for num in range(args.template_number)))
        elif data_template[0:2] == '{{' and data_template[-2:] == '}}':
            data_template = data_template[2:-2]
            data_string = '{{\n{0}\n}}\n'.format(',\n'.join(data_template.format(num=num) for num in range(args.template_number)))
        else:
            raise ValueError('Invalid json template')
    else:
        data_string = '\n'.join(pkg.data_template.format(num=num) for num in range(args.template_number))
    if pkg.loads_args is None:
        code = '{package}.{loads}(data_string)'.format(package=pkg.name, loads=pkg.loads_method)
    else:
        code = '{package}.{loads}(data_string, {args})'.format(package=pkg.name, loads=pkg.loads_method, args=','.join(pkg.loads_args))
    setup = '{imp}\ndata_string = """\n{data_string}"""\n'.format(imp=pkg.import_template, data_string=data_string)
    benchmark_times = timeit.repeat(code, setup=setup, repeat=args.timeit_repeat, number=args.timeit_number)
    benchmark_time = min(benchmark_times)
    if pkg.variant is None:
        benchmark_results[pkg.name] = benchmark_time
    else:
        benchmark_results['{0} ({1})'.format(pkg.name, pkg.variant)] = benchmark_time

output = {'python': py_info, 'template_number': args.template_number,
          'timeit_number': args.timeit_number, 'results': benchmark_results}
if args.py_out:
    print(str(output))
else:
    print('\n' + output['python'])
    print('-'*40)
    padding = max([len(k) for k in output['results']])
    for p, t in sorted([(k, v) for k, v in output['results'].items()], key=lambda x: x[1]):
        print(p.ljust(padding+2) + str(t))
