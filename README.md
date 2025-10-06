# SkunkScrape

[![CI](https://img.shields.io/github/actions/workflow/status/SKUNKSCRAPE/skunkscrape/ci.yml?branch=main&label=CI)](https://github.com/SKUNKSCRAPE/skunkscrape/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-blue.svg)](#requirements)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linter: ruff](https://img.shields.io/badge/linter-ruff-46a2f1.svg)](https://github.com/astral-sh/ruff)
[![Tests: pytest](https://img.shields.io/badge/tests-pytest-0a9edc.svg)](https://docs.pytest.org/)
[![Coverage](https://img.shields.io/badge/coverage-codecov-ff69b4.svg)](https://app.codecov.io/github/SKUNKSCRAPE/skunkscrape) <!-- swap with real Codecov badge once connected -->
[![Open Issues](https://img.shields.io/github/issues/SKUNKSCRAPE/skunkscrape.svg)](https://github.com/SKUNKSCRAPE/skunkscrape/issues)
[![Last Commit](https://img.shields.io/github/last-commit/SKUNKSCRAPE/skunkscrape.svg)](https://github.com/SKUNKSCRAPE/skunkscrape/commits/main)
[![Repo Size](https://img.shields.io/github/repo-size/SKUNKSCRAPE/skunkscrape.svg)](#)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](#contributing)

<!-- Optional (uncomment when applicable)
[![PyPI](https://img.shields.io/pypi/v/skunkscrape.svg)](https://pypi.org/project/skunkscrape/)
[![Docker Pulls](https://img.shields.io/docker/pulls/skunkscrape/skunkscrape.svg)](https://hub.docker.com/r/skunkscrape/skunkscrape)
-->

Modular ZA-focused lead discovery and scraping toolkit with **CLI + GUI**, proxy rotation, discovery utilities, and export pipeline.

## Table of Contents

- [Features](#features)  
- [Architecture](#architecture)  
- [Project Layout](#project-layout)  
- [Requirements](#requirements)  
- [Quick Start](#quick-start)  
- [Configuration](#configuration)  
  - [.env](#env)  
  - [Proxies](#proxies)  
  - [Plugin Manifest](#plugin-manifest)  
- [Usage](#usage)  
  - [CLI](#cli)  
  - [GUI](#gui)  
  - [Discovery Utilities](#discovery-utilities)  
  - [Pipeline](#pipeline)  
  - [Scheduling](#scheduling)  
- [Exports](#exports)  
- [Packaging & Deployment](#packaging--deployment)  
  - [PyInstaller](#pyinstaller)  
  - [Docker](#docker)  
- [Development](#development)  
  - [Testing](#testing)  
  - [Linting & Formatting](#linting--formatting)  
- [Logging](#logging)  
- [Troubleshooting](#troubleshooting)  
- [Roadmap](#roadmap)  
- [Contributing](#contributing)  
- [License](#license)

## Features

- **Two entry points**: Python CLI (`skunkscrape`) and Tkinter GUI.  
- **Plugin architecture** with a simple `manifest.json`.  
- **Proxy rotation** supporting JSON and legacy text formats.  
- **ZA discovery tools** (CT, Common Crawl, directories/jobs).  
- **Pipeline hooks** for normalization, DNC/HLR enrichment (stubs), and exports.  
- **Scheduler** for recurring jobs (schedule/croniter).  
- **Packagable** as a single executable (PyInstaller) or container (Docker).

## Architecture

- **Core**: configuration, logging, shared utilities, exceptions.  
- **CLI**: orchestrates plugins and batches.  
- **GUI**: category → plugin selector + proxy picker.  
- **Plugins**: each scraper is self-contained and exposes `main()`.  
- **Discovery**: host/source generation for ZA domains and socials.  
- **Pipeline**: normalization, exporters, and scheduling.

## Project Layout

```

SkunkScrape/
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── requirements.txt
│
├── data/
│   ├── proxies/
│   │   ├── proxies.json
│   │   └── Webshare 10 proxies.txt
│   ├── seeds/
│   ├── logs/
│   ├── cache/
│   └── exports/
│
├── assets/
│   ├── banner.png
│   └── favicon.ico
│
├── skunkscrape/
│   ├── **init**.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   ├── utils.py
│   │   └── exceptions.py
│   ├── cli/
│   │   └── main.py
│   ├── gui/
│   │   └── main_gui.py
│   ├── plugins/
│   │   ├── manifest.json
│   │   ├── gumtree_scraper.py
│   │   ├── autotrader_scraper.py
│   │   ├── property24_scraper.py
│   │   └── smart_contact_crawler.py
│   ├── discovery/
│   │   ├── discover_coza_sources.py
│   │   ├── source_generator.py
│   │   └── discovery_runner.py
│   └── pipeline/
│       ├── collector.py
│       ├── exporter.py
│       └── scheduler.py
│
├── tests/
│   ├── test_plugins.py
│   ├── test_utils.py
│   └── test_gui_launcher.py
│
├── scripts/
│   ├── build_exe.ps1
│   ├── run_all_scrapers.ps1
│   ├── fix_plugins.ps1
│   └── scan_project_tree.ps1
│
└── Dockerfile
```


## Requirements

- Python **3.10+** (3.11 recommended).  
- Windows, macOS, or Linux.  
- Recommended: virtual environment.

---

## Quick Start

```bash
# Create & activate venv (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Copy environment template
copy .env.example .env
````

List available plugins and run one:

```bash
python -m skunkscrape.cli.main list
python -m skunkscrape.cli.main run --name gumtree_scraper
```

Launch the GUI:

```bash
python -m skunkscrape.gui.main_gui
```

---

## Configuration

### .env

Read by `skunkscrape/core/config.py`:

```
PROXY_FILE=data/proxies/proxies.json
LOG_LEVEL=INFO
EXPORT_DIR=data/exports
WEBHOOK_URL=
CRM_HUBSPOT_KEY=
CRM_SALESFORCE_KEY=
```

### Proxies

**Preferred**: `data/proxies/proxies.json`

```json
[
  { "host": "198.23.239.134", "port": 6540, "user": "userA", "pass": "secretA" },
  { "host": "45.38.107.97",   "port": 6014, "user": "userB", "pass": "secretB" }
]
```

**Legacy**: `Webshare 10 proxies.txt` (format `ip:port:user:pass`).

### Plugin Manifest

`skunkscrape/plugins/manifest.json` groups plugins by category:

```json
{
  "categories": {
    "Directories": { "plugins": ["gumtree_scraper","junkmail_scraper","sayellow_scraper"] },
    "Jobs":        { "plugins": ["pnet_scraper","careerjunction_scraper","careers24_scraper"] },
    "Property":    { "plugins": ["property24_scraper","privateproperty_scraper"] },
    "Autos":       { "plugins": ["autotrader_scraper"] }
  }
}
```

---

## Usage

### CLI

```bash
# List plugins
python -m skunkscrape.cli.main list

# Run a single plugin
python -m skunkscrape.cli.main run --name pnet_scraper

# Run all plugins defined in the manifest
python -m skunkscrape.cli.main run --all
```

**Plugin contract**: each plugin module exports a `main(**kwargs)` function.

### GUI

```bash
python -m skunkscrape.gui.main_gui
```

* Category → Plugin dropdowns come from `manifest.json`.
* Proxy dropdown comes from `PROXY_FILE`.

### Discovery Utilities

```bash
python -m skunkscrape.discovery.discover_coza_sources
python -m skunkscrape.discovery.source_generator --out data/seeds/sources.txt --max 100000 --threads 32 --proxy-file "data/proxies/Webshare 10 proxies.txt"
```

### Pipeline

* `collector.py`: normalization, DNC/HLR (stubs).
* `exporter.py`: CSV/CRM/Webhook/Discord exporters (stubs).

### Scheduling

* `scheduler.py`: wrappers around `schedule`/`croniter`.
* Drive schedules via env or a small YAML/TOML.

---

## Exports

Default export directory is `data/exports`.
CSV supported now; CRM/Webhook connectors ready for extension.

---

## Packaging & Deployment

### PyInstaller

```powershell
.\scripts\build_exe.ps1
# Output: dist/SkunkScrape.exe
```

### Docker

```bash
docker build -t skunkscrape:latest .
docker run --rm -it -v "%cd%/data:/app/data" skunkscrape:latest
```

---

## Development

```bash
pip install -r requirements.txt
pip install -e .[dev]
```

### Testing

```bash
pytest -q
```

### Linting & Formatting

```bash
ruff check .
black .
isort .
```

---

## Logging

Logs write to `data/logs/`. Configure level via `.env` (`LOG_LEVEL=DEBUG|INFO|WARNING`).

---

## Troubleshooting

* **`ModuleNotFoundError: skunkscrape`** → run from repo root or `pip install -e .`.
* **GUI `KeyError: 'categories'`** → ensure `plugins/manifest.json` exists and is valid.
* **Proxy timeouts** → validate credentials; test endpoints sans proxy first.
* **PyInstaller missing assets** → add `--add-data "assets;assets"`.

---

## Roadmap

* Web dashboard (React/Next.js) + Python API.
* Setuptools `entry_points` for plugin discovery.
* CRM connectors (HubSpot, Salesforce, Zoho).
* Enrichment (HLR/email validation).
* Cloud scheduler (Cloud Run + Scheduler or GitHub Actions cron).

---

## Contributing

Bug reports and pull requests are welcome on GitHub:
[https://github.com/SKUNKSCRAPE/skunkscrape](https://github.com/SKUNKSCRAPE/skunkscrape)

---

## License

This project is licensed under the MIT License — see [`LICENSE`](LICENSE).


### Badge quick-setup (optional)

* **CI badge**: ensure a workflow at `.github/workflows/ci.yml`.
* **Codecov**: create a project on Codecov and replace the Coverage badge with the Codecov URL they provide.
* **PyPI/Docker badges**: uncomment once you publish to PyPI or Docker Hub.

If you want, I can also drop in a minimal `.github/workflows/ci.yml` to power the CI badge and a `codecov.yml` starter so the coverage badge becomes live.
