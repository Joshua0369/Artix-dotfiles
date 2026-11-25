#!/usr/bin/env python3
import os
import sys
import time
import subprocess
from Xlib import X, display
from Xlib.ext import xtest

PIDFILE = "/tmp/python_full_bow.pid"

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
            # release left click on toggle off just in case
            try:
                d_off = display.Display()
                xtest.fake_input(d_off, X.ButtonRelease, X.Button1)
                d_off.sync()
            except Exception:
                pass
            notify("Full Bow", "STOPPED")
            sys.exit(0)
    except (ValueError, OSError):
        pass
    os.remove(PIDFILE)

# 2. Test X11 display connection FIRST
try:
    d = display.Display()
except Exception as e:
    notify("Full Bow Error", f"X11 init failed: {e}")
    sys.exit(1)

# 3. Fork into background daemon
try:
    pid = os.fork()
    if pid > 0:
        notify("Full Bow", "STARTED (1s hold)")
        sys.exit(0)
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
        xtest.fake_input(d, X.ButtonPress, X.Button1)
        d.sync()
        time.sleep(1.0)
        xtest.fake_input(d, X.ButtonRelease, X.Button1)
        d.sync()
except Exception:
    pass
finally:
    try:
        xtest.fake_input(d, X.ButtonRelease, X.Button1)
        d.sync()
    except Exception:
        pass
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)
