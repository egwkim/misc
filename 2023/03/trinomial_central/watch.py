import ast
import os
import platform
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Callable

from manim.utils import module_ops


def clear():
    """Clear output."""
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


def proc_callback(proc: subprocess.Popen, func: Callable):
    """Execute function when the process exits successfully.

    Args:
        proc (subprocess.Popen)

        func (Callable)

    Returns:
        (Any | Literal[False]):
        Returns the return of the function.
        If the process returns an error code, return False.
    """
    if proc.wait() == 0:
        return func()
    return False


def input_new_line(proc: subprocess.Popen, interval: float = 1):
    """Create a thread that inputs a new line to the process.

    Args:
        proc (subprocess.Popen): Process to input new line.

        interval (float, optional): Input interval in seconds. Should be equal to or greater than 1. Defaults to 1.
    """
    while proc.poll() == None:
        os.write(proc.stdin.fileno(), b"\n")
        time.sleep(interval)


def watch(file, command, interval: float = 1, on_exit: Callable | None = None):
    prev_stamp = 0
    stamp = os.stat(file).st_mtime
    p = None

    while True:
        # If the file is updated, create a subprocess
        # If one exists, kill it and create a new one
        if prev_stamp != stamp:
            prev_stamp = stamp
            clear()
            if p != None and p.poll() == None:
                p.terminate()
                p.wait()
            p = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE)

            # Print message after slide is generated
            threading.Thread(target=proc_callback, args=(p, on_exit)).start()
            # Input new line to avoid getting stuck
            threading.Thread(target=input_new_line, args=(p, 1)).start()

        time.sleep(interval)

        # Update stamp to check if the file is modified
        stamp = os.stat(file).st_mtime


def get_scenes_in_file(path):
    module = module_ops.get_module(Path(path))
    scenes = [
        scene.__name__ for scene in module_ops.get_scene_classes_from_module(module)
    ]

    with open(path, "r") as f:
        content = f.read()
        parsed_ast = ast.parse(content)
        scenes_ordered = []
        for n in ast.walk(parsed_ast):
            if isinstance(n, ast.ClassDef) and n.name in scenes:
                scenes_ordered.append(n.name)

    return scenes_ordered


def main():
    file = "slides.py"
    scenes = get_scenes_in_file(file)

    def select_scenes():
        for i, s in enumerate(scenes):
            print(f"{i+1}: {s}")

        while True:
            try:
                selections = [int(i) for i in input("Select scenes: ").split(",")]
                for i in selections:
                    if not (0 < i and i < len(scenes) + 1):
                        raise IndexError(f"Index out of range: {i}")
                selected_scenes = " ".join(scenes[i - 1] for i in selections)
                break
            except (ValueError, IndexError) as e:
                print(e)
        return selected_scenes

    if len(sys.argv) > 1:
        if sys.argv[1] == "-a":
            selected_scenes = " ".join(scenes)
        else:
            selected_scenes = " ".join(sys.argv[1:])
    else:
        selected_scenes = select_scenes()

    title = "미적분을 활용한 확률과 통계 문제 풀이"
    output = "slides.html"
    verbosity = "info"
    quality = "l"
    command = (
        f"manim -q{quality} -v {verbosity} --progress_bar display {file} {selected_scenes} && "
        f"manim-slides convert -ctitle='{title}' {selected_scenes} {output}"
    )

    def success_message():
        print("Slide generation completed!")
        print(f"file://{os.path.abspath(output)}")

    watch("slides.py", command, interval=5, on_exit=success_message)


if __name__ == "__main__":
    main()
