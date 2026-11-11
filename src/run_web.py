"""Launch the web edition of the Sign-to-Speech camera prototype (PC & Phone accessible)."""
import os
import sys
import socket
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT / "web"
PORT = 8000


def get_local_ip():
    """Get the local network IP (e.g. 192.168.x.x) for phone access."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def log_message(self, format, *args):
        pass  # quiet output


def main():
    if not (WEB_DIR / "index.html").exists():
        print(f"Error: Could not find {WEB_DIR / 'index.html'}")
        return

    local_ip = get_local_ip()
    local_url = f"http://localhost:{PORT}/"
    phone_url = f"http://{local_ip}:{PORT}/"

    print("\n" + "=" * 65)
    print("      🖐️ SMART GLOVE SIGN-TO-SPEECH - WEB & PHONE EDITION")
    print("=" * 65)
    print(f"  • Computer Browser:  {local_url}")
    print(f"  • Phone (Same Wi-Fi): {phone_url}")
    print("=" * 65)
    print("  • Opening browser on your computer...")
    print("  • To open on your phone: Connect to the same Wi-Fi and open:")
    print(f"    --> {phone_url}")
    print("  • Press Ctrl+C in this terminal to stop.")
    print("=" * 65 + "\n")

    webbrowser.open(local_url)

    # Bind to 0.0.0.0 so phones on the local network can connect
    server = HTTPServer(("0.0.0.0", PORT), CustomHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nWeb server stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
