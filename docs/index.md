# OptiArchitect documentation

OptiArchitect is an open-source Python toolkit that implements the classical operations research
algorithms as small, inspectable functions and **verifies every result independently**.

| Page | Contents |
|---|---|
| [installation.md](installation.md) | Requirements, extras, installation, testing the installation |
| [usage.md](usage.md) | Console, web application and Python API, with real output |
| [study.md](study.md) | Student study mode: questionnaires, reports, hosting, ethics checklist |
| [methods.md](methods.md) | The algorithms, the routing/diagnosis rules and the verification checks |
| [api.md](api.md) | API reference generated from the docstrings |
| [../examples/](../examples) | Three runnable scripts (LP, transportation/assignment, 1-D non-linear) |
| [../validation/](../validation) | Reproducible comparison with SciPy |
| [../CONTRIBUTING.md](../CONTRIBUTING.md) | How to contribute, report problems and get help |

**Supported scope.** Linear programming with any mix of `<=`, `>=`, `=` rows and `x >= 0`; transportation and
assignment problems (including unbalanced and rectangular ones); single-variable non-linear optimization on an
interval. Dense tableaux are used, so the package targets teaching-size and benchmark-size models, not large sparse
problems. There is no integer programming.
