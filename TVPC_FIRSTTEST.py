import os, threading, time, random, importlib.util, subprocess, sys, platform, shutil
from guizero import App, PushButton, Text

# ------------------------
# Dependency checks
# ------------------------
def install_python_package(pkg):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

for pkg in ["guizero", "python-vlc"]:
    if importlib.util.find_spec(pkg) is None:
        install_python_package(pkg)

import vlc

# ------------------------
# Settings
# ------------------------
VIDEO_FOLDER = "videos"  # <-- change
SHUFFLE = False
LOOP_FOREVER = True

# ------------------------
# VLC Setup
# ------------------------
instance = vlc.Instance()
player = instance.media_player_new()
current_playlist = []
current_index = 0
is_playing = False

# ------------------------
# Playback functions
# ------------------------
def get_video_list(folder):
    supported_exts = (".mp4", ".mkv", ".avi", ".mov")
    files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(supported_exts)]
    if SHUFFLE:
        random.shuffle(files)
    else:
        files.sort()
    return files

def play_video(index):
    global current_index, is_playing
    if 0 <= index < len(current_playlist):
        current_index = index
        video_path = current_playlist[current_index]
        media = instance.media_new(video_path)
        player.set_media(media)
        player.play()
        now_playing.value = f"Now Playing:\n{os.path.basename(video_path)}"
        is_playing = True

def play_next():
    global current_index
    current_index += 1
    if current_index >= len(current_playlist):
        if LOOP_FOREVER:
            current_index = 0
        else:
            return
    play_video(current_index)

def monitor_playback():
    while True:
        if is_playing and player.get_state() == vlc.State.Ended:
            play_next()
        time.sleep(0.5)

def start_playback():
    if current_playlist:
        threading.Thread(target=monitor_playback, daemon=True).start()
        play_video(0)

def pause_resume():
    if player.is_playing():
        player.pause()
        play_pause_button.text = "▶ Resume"
    else:
        player.play()
        play_pause_button.text = "⏸ Pause"

def toggle_fullscreen():
    player.toggle_fullscreen()

# ------------------------
# GUI Controls Window
# ------------------------
control_app = App("Controls", width=300, height=150)

now_playing = Text(control_app, text="No video playing", size=12)
play_pause_button = PushButton(control_app, text="⏸ Pause", command=pause_resume)
skip_button = PushButton(control_app, text="⏭ Skip", command=play_next)
fullscreen_button = PushButton(control_app, text="⛶ Fullscreen", command=toggle_fullscreen)

# ------------------------
# Load playlist and start
# ------------------------
current_playlist = get_video_list(VIDEO_FOLDER)
if current_playlist:
    start_playback()
else:
    now_playing.value = "No videos found in folder."

control_app.display()
