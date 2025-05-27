# GitHub Copilot — Repository Code-Generation Rules  (Python • Azure Data & AI)

## 1 · Language & Style
- Target the **highest Python version supported by our Azure runtime image** (currently **3.11**) and add type hints.
- Format with **Ruff** (`ruff format`). If an existing module already uses **Black**, match Black to avoid churn.
- Lint and sort imports with `ruff check`; keep line length ≤ 120 chars; use f-strings.
- Write Google-style docstrings for every public function, class, and module.

## 2 · Azure SDK Usage
- Use official **Azure SDK** packages (`azure-*`) instead of raw REST or CLI calls.
- **Authenticate with `DefaultAzureCredential()`**. Store secrets in **Azure Key Vault** or **Managed Identity**—never hard-code them.
- Prefer async SDK variants (`azure.*.aio`) for production I/O-bound workloads; synchronous calls are fine for quick scripts or notebooks.
- Catch **`AzureError`**, log context, then raise a domain-specific exception.

## 3 · Project Structure
- Keep each source file **< 400 LOC**; split larger logic into packages under `/src`.
- Mirror source layout in `/tests`; use relative imports inside the package.
- Include a `py.typed` marker so type checkers treat the package as typed.

## 4 · Testing
- Use **Pytest**. For every feature, add tests for happy path, edge cases, and expected failures.
- Mock cloud calls with stubs (e.g., `pytest-azure`); avoid live Azure traffic in unit tests.
- Require **≥ 90 %** line coverage; enforce in CI with `pytest --cov --cov-fail-under=90`.

## 5 · Dependencies & Packaging
- Manage dependencies with **UV** and commit `uv.lock`. Where UV is unavailable (CI or client policy), fall back to **pip-tools** (`requirements.in` + `requirements.txt`).
- Pin direct dependencies; update via explicit PRs rather than transitive upgrades.

## 6 · Data & AI Conventions
- Use **Pandas** (or **Polars** for datasets > 10 M rows); track experiments with **MLflow** through Azure ML.
- When calling **Azure OpenAI**, stream responses and implement exponential back-off on `429` / `503`.

## 7 · Documentation & Explainability
- Update `README.md` or `/docs/` whenever APIs or setup steps change.
- Add an inline `# Reason:` comment before any non-obvious logic block.

## 8 · AI Behaviour Guardrails
- Ask clarifying questions if requirements are ambiguous.
- Reference only documented Azure SDK or PyPI packages; do not invent imports.
- Verify file paths and module names exist before referencing them.