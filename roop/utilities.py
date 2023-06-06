import glob
import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Any

import roop.globals
from PIL import Image


def run_ffmpeg(args: List) -> None:
    commands = ['ffmpeg', '-hide_banner', '-hwaccel', 'auto', '-loglevel', roop.globals.log_level]
    commands.extend(args)
    try:
        subprocess.check_output(commands, stderr=subprocess.STDOUT)
    except Exception:
        pass


def detect_fps(source_path: str) -> int:
    command = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate', '-of', 'default=noprint_wrappers=1:nokey=1', source_path]
    output = subprocess.check_output(command).decode().strip()
    try:
        return int(eval(output))
    except Exception:
        pass
    return 30


def extract_frames(target_path: str) -> None:
    temp_directory_path = get_temp_directory_path(target_path)
    run_ffmpeg(['-i', target_path, temp_directory_path + os.sep + '%04d.png'])


def create_video(target_path: str, fps: int) -> None:
    temp_directory_path = get_temp_directory_path(target_path)
    temp_file_path = get_temp_file_path(target_path)
    run_ffmpeg(['-i', temp_directory_path + os.sep + '%04d.png', '-framerate', str(fps), '-c:v', 'libx264', '-crf', '7', '-pix_fmt', 'yuv420p', '-y', temp_file_path])


def restore_audio(target_path: str) -> None:
    run_ffmpeg(['-i', target_path, '-i', get_temp_file_path(target_path), '-c:v', 'copy', '-map', '0:v:0', 'map', '1:a:0', '-y', get_temp_file_path(target_path)])


def get_temp_frames_paths(target_path: str) -> List:
    return glob.glob(get_temp_directory_path(target_path) + os.sep + '*.png')


def get_temp_directory_path(target_path: str) -> str:
    target_directory_path = os.path.dirname(target_path)
    return target_directory_path + os.sep + 'temp'


def get_temp_file_path(target_path: str) -> str:
    return get_temp_directory_path(target_path) + os.sep + 'temp.mp4'


def create_temp(target_path: str) -> None:
    Path(get_temp_directory_path(target_path)).mkdir(exist_ok=True)


def clean_temp(target_path: str, output_path: str) -> None:
    temp_file_path = get_temp_file_path(target_path)
    if os.path.isfile(temp_file_path):
        shutil.move(temp_file_path, output_path)
    if not roop.globals.keep_frames:
        shutil.rmtree(get_temp_directory_path(target_path))


def has_image_extention(image_path: str) -> bool:
    return image_path.lower().endswith(('png', 'jpg', 'jpeg', 'bmp'))


def is_image(path: str) -> bool:
    if os.path.isfile(path):
        try:
            image = Image.open(path)
            image.verify()
            return True
        except Exception:
            pass
    return False


def is_video(path: str) -> bool:
    try:
        run_ffmpeg(['-v', 'error', '-i', path, '-f', 'null', '-'])
        return True
    except subprocess.CalledProcessError:
        pass
    return False
