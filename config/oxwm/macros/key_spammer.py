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

# 1. Toggle logic: if PID file exists and process is active, kill it + restore res
if os.path.exists(PIDFILE):
    try:
        with open(PIDFILE, "r") as f:
            pid = int(f.read().strip())
        if is_running(pid):
            os.kill(pid, 15)  # SIGTERM
            os.remove(PIDFILE)

            # --- restore resolution to 1920x1080 ---
            subprocess.run(
                ['xrandr', '--output', 'eDP-1', '--mode', '1920x1080'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

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
        notify("Key Spammer", "STARTED (f spam + cursor bounce)")
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
    # --- ONE-TIME: set resolution to 640x360 on eDP-1 ---
    subprocess.run(
        ['xrandr', '--output', 'eDP-1', '--mode', '640x360'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # --- ONE-TIME: wait 2 seconds ---
    time.sleep(2)

    # --- MAIN LOOP: f spam + alternating cursor bounce ---
    point_a = (297, 146)
    point_b = (344, 146)
    current = point_a

    while True:
        xtest.fake_input(d, X.KeyPress, keycode)
        d.sync()
        xtest.fake_input(d, X.KeyRelease, keycode)
        d.sync()

        xtest.fake_input(d, X.MotionNotify, x=current[0], y=current[1])
        d.sync()

        current = point_b if current == point_a else point_a

        time.sleep(0.01)
except Exception:
    pass
finally:
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)
