#!/usr/bin/python3
"""Directory/file to image script, not super practical but a fun project.
Any char outside of the extended ascii range may have some problems.
"""
import os
import sys
import base64
import math
from ast import literal_eval #Json.loads does not support True/False values, eval is a security risk.
from PIL import Image

__author__ = "NotNullified"
__version__ = 1.0
__date__ = "5/17/2025"

script = "test.py"
with open(script, 'r') as f:
    output = f.read()

def make_perfect_square(inp: str) -> str:
    """Ensure inputed string has the length of a perfected square, inserting null chars.

    Args:
        inp (str): Input string to make perfect square.

    Returns:
        str: Perfectly square length string.
    """
    n = len(inp)
    next_root = math.isqrt(n) + (0 if math.isqrt(n) ** 2 == n else 1)
    amount_to_next_root = next_root ** 2 - n
    output = inp + chr(0x0) * amount_to_next_root
    return output

def str_to_img(txt: str, out: str='image.png') -> None:
    """Converts a string to an image by reading each char, converting it to an int, and then to a pixel.

    Args:
        txt (str): String input.
        out (str): Image output path.

    Returns:
        None
    """
    length = len(txt)
    sqrt_len = math.isqrt(length)
    
    if not sqrt_len:
        raise ValueError("Length must be perfect square")
    
    width = height = sqrt_len
    
    img = Image.new('L', (width, height))
    
    for x in range(width):
        for y in range(height):
            img.putpixel((x, y), ord(txt[x * width + y]))

    img.save(out)

def img_to_dict(img: str):
    """Read an image file and return encoded dict.

    Args:
        img (str): Path to input image.

    Returns:
        dict: Dictionary with files content'.
    """
    img = Image.open(img)
    pixels = img.load()
    length = img.size[0]
    string = ''

    for x in range(length):
        for y in range(length):
            pixel = pixels[x,y]
            string += (chr(pixel) if pixel != 0 else '')

    return literal_eval(string.replace('\0x00', '')) # Replace function is a hacky fix 

def _read_file(file_path: str) -> dict:
    """Read a file and return a dict with content and binary flag.

    Args:
        file_path (str): Path to a file.

    Returns:
        dict: Dictionary with keys 'binary' and 'content'.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return {"binary": False, "content": file.read()}
    except UnicodeDecodeError:
        with open(file_path, 'rb') as file:
            encoded = base64.b64encode(file.read()).decode('ascii')
            return {"binary": True, "content": encoded}

def _write_file(file_path: str, file_data: dict) -> None:
    """Write text or binary content to a file.

    Args:
        file_path (str): File path to write to.
        file_data (dict): Dictionary with 'binary' and 'content' keys.
    """
    if file_data["binary"]:
        binary_data = base64.b64decode(file_data["content"])
        with open(file_path, 'wb') as file:
            file.write(binary_data)
    else:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(file_data["content"])

def dict_to_path(structure: dict, base_path: str) -> None:
    """Recreate files and directories from a nested dictionary structure.

    Args:
        structure (dict): Dictionary created from `path_to_dict`.
        base_path (str): Root path to recreate the files/directories in.
    """
    for name, content in structure.items():
        full_path = os.path.join(base_path, name)

        if isinstance(content, dict) and "binary" in content and "content" in content:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            _write_file(full_path, content)
        else:
            os.makedirs(full_path, exist_ok=True)
            dict_to_path(content, full_path)

def path_to_dict(path: str) -> dict:
    """Convert a file or directory (including hidden and binary files) into a nested dictionary.

    Args:
        path (str): Path to a file or directory.

    Returns:
        dict: A nested dictionary representing the structure and file contents.
    """
    if os.path.isfile(path):
        return {os.path.basename(path): _read_file(path)}

    structure = {}
    for entry in os.listdir(path):
        entry_path = os.path.join(path, entry)
        if os.path.isdir(entry_path):
            structure[entry] = path_to_dict(entry_path)
        elif os.path.isfile(entry_path):
            structure[entry] = _read_file(entry_path)

    return {os.path.basename(os.path.normpath(path)): structure}

if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] == '--help':
        print("""-r <file path> (Make an image)
-w <img dir> <output dir> (Write image)
--help (Print this)""")
    elif sys.argv[1] == '-r':
        dict_obj = path_to_dict(sys.argv[2])
        str_to_img(make_perfect_square(str(dict_obj)))
    elif sys.argv[1] == '-w':
        dict_to_path(img_to_dict(sys.argv[2]), sys.argv[3])
    else:
        print("Unknown args, please use --help")
