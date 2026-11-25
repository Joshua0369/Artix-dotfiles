#!/usr/bin/env python3
import os
import sys
import time
import subprocess
from Xlib import X, display, XK
from Xlib.ext import xtest

PIDFILE = "/tmp/python_spammer.pid"

def notify(title, message):
    try:
        subprocess.run(
            ['notify-send', title, message, '-t', '1000'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass

def is_running(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True

# 1. Toggle logic: if PID file exists and process is active, kill it
if os.path.exists(PIDFILE):
    try:
        with open(PIDFILE, "r") as f:
            pid = int(f.read().strip())
        if is_running(pid):
            os.kill(pid, 15)  # SIGTERM
            os.remove(PIDFILE)
            notify("Key Spammer", "STOPPED")
            sys.exit(0)
    except (ValueError, OSError):
        pass
    os.remove(PIDFILE)

# 2. Test X11 display connection and keysym conversion
try:
    d = display.Display()
    keysym = XK.string_to_keysym('f')
    keycode = d.keysym_to_keycode(keysym)
except Exception as e:
    notify("Key Spammer Error", f"X11 init failed: {e}")
    sys.exit(1)

# 3. Fork into background daemon
try:
    pid = os.fork()
    if pid > 0:
        notify("Key Spammer", "STARTED (F key)")
        sys.exit(0)  # Parent exits immediately after notifying
except OSError as e:
    sys.stderr.write(f"Fork failed: {e}\n")
    sys.exit(1)

# 4. Child process setup
os.setsid()
os.umask(0)

with open(PIDFILE, "w") as f:
    f.write(str(os.getpid()))

try:
    while True:
        xtest.fake_input(d, X.KeyPress, keycode)
        d.sync()
        xtest.fake_input(d, X.KeyRelease, keycode)
        d.sync()
        time.sleep(0.01) # 10ms safe interval (100 CPS)
except Exception:
    pass
finally:
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)
