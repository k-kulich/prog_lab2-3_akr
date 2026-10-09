import os
import shutil

FILE_NAME = "task1_sample.txt"
COPY_NAME = "task1_sample_copy.txt"
NESTED_DIRS = ["level1", "level1/level2", "level1/level2/level3"]
MOVED_NAME = "moved_sample.txt"
TEMP_FILES = ["generated_a.txt", "generated_b.txt", "generated_c.txt"]
RENAME_SRC = "new_file.txt"
RENAME_DST = "level1/renamed_new_file.txt"
EMPTY_DIR = "empty_dir"


def copy_file(src: str, dst: str) -> str:
    if not os.path.exists(src):
        with open(src, "w", encoding="utf-8") as f:
            f.write("Источник для копирования\n")
    shutil.copy(src, dst)
    return os.path.abspath(dst)


def rename_file(src: str, dst: str) -> str:
    os.rename(src, dst)
    return os.path.abspath(dst)


def make_dirs(paths):
    for p in paths:
        os.makedirs(p, exist_ok=True)


def move_file(src: str, dst: str) -> str:
    shutil.move(src, dst)
    return os.path.abspath(dst)


def create_files(names, content="data"):
    created = []
    for name in names:
        with open(name, "w", encoding="utf-8") as f:
            f.write(content)
        created.append(os.path.abspath(name))
    return created


def list_dir(path=".") -> dict:
    entries = os.listdir(path)
    files = [e for e in entries if os.path.isfile(os.path.join(path, e))]
    dirs = [e for e in entries if os.path.isdir(os.path.join(path, e))]
    return {"files": sorted(files), "dirs": sorted(dirs), "all": sorted(entries)}


def walk_tree(root=".") -> list:
    """Возвращает список словарей {path, files} для каждой директории."""
    result = []
    for dirpath, dirnames, filenames in os.walk(root):
        result.append({"path": dirpath, "files": sorted(filenames)})
    return result


def create_and_remove_empty_dir(path: str) -> bool:
    os.makedirs(path, exist_ok=True)
    os.rmdir(path)
    return not os.path.exists(path)


def main():
    print("=== 1. Копирование файла ===")
    copied = copy_file(FILE_NAME, COPY_NAME)
    print(f"Скопирован: {copied}")

    print("\n=== 2. Создание вложенных директорий и перемещение ===")
    make_dirs(NESTED_DIRS)
    moved = move_file(COPY_NAME, MOVED_NAME)
    target = os.path.join(NESTED_DIRS[-1], MOVED_NAME)
    shutil.move(moved, target)
    print(f"Перемещен в: {os.path.abspath(target)}")

    print("\n=== 3. Новый файл, перемещение и переименование одной командой ===")
    create_files([RENAME_SRC], content="new file content")
    os.renames(RENAME_SRC, RENAME_DST)
    print(f"Перемещен и переименован: {os.path.abspath(RENAME_DST)}")

    print("\n=== 4. Создание файлов и обзор ===")
    create_files(TEMP_FILES)
    print(f"Содержимое '{os.getcwd()}':")
    for k, v in list_dir(".").items():
        print(f"  {k}: {v}")

    print(f"\nСодержимое '{NESTED_DIRS[-1]}':")
    for k, v in list_dir(NESTED_DIRS[-1]).items():
        print(f"  {k}: {v}")

    print("\n=== 5. Возврат, создание/удаление пустой директории ===")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    removed = create_and_remove_empty_dir(EMPTY_DIR)
    print(f"Пустая директория удалена: {removed}")

    print("\n=== 6. Обход дерева ===")
    for entry in walk_tree("."):
        print(f"  {entry['path']}: {entry['files']}")


if __name__ == "__main__":
    main()