# Code Standard

This document defines the minimum engineering standard for this project. All
new code and changes to existing code must follow these rules.

## Python Environment and Dependencies

- Use Python 3.12 or newer unless the project configuration specifies another
  supported version.
- Use [`uv`](https://docs.astral.sh/uv/) for Python version management,
  virtual environments, dependency management, locking, and command execution.
- Keep the virtual environment in the repository root at `.venv`.
- Never install project packages into the system Python or user site-packages.
- Declare runtime and development dependencies in `pyproject.toml` and commit
  `uv.lock`.
- Do not maintain ad hoc, manually edited dependency lists when `uv` can manage
  them.
- Pin the supported Python range in `pyproject.toml`. Let `uv.lock` record exact
  transitive versions for reproducible installs.
- Never commit `.venv`, caches, build output, coverage output, or secrets.

Set up and use the environment with:

```bash
uv python install 3.12
uv venv --python 3.12
source .venv/bin/activate
uv sync --all-groups
```

On Windows PowerShell, activate it with:

```powershell
.venv\Scripts\Activate.ps1
```

Manage packages through `uv`; do not call `pip install` directly:

```bash
uv add package-name
uv add --dev pytest
uv remove package-name
uv lock --upgrade-package package-name
```

Run project commands in the managed environment. Activating `.venv` is useful
for an interactive shell; `uv run` is preferred in documentation, scripts, and
CI because it guarantees the correct environment:

```bash
uv run python -m package_name
uv run pytest
```

## Clean Code

### Design

- Keep each module, class, and function focused on one responsibility.
- Prefer small, composable functions and explicit data flow over hidden mutable
  state.
- Separate domain logic from I/O, frameworks, databases, clocks, randomness,
  and external services.
- Depend on narrow interfaces at system boundaries so behavior can be tested
  without network or filesystem access.
- Prefer simple code that solves the current requirement. Do not add
  abstractions for hypothetical future use.
- Remove dead code instead of commenting it out. Version control preserves
  history.
- Avoid global mutable state and import-time side effects.

### Naming and Readability

- Use names that reveal intent and match the domain language.
- Follow PEP 8: `snake_case` for functions and variables, `PascalCase` for
  classes, and `UPPER_CASE` for constants.
- Use positive, readable boolean names such as `is_valid` or `has_access`.
- Replace unexplained literals with well-named constants when the meaning is
  not immediately obvious.
- Write comments to explain *why*, constraints, or non-obvious trade-offs.
  Do not restate what clear code already says.
- Add docstrings to public modules, classes, and functions when their contract
  is not obvious from the signature and types.

### Functions and Types

- Give functions a small, explicit parameter list. Group related values in a
  typed object when that improves clarity.
- Add type annotations to public interfaces and new or changed functions.
- Return consistent types; do not use sentinel values whose meaning is unclear.
- Validate data at system boundaries and keep internal invariants explicit.
- Prefer immutable values where practical.
- Raise specific exceptions with actionable messages. Do not use bare
  `except`, silently swallow failures, or use exceptions for normal control
  flow.

### Formatting and Quality

- Use an automated formatter and linter; do not debate hand formatting in
  reviews. The recommended baseline is Ruff for both formatting and linting.
- Use a static type checker for typed production code. The recommended
  baseline is Pyright or mypy, configured in `pyproject.toml`.
- Keep all quality-tool configuration in `pyproject.toml` where supported.
- A change is complete only when formatting, linting, type checks, and tests
  pass locally and in CI.

Recommended commands:

```bash
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
```

## Test-Driven Development

Use the red-green-refactor cycle for every behavior change:

1. **Red:** Write the smallest test that describes the required behavior and
   confirm it fails for the expected reason.
2. **Green:** Write the minimum production code needed to make the test pass.
3. **Refactor:** Improve names, structure, and duplication while keeping all
   tests green.

Do not write production behavior before its failing test, except for a short,
discarded exploration used to understand an unfamiliar API. Recreate the final
implementation through the TDD cycle.

### Test Requirements

- Use `pytest` as the default test framework.
- Test observable behavior and public contracts, not private implementation
  details.
- Use the Arrange-Act-Assert structure when it improves clarity.
- Give tests behavior-focused names, for example
  `test_rejects_order_when_inventory_is_insufficient`.
- Each test must be deterministic, isolated, and repeatable in any order.
- Do not rely on the developer's machine, current time, random state, network,
  or shared external services. Inject or control those dependencies.
- Prefer real, lightweight domain objects. Use fakes or stubs at external
  boundaries; use mocks only when the interaction itself is part of the
  contract.
- Every bug fix must begin with a regression test that fails before the fix and
  passes afterward.
- Cover normal behavior, meaningful boundary cases, and failure paths.
- Keep tests fast. Separate slower integration and end-to-end tests with
  explicit markers.
- Treat coverage as a diagnostic, not a target to game. New or changed behavior
  must be covered even when the repository-wide percentage is already high.

### Test Layout

Mirror production modules under `tests/`:

```text
src/package_name/service.py
tests/unit/test_service.py
tests/integration/test_service_integration.py
```

Run the smallest relevant test during the red-green loop, then the full suite
before considering the change complete:

```bash
uv run pytest tests/unit/test_service.py -q
uv run pytest
```

## Definition of Done

A change is done when:

- Its expected behavior and acceptance criteria are clear.
- A test was observed failing before the production change.
- The minimum implementation passes the new test.
- The code was refactored without changing behavior.
- Relevant unit, integration, and regression tests pass.
- Formatting, linting, and type checks pass.
- Dependency and lockfile changes are intentional and committed.
- Documentation is updated when a public interface or developer workflow
  changes.
- No secrets, local environment files, generated artifacts, or unrelated
  changes are included.
