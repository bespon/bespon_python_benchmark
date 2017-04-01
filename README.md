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
  * `--timeit_number <number>`:  Number of times to benchmark each package
    (default: 10).  `timeit` keeps the best time.
  * `--template_number <number>`:  Each package is used with a dataset that is
    created by concatenating a data template this many times (default: 1000).
    Note that the data template contains a template field `{num}` that
    is formatted with successive integers from 0 up to the number of
    concatenations, so that the final dataset does not contain duplicate data.
  * `--py_out`:  By default, results are printed to stdout as a sorted table.
    This causes them to be printed as a string representation of a Python
    dict.

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
Python 3.6 (CPython, Windows)
----------------------------------------
json            0.016726604813152142
yaml (CLoader)  0.5809957846299323
bespon          1.217191325372268
toml            1.4090164097498867
pytoml          5.019502815708046
yaml            8.87523552005168
```
If `--py_out` is used, then the result is a string representation of a Python
dict that contains complete information about the run.  For example,
```
{'python': 'Python 3.6 (CPython, Windows)',
 'template_number': 1000,
 'timeit_number': 10,
 'results': {'json': 0.016817009404418066,
             'bespon': 1.2157752793472614,
             'yaml': 8.743431477415822,
             'yaml (CLoader)': 0.572789446829228,
             'toml': 1.4005540718930085,
             'pytoml': 5.088717916610104}}
```


## Notes on use

Decoding benchmarks can take a long time to run if the option
`--template_number` is increased significantly beyond 1000 when the `pytoml`
package is being used, due to nonlinear performance scaling.
