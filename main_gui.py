import sys, os, json, subprocess, yaml
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from PIL import Image, ImageTk

# Resolve paths dynamically
PROJECT_ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = PROJECT_ROOT / "plugins" / "manifest.json"
CRAWLER_CFG = PROJECT_ROOT / "config" / "crawler.yaml"
PROXIES_JSON = PROJECT_ROOT / "data" / "proxies" / "proxies.json"
BANNER_PATH = str(PROJECT_ROOT / "assets" / "banner.png")
ICON_PATH = str(PROJECT_ROOT / "assets" / "favicon.ico")

def load_manifest():
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Missing manifest.json at {MANIFEST_PATH}")
    with MANIFEST_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

def load_proxies():
    if not PROXIES_JSON.exists():
        return []
    with PROXIES_JSON.open("r", encoding="utf-8") as f:
        proxies = json.load(f)
        # Display host:port for selection
        return [f"{p['host']}:{p['port']} ({p['username']})" for p in proxies]

def get_proxy_by_display(display_value):
    with PROXIES_JSON.open("r", encoding="utf-8") as f:
        proxies = json.load(f)
    for p in proxies:
        if f"{p['host']}:{p['port']} ({p['username']})" == display_value:
            return p
    return None

class SkunkScrapeGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🦨 SkunkScrape Launcher")
        if os.path.exists(ICON_PATH):
            self.iconbitmap(default=ICON_PATH)
        self.geometry("650x520")
        self.minsize(600, 420)
        self.configure(padx=15, pady=15)

        self.manifest = load_manifest()

        # Menu bar
        menu = tk.Menu(self)
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Exit", command=self.quit)
        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu.add_cascade(label="File", menu=file_menu)
        menu.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menu)

        # Banner
        if os.path.exists(BANNER_PATH):
            banner_image = Image.open(BANNER_PATH).resize((550, 80), Image.LANCZOS)
            self.banner_photo = ImageTk.PhotoImage(banner_image)
            ttk.Label(self, image=self.banner_photo).pack(pady=(0, 15))

        # Category + Plugin selection
        ttk.Label(self, text="Select a Category:").pack(anchor="w")
        self.category_var = tk.StringVar()
        self.category_menu = ttk.Combobox(
            self, textvariable=self.category_var,
            values=list(self.manifest["categories"].keys()),
            state="readonly"
        )
        self.category_menu.pack(fill="x")
        self.category_menu.bind("<<ComboboxSelected>>", self.update_plugins)

        ttk.Label(self, text="Select a Plugin:").pack(anchor="w", pady=(10,0))
        self.plugin_var = tk.StringVar()
        self.plugin_menu = ttk.Combobox(self, textvariable=self.plugin_var, values=[], state="readonly")
        self.plugin_menu.pack(fill="x")

        # URL + Depth
        self.url_var = tk.StringVar()
        ttk.Label(self, text="Start URL (optional):").pack(anchor="w", pady=(10,0))
        ttk.Entry(self, textvariable=self.url_var).pack(fill="x")

        self.depth_var = tk.IntVar(value=2)
        ttk.Label(self, text="Crawl Depth (crawler only):").pack(anchor="w", pady=(10,0))
        ttk.Spinbox(self, from_=1, to=5, textvariable=self.depth_var).pack(fill="x")

        # Proxy selector
        ttk.Label(self, text="Select Proxy:").pack(anchor="w", pady=(10,0))
        self.proxy_var = tk.StringVar()
        proxy_list = load_proxies()
        self.proxy_menu = ttk.Combobox(self, textvariable=self.proxy_var, values=proxy_list, state="readonly")
        self.proxy_menu.pack(fill="x")
        if proxy_list:
            self.proxy_var.set(proxy_list[0])

        self.webhook_var = tk.BooleanVar()
        ttk.Checkbutton(self, text="Send to Webhook", variable=self.webhook_var).pack(anchor="w", pady=(10,0))

        ttk.Button(self, text="🚀 Run Plugin", command=self.run_plugin).pack(pady=20)

    def update_plugins(self, event=None):
        cat = self.category_var.get()
        plugins = self.manifest["categories"][cat]["plugins"]
        self.plugin_menu["values"] = plugins
        if plugins:
            self.plugin_var.set(plugins[0])

    def run_plugin(self):
        cat = self.category_var.get()
        plugin = self.plugin_var.get()
        if not cat or not plugin:
            messagebox.showerror("Error", "Please select a category and plugin.")
            return

        url = self.url_var.get().strip()
        depth = self.depth_var.get()
        webhook = self.webhook_var.get()
        selected_proxy = get_proxy_by_display(self.proxy_var.get())

        # Create a temporary proxy file for the selected proxy
        proxy_file = PROJECT_ROOT / "data" / "proxies" / "selected_proxy.txt"
        if selected_proxy:
            with proxy_file.open("w", encoding="utf-8") as f:
                f.write(f"{selected_proxy['host']}:{selected_proxy['port']}:{selected_proxy['username']}:{selected_proxy['password']}")

        if plugin == "bulk_crawler":
            cfg = {}
            if CRAWLER_CFG.exists():
                with CRAWLER_CFG.open("r", encoding="utf-8") as f:
                    cfg = yaml.safe_load(f).get("crawler", {})

            cmd = ["python", "-m", "crawler.crawler"]
            cmd += ["--sources-file", cfg.get("sources_file", str(PROJECT_ROOT / "sources" / "sources.csv"))]
            cmd += ["--depth", str(depth or cfg.get("depth", 2))]
            cmd += ["--proxy-file", str(proxy_file)]
            if cfg.get("timeout"):
                cmd += ["--timeout", str(cfg["timeout"])]
            if cfg.get("retries"):
                cmd += ["--retries", str(cfg["retries"])]
            if webhook or cfg.get("to_webhook"):
                cmd += ["--to-webhook"]
        else:
            plugin_path = PROJECT_ROOT / "plugins" / f"{plugin}.py"
            cmd = ["python", str(plugin_path)]
            if url:
                cmd += ["--url", url]
            if plugin == "smart_contact_crawler":
                cmd += ["--depth", str(depth)]
            if webhook:
                cmd += ["--to-webhook"]
            cmd += ["--proxy-file", str(proxy_file)]

        try:
            subprocess.run(cmd, check=True)
            messagebox.showinfo("Done", f"Plugin '{plugin}' executed successfully.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Plugin failed: {e}")

    def show_about(self):
        messagebox.showinfo("About SkunkScrape",
            "SkunkScrape GUI\nVersion 2.5\n\nDeveloped by Skunkworks (Pty) Ltd\nhttps://www.skunkworks.africa")

if __name__ == "__main__":
    app = SkunkScrapeGUI()
    app.mainloop()
