import subprocess
import time
import re
import urllib.request
import platform
import sys
import os

# Global binary path handler determining if we use system PATH or an explicit downloaded execution binary.
CLOUDFLARED_BIN = "cloudflared"

def install_cloudflared():
    """Installs cloudflared natively based on the OS if it doesn't already exist."""
    global CLOUDFLARED_BIN
    
    try:
        # Check if cloudflared is already installed functionally and reachable in PATH
        subprocess.run([CLOUDFLARED_BIN, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print("✅ cloudflared is already installed and accessible in the system PATH.")
        return
    except (FileNotFoundError, OSError):
        print("⚠️ cloudflared not found in PATH. Initiating OS-specific installation...")

    current_os = platform.system()
    
    if current_os == "Linux":
        print("🔄 Installing cloudflared for Linux (AMD64)...")
        # Download the DEB package quietly
        subprocess.run(
            ["wget", "-q", "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb"],
            check=True
        )
        try:
            subprocess.run(["sudo", "dpkg", "-i", "cloudflared-linux-amd64.deb"], check=True)
        except subprocess.CalledProcessError:
            print("❌ Failed to install with sudo. Attempting direct installation (requires root)...")
            subprocess.run(["dpkg", "-i", "cloudflared-linux-amd64.deb"], check=True)
            
    elif current_os == "Darwin":  # macOS
        print("🔄 Installing cloudflared for macOS using Homebrew...")
        try:
            subprocess.run(["brew", "install", "cloudflared"], check=True)
        except FileNotFoundError:
            print("❌ Homebrew is not installed. Please install 'brew' or manually download cloudflared.")
            sys.exit(1)
            
    elif current_os == "Windows":
        print("🔄 Downloading cloudflared.exe for Windows...")
        exe_path = os.path.abspath("cloudflared.exe")
        CLOUDFLARED_BIN = exe_path # Use the explicit local EXE path moving forward
        if not os.path.exists(exe_path):
            try:
                urllib.request.urlretrieve(
                    "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe", 
                    exe_path
                )
                print("✅ Successfully downloaded cloudflared.exe locally.")
            except Exception as e:
                print(f"❌ Failed to download Windows binary: {e}")
                sys.exit(1)
    else:
        print(f"❌ Unsupported OS: {current_os}. Please manually install cloudflared.")
        sys.exit(1)

def kill_processes():
    """Terminates existing background instances of streamlit or cloudflared to avoid port conflicts."""
    print("🧹 Cleaning up old stray processes...")
    
    if platform.system() == "Windows":
        # Windows native WMI and TaskKill procedures for ghost processes
        # Quiet subprocess blocks prevent noisy console dumping
        subprocess.run(['wmic', 'process', 'where', 'commandline like "%streamlit run%"', 'call', 'terminate'], capture_output=True)
        subprocess.run(['taskkill', '/F', '/IM', 'cloudflared.exe'], capture_output=True)
    else:
        # Unix/Linux POSIX standard kills
        subprocess.run(["pkill", "-f", "streamlit"], capture_output=True)
        subprocess.run(["pkill", "-f", "cloudflared"], capture_output=True)
        
    time.sleep(2)

def start_streamlit():
    """Starts the streamlit app in headless mode as a detached background process."""
    print("🚀 Starting Streamlit backend on port 8501...")
    
    streamlit_cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port=8501",
        "--server.headless=true",
        "--server.address=0.0.0.0"
    ]
    
    subprocess.Popen(
        streamlit_cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    print("⏳ Waiting to verify Streamlit execution footprint...")
    time.sleep(8)
    
    try:
        urllib.request.urlopen("http://localhost:8501", timeout=10)
        print("✅ Streamlit is actively bound on local port 8501.")
    except Exception as e:
        print(f"⚠️ Warning during verification: HTTP socket unavailable ({e}) - continuing anyway...")

def start_tunnel():
    """Deploys the Cloudflare explicit tunnel targeting streamlit's localhost socket."""
    print("🌐 Initiating Cloudflare Tunnel mapping...")
    
    tunnel = subprocess.Popen(
        [CLOUDFLARED_BIN, "tunnel", "--url", "http://localhost:8501"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    print("📡 Waiting for TryCloudflare Public Webhook URL...")
    
    public_url = None
    if tunnel.stdout is not None:
        for line in tunnel.stdout:
            text = line.strip()
            
            match = re.search(r"https://[\w-]+\.trycloudflare\.com", text)
            if match:
                public_url = match.group(0)
                print("="*60)
                print(f"✅ APP IS EXTERNALLY LIVE AT: {public_url}")
                print("="*60)
                print("⚠️ NOTE: Keep this terminal execution running to keep the tunnel alive.")
                break
                
    if not public_url:
        print("❌ Tunnel failed to propagate a valid URL hook. Please terminate and attempt re-run.")
        
    try:
        tunnel.wait() # Indefinitely lock script execution natively mapping tunnel runtime.
    except KeyboardInterrupt:
        print("\n🛑 Terminating tunnel execution gracefully...")
        tunnel.terminate()
        kill_processes()
        print("✅ Exited.")

if __name__ == "__main__":
    print(f"--- ZeroDay Armor Tunnel Utility ({platform.system()}) ---")
    install_cloudflared()
    kill_processes()
    start_streamlit()
    start_tunnel()
