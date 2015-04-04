import os


def path_config(storage_path):
    orphaned_path = storage_path + "\\orphaned"
    json_path = os.path.join(storage_path, "meta.json")

    return storage_path, orphaned_path, json_path


def ensure_dir(directories):
    for d in directories:
        if not os.path.exists(d):
            os.mkdir(d)

