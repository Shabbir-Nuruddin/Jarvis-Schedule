"""
Shabbir's 30-Day Gauntlet - Desktop App
Run: py -3.11 app.py
"""

import sys, os, json, subprocess

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import webview
except ImportError:
    print("Installing pywebview...")
    install("pywebview")
    import webview

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(BASE_DIR, "shabbir_30day_gauntlet.html")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

if not os.path.exists(HTML_FILE):
    print(f"ERROR: Cannot find shabbir_30day_gauntlet.html in {BASE_DIR}")
    input("Press Enter to exit...")
    sys.exit(1)

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_config(data):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Config save error: {e}")

class Api:
    """Exposed to JavaScript so the app can read/write config."""
    
    def save_key(self, key):
        cfg = load_config()
        cfg["geminiKey"] = key.strip()
        save_config(cfg)
        print(f"[App] API key saved: {key[:8]}...")
        return True
    
    def load_key(self):
        cfg = load_config()
        key = cfg.get("geminiKey", "")
        if key:
            print(f"[App] API key loaded: {key[:8]}...")
        return key
    
    def save_data(self, data_json):
        """Save all app state to config.json"""
        try:
            cfg = load_config()
            cfg["appState"] = json.loads(data_json)
            save_config(cfg)
            return True
        except Exception as e:
            print(f"[App] Save error: {e}")
            return False
    
    def load_data(self):
        """Load app state from config.json"""
        try:
            cfg = load_config()
            state = cfg.get("appState", {})
            # Always restore the key into state
            if cfg.get("geminiKey"):
                state["geminiKey"] = cfg["geminiKey"]
            return json.dumps(state)
        except Exception as e:
            print(f"[App] Load error: {e}")
            return "{}"


api = Api()

def on_loaded():
    """Called when the page finishes loading - inject saved data."""
    cfg = load_config()
    key = cfg.get("geminiKey", "")
    state = cfg.get("appState", {})
    if key:
        state["geminiKey"] = key
    
    if state:
        state_json = json.dumps(state).replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
        script = f"""
        try {{
            const savedState = JSON.parse(`{state_json}`);
            if(savedState && Object.keys(savedState).length > 0) {{
                S = {{...S, ...savedState}};
                saveS();
                renderSchedule();
                updateSidebar();
                console.log('[App] State restored, key:', savedState.geminiKey ? savedState.geminiKey.slice(0,8)+'...' : 'none');
            }}
        }} catch(e) {{
            console.error('[App] State restore error:', e);
        }}
        """
        try:
            window.evaluate_js(script)
        except Exception as e:
            print(f"[App] JS inject error: {e}")

window = webview.create_window(
    title="Shabbir's 30-Day Gauntlet",
    url="file:///" + HTML_FILE.replace(os.sep, "/"),
    width=1280,
    height=850,
    min_size=(900, 600),
    background_color="#0a0a0a",
    js_api=api,
)

webview.start(on_loaded, debug=False)