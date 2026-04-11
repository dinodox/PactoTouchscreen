#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2026 Dino Dox
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.

import os
import sys
import pygame
import threading
import time
from gpiozero import OutputDevice
from evdev import InputDevice, ecodes

# -----------------------------
# ENV
# -----------------------------
os.environ["SDL_VIDEODRIVER"] = "kmsdrm"
os.environ["SDL_AUDIODRIVER"] = "dummy"

# -----------------------------
# SCREEN
# -----------------------------
WIDTH, HEIGHT = 800, 480
ICON_SIZE = 128
TIMEOUT_SECONDS = 120

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()

# -----------------------------
# LAYOUT
# -----------------------------
ROWS, COLS = 3, 4
BASE = os.path.dirname(os.path.abspath(__file__))

icons_paths = [
    ["icons/2player.png","icons/4player.png","icons/twinstick.png","icons/smario.png"],
    ["icons/dpad.png","icons/analogfast.png","icons/analogslow.png","icons/pacman.png"],
    ["icons/turbo.png","icons/8to6.png","icons/dirk.png","icons/kb.png"]
]

PLACEHOLDERS = [(0,3), (1,3), (2,2)]

# -----------------------------
# GPIO CONFIG
# -----------------------------
GPIO_CONFIG = {
    "player": {
        "2p": 17,
        "4p": 22,
        "twinstick": 27
    },
    "control": {
        "dpad": 13,
        "afast": 5,
        "aslow": 6
    },
    "features": {
        "turbo_on": 26,
        "turbo_off": 16,
        "8to6_on": 19,
        "8to6_off": 25,
        "kb": 20,
        "disconnect": 21
    }
}

# -----------------------------
# GPIO INIT
# -----------------------------
GPIO = {}
for cat in GPIO_CONFIG:
    for name, pin in GPIO_CONFIG[cat].items():
        GPIO[name] = OutputDevice(pin, active_high=False, initial_value=True)

group_player = ["2p", "4p", "twinstick"]
group_control = ["dpad", "afast", "aslow"]

# -----------------------------
# HELPERS
# -----------------------------
def set_group(group, active):
    for g in group:
        GPIO[g].off()
    GPIO[active].on()

def pulse(pin, t=0.12):
    GPIO[pin].on()
    time.sleep(t)
    GPIO[pin].off()

def flash(cell):
    pygame.draw.rect(screen, (0,255,0), cell["rect"].inflate(12,12), 0)
    pygame.display.flip()
    time.sleep(0.12)

def reset_to_defaults():
    for p in group_player + group_control:
        GPIO[p].off()

    GPIO["turbo_on"].on()
    GPIO["turbo_off"].off()

    GPIO["8to6_on"].off()
    GPIO["8to6_off"].on()

    GPIO["disconnect"].off()
    GPIO["kb"].off()

    set_group(group_player, "2p")
    set_group(group_control, "afast")

# -----------------------------
# ICON LOAD
# -----------------------------
def load_icon(path):
    if not path:
        return None
    full = os.path.join(BASE, path)
    if not os.path.exists(full):
        return None
    img = pygame.image.load(full)
    img = img.convert_alpha() if img.get_alpha() else img.convert()
    return pygame.transform.scale(img, (ICON_SIZE, ICON_SIZE))

# -----------------------------
# GRID
# -----------------------------
margin_x = (WIDTH - (COLS * ICON_SIZE)) // (COLS + 1)
margin_y = (HEIGHT - (ROWS * ICON_SIZE)) // (ROWS + 1)

grid = []
for r in range(ROWS):
    row = []
    for c in range(COLS):
        img = load_icon(icons_paths[r][c])
        rect = None
        if img:
            rect = img.get_rect()
            rect.x = margin_x + c*(ICON_SIZE+margin_x)
            rect.y = margin_y + r*(ICON_SIZE+margin_y)

        selected = (r,c) in [(0,0),(1,1)]
        row.append({"img":img,"rect":rect,"selected":selected})
    grid.append(row)

# -----------------------------
# INIT
# -----------------------------
time.sleep(1)
reset_to_defaults()

# -----------------------------
# TOUCH
# -----------------------------
touch = {"x":0,"y":0,"press":False}

def touch_thread():
    dev = InputDevice("/dev/input/event0")
    rx = ry = 0
    for e in dev.read_loop():
        if e.type == ecodes.EV_ABS:
            if e.code == ecodes.ABS_X: rx = e.value
            if e.code == ecodes.ABS_Y: ry = e.value
            touch["x"] = int((rx/4095)*WIDTH)
            touch["y"] = int((ry/4095)*HEIGHT)
        elif e.type == ecodes.EV_KEY and e.code == 272 and e.value == 1:
            touch["press"] = True

threading.Thread(target=touch_thread, daemon=True).start()

def deselect_all():
    for r in grid:
        for c in r:
            c["selected"] = False

def deselect_row(r):
    for c in range(COLS):
        grid[r][c]["selected"] = False

# -----------------------------
# MAIN
# -----------------------------
kb_mode = False
disconnect_mode = False
last_activity = time.time()
screen_asleep = False

last_kb = 0
last_dis = 0
DEBOUNCE = 3

running = True
while running:
    now = time.time()

    if not screen_asleep and now - last_activity > TIMEOUT_SECONDS:
        screen_asleep = True

    for e in pygame.event.get():
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            running = False

    if touch["press"]:
        touch["press"] = False
        last_activity = now

        if screen_asleep:
            screen_asleep = False
            continue

        x, y = touch["x"], touch["y"]

        for r in range(ROWS):
            for c in range(COLS):
                cell = grid[r][c]
                if not cell["img"] or (r,c) in PLACEHOLDERS:
                    continue
                if not cell["rect"].collidepoint(x,y):
                    continue

                # KB MODE
                if (r,c) == (2,3):
                    if now - last_kb < DEBOUNCE:
                        break
                    last_kb = now

                    kb_mode = not kb_mode
                    pulse("kb")
                    flash(cell)
                    deselect_all()

                    if kb_mode:
                        cell["selected"] = True
                        GPIO["kb"].on()            # ✅ HOLD KB ACTIVE
                        GPIO["disconnect"].off()
                    else:
                        reset_to_defaults()
                        grid[0][0]["selected"] = True
                        grid[1][1]["selected"] = True
                    break

                if kb_mode:
                    break

                # PLAYER
                if r == 0 and c <= 2:
                    deselect_row(0)
                    cell["selected"] = True
                    set_group(group_player, group_player[c])
                    flash(cell)
                    break

                # CONTROL
                if r == 1 and c <= 2:
                    deselect_row(1)
                    cell["selected"] = True
                    set_group(group_control, group_control[c])
                    flash(cell)
                    break

                # TURBO
                if (r,c) == (2,0):
                    cell["selected"] = not cell["selected"]
                    if cell["selected"]:
                        GPIO["turbo_on"].off()
                        GPIO["turbo_off"].on()
                    else:
                        GPIO["turbo_on"].on()
                        GPIO["turbo_off"].off()
                    flash(cell)
                    break

                # 8TO6
                if (r,c) == (2,1):
                    cell["selected"] = not cell["selected"]
                    if cell["selected"]:
                        GPIO["8to6_on"].on()
                        GPIO["8to6_off"].off()
                    else:
                        GPIO["8to6_on"].off()
                        GPIO["8to6_off"].on()
                    flash(cell)
                    break

    screen.fill((0,0,0))

    if not screen_asleep:
        for r in grid:
            for c in r:
                if c["img"]:
                    if c["selected"]:
                        pygame.draw.rect(screen,(255,0,0),c["rect"].inflate(8,8),4)
                    screen.blit(c["img"],c["rect"])

    pygame.display.flip()
    clock.tick(60)

# CLEANUP
for p in GPIO.values():
    p.close()

pygame.quit()
sys.exit()
# ENV
# -----------------------------
os.environ["SDL_VIDEODRIVER"] = "kmsdrm"
os.environ["SDL_AUDIODRIVER"] = "dummy"

# -----------------------------
# SCREEN
# -----------------------------
WIDTH, HEIGHT = 800, 480
ICON_SIZE = 128
TIMEOUT_SECONDS = 120

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()

# -----------------------------
# LAYOUT
# -----------------------------
ROWS, COLS = 3, 4
BASE = os.path.dirname(os.path.abspath(__file__))

icons_paths = [
    ["icons/2player.png","icons/4player.png","icons/twinstick.png","icons/smario.png"],
    ["icons/dpad.png","icons/analogfast.png","icons/analogslow.png","icons/pacman.png"],
    ["icons/turbo.png","icons/8to6.png","icons/dirk.png","icons/kb.png"]
]

PLACEHOLDERS = [(0,3), (1,3), (2,2)]

# -----------------------------
# GPIO CONFIG (SINGLE SOURCE OF TRUTH)
# -----------------------------
GPIO_CONFIG = {
    "player": {
        "2p": 17,
        "4p": 22,
        "twinstick": 27
    },
    "control": {
        "dpad": 13,
        "afast": 5,
        "aslow": 6
    },
    "features": {
        "turbo_on": 26,
        "turbo_off": 16,
        "8to6_on": 19,
        "8to6_off": 25,
        "kb": 20,
        "disconnect": 21
    }
}

# -----------------------------
# GPIO INIT
# -----------------------------
GPIO = {}

for cat in GPIO_CONFIG:
    for name, pin in GPIO_CONFIG[cat].items():
        GPIO[name] = OutputDevice(pin, active_high=False, initial_value=True)

# groups
group_player = ["2p", "4p", "twinstick"]
group_control = ["dpad", "afast", "aslow"]

# -----------------------------
# HELPERS
# -----------------------------
def set_group(group, active):
    for g in group:
        GPIO[g].off()
    GPIO[active].on()

def pulse(pin, t=0.12):
    GPIO[pin].on()
    time.sleep(t)
    GPIO[pin].off()

def flash(cell):
    pygame.draw.rect(screen, (0,255,0), cell["rect"].inflate(12,12), 0)
    pygame.display.flip()
    time.sleep(0.12)

def reset_to_defaults():
    for p in group_player + group_control:
        GPIO[p].off()

    GPIO["turbo_on"].on()      # OFF at boot
    GPIO["turbo_off"].off()

    GPIO["8to6_on"].off()
    GPIO["8to6_off"].on()

    GPIO["disconnect"].off()
    GPIO["kb"].off()

    set_group(group_player, "2p")
    set_group(group_control, "afast")

# -----------------------------
# ICON LOAD
# -----------------------------
def load_icon(path):
    if not path:
        return None
    full = os.path.join(BASE, path)
    if not os.path.exists(full):
        return None
    img = pygame.image.load(full)
    img = img.convert_alpha() if img.get_alpha() else img.convert()
    return pygame.transform.scale(img, (ICON_SIZE, ICON_SIZE))

# -----------------------------
# GRID
# -----------------------------
margin_x = (WIDTH - (COLS * ICON_SIZE)) // (COLS + 1)
margin_y = (HEIGHT - (ROWS * ICON_SIZE)) // (ROWS + 1)

grid = []
for r in range(ROWS):
    row = []
    for c in range(COLS):
        img = load_icon(icons_paths[r][c])
        rect = None
        if img:
            rect = img.get_rect()
            rect.x = margin_x + c*(ICON_SIZE+margin_x)
            rect.y = margin_y + r*(ICON_SIZE+margin_y)

        selected = (r,c) in [(0,0),(1,1)]
        row.append({"img":img,"rect":rect,"selected":selected})
    grid.append(row)

# -----------------------------
# APPLY BOOT STATE
# -----------------------------
time.sleep(1)
reset_to_defaults()

# -----------------------------
# TOUCH
# -----------------------------
touch = {"x":0,"y":0,"press":False}

def touch_thread():
    dev = InputDevice("/dev/input/event0")
    rx = ry = 0
    for e in dev.read_loop():
        if e.type == ecodes.EV_ABS:
            if e.code == ecodes.ABS_X: rx = e.value
            if e.code == ecodes.ABS_Y: ry = e.value
            touch["x"] = int((rx/4095)*WIDTH)
            touch["y"] = int((ry/4095)*HEIGHT)
        elif e.type == ecodes.EV_KEY and e.code == 272 and e.value == 1:
            touch["press"] = True

threading.Thread(target=touch_thread, daemon=True).start()

def deselect_all():
    for r in grid:
        for c in r:
            c["selected"] = False

def deselect_row(r):
    for c in range(COLS):
        grid[r][c]["selected"] = False

# -----------------------------
# MAIN STATE
# -----------------------------
kb_mode = False
disconnect_mode = False
last_activity = time.time()
screen_asleep = False

# debounce
last_kb = 0
last_dis = 0
DEBOUNCE = 3

# -----------------------------
# LOOP
# -----------------------------
running = True
while running:
    now = time.time()

    if not screen_asleep and now - last_activity > TIMEOUT_SECONDS:
        screen_asleep = True

    for e in pygame.event.get():
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            running = False

    if touch["press"]:
        touch["press"] = False
        last_activity = now

        if screen_asleep:
            screen_asleep = False
            continue

        x, y = touch["x"], touch["y"]

        for r in range(ROWS):
            for c in range(COLS):
                cell = grid[r][c]
                if not cell["img"] or (r,c) in PLACEHOLDERS:
                    continue
                if not cell["rect"].collidepoint(x,y):
                    continue

                # ---------------- KB ----------------
                if (r,c) == (2,3):
                    if now - last_kb < DEBOUNCE:
                        break
                    last_kb = now

                    kb_mode = not kb_mode
                    pulse("kb")
                    flash(cell)
                    deselect_all()

                    if kb_mode:
                        cell["selected"] = True
                        GPIO["disconnect"].off()
                    else:
                        reset_to_defaults()
                        grid[0][0]["selected"] = True
                        grid[1][1]["selected"] = True
                    break

                if kb_mode:
                    break

                # ---------------- DISCONNECT ----------------
                if (r,c) == (2,2):
                    if now - last_dis < DEBOUNCE:
                        break
                    last_dis = now

                    disconnect_mode = not disconnect_mode
                    pulse("disconnect")
                    flash(cell)
                    deselect_all()

                    if disconnect_mode:
                        cell["selected"] = True
                        GPIO["kb"].off()
                    else:
                        reset_to_defaults()
                        grid[0][0]["selected"] = True
                        grid[1][1]["selected"] = True
                    break

                if disconnect_mode:
                    break

                # ---------------- PLAYER ----------------
                if r == 0 and c <= 2:
                    deselect_row(0)
                    cell["selected"] = True
                    set_group(group_player,
                              group_player[c])
                    flash(cell)
                    break

                # ---------------- CONTROL ----------------
                if r == 1 and c <= 2:
                    deselect_row(1)
                    cell["selected"] = True
                    set_group(group_control,
                              group_control[c])
                    flash(cell)
                    break

                # ---------------- TURBO ----------------
                if (r,c) == (2,0):
                    cell["selected"] = not cell["selected"]
                    if cell["selected"]:
                        GPIO["turbo_on"].off()
                        GPIO["turbo_off"].on()
                    else:
                        GPIO["turbo_on"].on()
                        GPIO["turbo_off"].off()
                    flash(cell)
                    break

                # ---------------- 8TO6 ----------------
                if (r,c) == (2,1):
                    cell["selected"] = not cell["selected"]
                    GPIO["8to6_on"].on() if cell["selected"] else GPIO["8to6_on"].off()
                    GPIO["8to6_off"].off() if cell["selected"] else GPIO["8to6_off"].on()
                    flash(cell)
                    break

    # ---------------- DRAW ----------------
    screen.fill((0,0,0))
    if not screen_asleep:
        for r in grid:
            for c in r:
                if c["img"]:
                    if c["selected"]:
                        pygame.draw.rect(screen,(255,0,0),c["rect"].inflate(8,8),4)
                    screen.blit(c["img"],c["rect"])

    pygame.display.flip()
    clock.tick(60)

# ---------------- CLEANUP ----------------
for p in GPIO.values():
    p.close()

pygame.quit()
sys.exit()
