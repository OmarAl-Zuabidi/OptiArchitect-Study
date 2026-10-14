# Security policy

## Supported versions
The latest release receives fixes.

## Reporting a vulnerability
Please do **not** open a public issue for a security problem. Use GitHub's private vulnerability reporting
("Security" tab -> "Report a vulnerability") on this repository.

## Scope note
The program accepts mathematical formulas typed by the user (Part 3). They are validated against an
abstract-syntax-tree white-list before reaching SymPy and are never passed to `eval`. A formula that
bypasses this validation is considered a security issue.
