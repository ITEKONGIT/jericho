# Internal Network Tooling

Tools and scripts designed for internal LAN assessments, pivoting, and hardware exploitation.

## Printers

* **`printers/PRET`** — Printer Exploitation Toolkit. Used for connecting to devices via port 9100/tcp, capturing print jobs, and extracting sensitive memory or credentials from networked printers.

> **Vendored code — not ours.** `printers/PRET/` is PRET (**v0.25**) by Jens Mueller (Ruhr University Bochum), developed as part of a master's thesis on printer security. It ships under its own terms: see `printers/PRET/LICENSE.md` and `printers/PRET/DISCLAIMER.md`. Its upstream documentation, command reference, and the Hacking Printers wiki links all live in `printers/PRET/README.md`.
>
> Two things to know before touching it:
> 1. It targets a **Python 2** interpreter upstream, so the files emit `SyntaxWarning`s under Python 3. That is why the repo's byte-compile gate excludes this directory — a syntax error we introduced elsewhere should not be able to hide behind upstream noise.
> 2. `mibs/`, `db/`, `fonts/`, `lpd/`, `overlays/`, and `testpages/` are upstream data resources, not our content. Don't reformat or "fix" them.
