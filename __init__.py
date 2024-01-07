import pathlib
import sys

def get_project_head(head_dir_name=None):
    if head_dir_name is None:
        raise ValueError("head_dir_name cannot be None.")

    if type(head_dir_name) != str:
        raise ValueError("head_dir_name must be a str.")

    index = -1
    proj_head_path = None
    curr_dir = pathlib.Path.cwd()
    path_parts = curr_dir.parts

    for i in range(0,len(path_parts)):
        if path_parts[i] == head_dir_name:
            index = i

    if index < 0:
        return False, None
    index = index + 1
    proj_head_path = pathlib.Path(path_parts[0])

    for i in range (0,index):
        proj_head_path = proj_head_path / path_parts[i]
        
    return True, proj_head_path



