# Benchmark BespON in Python

Code for comparing performance of JSON, BespON, YAML, and TOML in Python.
It uses whatever standard/popular Python packages are installed for these
formats.  All timing is performed with
[`timeit`](https://docs.python.org/3.6/library/timeit.html).

Benchmark results should be interpreted with the understanding that they
may be highly dependent on the form of the benchmark data.  In formats in
which data may have multiple representations, the exact representation used
may also play a significant role.



## Decoding benchmark

**Usage:**
```
python bespon_decoding_benchmark.py
```

**Options:**

  * `--bespon_py <path>`:  Use `bespon` package at specified path, rather than
    installed `bespon` package.
  * `--timeit_number <number>`:  Number of times that the benchmark code is
    executed during each timed run (default: 1).
  * `--timeit_repeat <number>`:  Number of timed runs that are performed
    per package (default: 10).  The minimum time obtained for each
    package is reported.
  * `--template_number <number>`:  Each package is used with a dataset that is
    created by concatenating a data template this many times (default: 1000).
    Note that the data template contains a template field `{num}` that
    is formatted with successive integers from 0 up to the number of
    concatenations, so that the final dataset does not contain duplicate data.
  * `--py_out`:  By default, results are printed to stdout as a sorted table.
    This causes them to be printed as a string representation of a Python
    dict instead.

**Data template:**  The built-in data template is a mix of dicts and lists
of strings.
```text
key{num} =
    first_subkey{num} = "Some text that goes on for a while {num}"
    second_subkey{num} = "Some more text that also goes on and on {num}"
    third_subkey{num} =
      * "first list item {num}"
      * "second list item {num}"
      * "third list item {num}"
```

**Output:**  Results are printed to stdout.
For example,
```
Python 3.6 (CPython, Linux)
----------------------------------------
json            0.0015381950000090683
yaml (CLoader)  0.05863191299999926
bespon          0.09437812199999485
toml            0.16262568400000532
pytoml          0.44667368100002136
yaml            0.9945613440000045
```
If `--py_out` is used, then the result is a string representation of a Python
dict that contains complete information about the run.  For example,
```
{'python': 'Python 3.6 (CPython, Linux)', 'template_number': 1000,
 'timeit_number': 1, 'timeit_repeat': 10,
 'results': {'json': 0.0015339250000465654, 'bespon': 0.09245784400002321,
             'yaml': 0.9864068850000081, 'yaml (CLoader)': 0.05825553699997954,
             'toml': 0.16168690499995364, 'pytoml': 0.4443770299999983}}
```


## Notes on use

Decoding benchmarks can take a long time to run if the option
`--template_number` is increased significantly beyond 1000 when the `pytoml`
package is being used, due to nonlinear performance scaling.
