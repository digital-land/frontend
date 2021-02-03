#!/usr/bin/env python3
import os


def markdown_files_only(files, file_ext=".md"):
    return [f for f in files if f.endswith(file_ext)]


def get_markdown_files(d):
    if os.path.isdir(d):
        return markdown_files_only(os.listdir(d))
    return None
