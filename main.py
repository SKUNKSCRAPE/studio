# main.py — Enhanced CLI Orchestrator for SkunkScrape
import argparse
import logging
import subprocess
import json
from pathlib import Path
import tempfile

LOG_DIR = Path("data/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=str(LOG_DIR / "main.log"),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
log = logging.getLogger("main")

PROJECT_ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = PROJECT_ROOT / "plugins" / "manifest.json"
PROXIES_JSON = PROJECT_ROOT / "data" / "proxies" / "proxies.json"

# -----------------------
# Helpers
# -----------------------
def load_manifest():
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Missing manifest.json at {MANIFEST_PATH}")
    with MANIFEST_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

def list_plugins(manifest):
    plugins = {}
    for cat, info in manifest["categories"].items():
        for p in info["plugins"]:
            plugins[p] = p
    return plugins

def load_proxies():
    if not PROXIES_JSON.exists():
        return []
    with PROXIES_JSON.open("r", encoding="utf-8") as f:
        return json.load(f)

def select_proxy(selection):
    """selection can be int (index) or host:port string"""
    proxies = load_proxies()
    if not proxies:
        return None

    if selection is None:
        return proxies[0]  # default first proxy

    # If numeric index
    if selection.isdigit():
        idx = int(selection)
        if 0 <= idx < len(proxies):
            return proxies[idx]
        return None

    # If host:port string
    for p in proxies:
        if f"{p['host']}:{p['port']}" == selection:
            return p
    return None

def write_proxy_file(proxy):
    if not proxy:
        return None
    tmp_path = Path(tempfile.gettempdir()) / "selected_proxy.txt"
    with tmp_path.open("w", encoding="utf-8") as f:
        f.write(f"{proxy['host']}:{proxy['port']}:{proxy['username']}:{proxy['password']}")
    return str(tmp_path)

# -----------------------
# Runner
# -----------------------
def run_plugin(plugin, url=None, depth=None, to_webhook=False, target_leads=None, proxy_selection=None):
    name = plugin
    cmd = ["python", "-m", f"skunkscrape.plugins.{name}"]

    if url:
        if name == "smart_contact_crawler":
            cmd += ["--url", url]
        else:
            cmd += ["--url", url, "--category", url, "--search", url]
    if name == "smart_contact_crawler" and depth:
        cmd += ["--depth", str(depth)]
    if to_webhook:
        cmd += ["--to-webhook"]
    if target_leads:
        cmd += ["--target-leads", str(target_leads)]

    # Proxy selection
    proxy = select_proxy(proxy_selection)
    proxy_file = write_proxy_file(proxy)
    if proxy_file:
        cmd += ["--proxy-file", proxy_file]

    print(f"\n🚀 Running {plugin} with proxy {proxy['host']}:{proxy['port']}...")
    log.info(f"Launching {plugin}: {cmd}")

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        log.error(f"Error running {plugin}: {e}")
        print(f"❌ Error running {plugin} — see logs/main.log")

# -----------------------
# CLI
# -----------------------
def main():
    manifest = load_manifest()
    plugins = list_plugins(manifest)

    parser = argparse.ArgumentParser(description="SkunkScrape CLI Orchestrator")
    parser.add_argument("--plugin", help="Run plugin (e.g., gumtree_scraper)")
    parser.add_argument("--category", help="Run all plugins in a category")
    parser.add_argument("--all", action="store_true", help="Run all plugins")
    parser.add_argument("--url", help="Start URL (if plugin requires)")
    parser.add_argument("--depth", type=int, help="Depth for smart crawler")
    parser.add_argument("--to-webhook", action="store_true", help="Push to webhook")
    parser.add_argument("--target-leads", type=int, help="Desired number of leads")
    parser.add_argument("--proxy", help="Select proxy (index or host:port from proxies.json)")
    parser.add_argument("--list-proxies", action="store_true", help="List available proxies")
    args = parser.parse_args()

    if args.list_proxies:
        proxies = load_proxies()
        for i, p in enumerate(proxies):
            print(f"[{i}] {p['host']}:{p['port']} ({p['username']})")
        return

    if args.all:
        for p in plugins:
            run_plugin(p, url=args.url, depth=args.depth,
                       to_webhook=args.to_webhook, target_leads=args.target_leads,
                       proxy_selection=args.proxy)
    elif args.category:
        if args.category not in manifest["categories"]:
            print(f"❌ Unknown category: {args.category}")
            return
        for p in manifest["categories"][args.category]["plugins"]:
            run_plugin(p, url=args.url, depth=args.depth,
                       to_webhook=args.to_webhook, target_leads=args.target_leads,
                       proxy_selection=args.proxy)
    elif args.plugin:
        if args.plugin not in plugins:
            print(f"❌ Unknown plugin: {args.plugin}")
            print("👉 Available plugins:", ", ".join(sorted(plugins)))
            return
        run_plugin(args.plugin, url=args.url, depth=args.depth,
                   to_webhook=args.to_webhook, target_leads=args.target_leads,
                   proxy_selection=args.proxy)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
