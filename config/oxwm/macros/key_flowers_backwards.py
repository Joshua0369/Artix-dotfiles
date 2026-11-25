#!/usr/bin/env python3
import os
import sys
import time
import subprocess
from Xlib import X, display, XK
from Xlib.ext import xtest

PIDFILE = "/tmp/python_macro3.pid"

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

# 1. Toggle logic
if os.path.exists(PIDFILE):
    try:
        with open(PIDFILE, "r") as f:
            pid = int(f.read().strip())
        if is_running(pid):
            os.kill(pid, 15)  # SIGTERM
            os.remove(PIDFILE)

            # --- press w once for 20 ms on toggle-off ---
            try:
                d_off = display.Display()
                kc_w_off = d_off.keysym_to_keycode(XK.string_to_keysym('w'))
                xtest.fake_input(d_off, X.KeyPress, kc_w_off)
                d_off.sync()
                time.sleep(0.020)
                xtest.fake_input(d_off, X.KeyRelease, kc_w_off)
                d_off.sync()
            except Exception:
                pass

            notify("Macro3", "STOPPED")
            sys.exit(0)
    except (ValueError, OSError):
        pass
    os.remove(PIDFILE)

# 2. X11 init + keycodes
try:
    d = display.Display()
    kc_s = d.keysym_to_keycode(XK.string_to_keysym('s'))
except Exception as e:
    notify("Macro3 Error", f"X11 init failed: {e}")
    sys.exit(1)

# 3. Fork into background daemon
try:
    pid = os.fork()
    if pid > 0:
        notify("Macro3", "STARTED")
        sys.exit(0)
except OSError as e:
    sys.stderr.write(f"Fork failed: {e}\n")
    sys.exit(1)

# 4. Child process setup
os.setsid()
os.umask(0)

with open(PIDFILE, "w") as f:
    f.write(str(os.getpid()))

POINT_A = (590, 550)
POINT_B = (777, 550)

def press(keycode, hold_ms):
    xtest.fake_input(d, X.KeyPress, keycode)
    d.sync()
    time.sleep(hold_ms / 1000.0)
    xtest.fake_input(d, X.KeyRelease, keycode)
    d.sync()

def click(hold_ms):
    xtest.fake_input(d, X.ButtonPress, 1)  # left button
    d.sync()
    time.sleep(hold_ms / 1000.0)
    xtest.fake_input(d, X.ButtonRelease, 1)
    d.sync()

def move_to(point):
    xtest.fake_input(d, X.MotionNotify, x=point[0], y=point[1])
    d.sync()

try:
    while True:
        # 1. move cursor to (590, 550)
        move_to(POINT_A)

        # 2. wait 40 ms
        time.sleep(0.040)

        # 3. click 20 ms
        click(20)

        # 4. wait 40 ms
        time.sleep(0.040)

        # 5. move cursor to (777, 550)
        move_to(POINT_B)

        # 6. wait 40 ms
        time.sleep(0.040)

        # 7. click 20 ms
        click(20)

        # 8. wait 40 ms
        time.sleep(0.040)

        # 9. move cursor to (590, 550)
        move_to(POINT_A)

        # 10. wait 40 ms
        time.sleep(0.040)

        # 11. click 20 ms
        click(20)

        # 12. wait 40 ms
        time.sleep(0.040)

        # 13. move cursor to (777, 550)
        move_to(POINT_B)

        # 14. wait 40 ms
        time.sleep(0.040)

        # 15. click 20 ms
        click(20)

        # 16. wait 40 ms
        time.sleep(0.040)

        # 17. hold s for 186 ms
        press(kc_s, 186)

        # 18. wait 100 ms
        time.sleep(0.100)
except Exception:
    pass
finally:
    if os.path.exists(PIDFILE):
        os.remove(PIDFILE)
