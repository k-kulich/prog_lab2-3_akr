import os
import stat
import time

FILE_NAME = "task1_sample.txt"
FILE_CONTENT = "Привет! Это тестовые данные для задания 1.\nВторая строка.\n"


def get_script_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def ensure_script_dir() -> str:
    """Если скрипт запущен не из своей папки — перейти в неё."""
    script_dir = get_script_dir()
    if os.path.abspath(os.getcwd()) != script_dir:
        os.chdir(script_dir)
    return os.getcwd()


def create_file(file_name: str, content: str) -> str:
    """Создает файл и записывает в него данные. Возвращает абсолютный путь."""
    path = os.path.abspath(file_name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def file_exists(file_name: str) -> bool:
    return os.path.exists(os.path.abspath(file_name))


def file_info(file_name: str) -> dict:
    path = os.path.abspath(file_name)
    if not os.path.exists(path):
        return {"exists": False}
    st = os.stat(path)
    return {
        "exists": True,
        "path": path,
        "size": st.st_size,
        "mtime": time.ctime(st.st_mtime),
        "atime": time.ctime(st.st_atime),
        "mode_octal": oct(st.st_mode & 0o777),
        "mode_str": stat.filemode(st.st_mode),
    }


def current_user() -> str:
    try:
        return os.getlogin()
    except OSError:
        import getpass
        return getpass.getuser()


def change_permissions(file_name: str, mode: int) -> str:
    path = os.path.abspath(file_name)
    os.chmod(path, mode)
    return oct(os.stat(path).st_mode & 0o777)


def main():
    print(f"Текущая директория до: {os.getcwd()}")
    print(f"Директория скрипта:    {get_script_dir()}")
    print(f"Текущая директория после: {ensure_script_dir()}\n")

    path = create_file(FILE_NAME, FILE_CONTENT)
    print(f"Создан файл: {path}")
    print(f"Файл существует: {file_exists(FILE_NAME)}\n")

    info = file_info(FILE_NAME)
    print(f"Размер:               {info['size']} байт")
    print(f"Последнее изменение:  {info['mtime']}")
    print(f"Последний доступ:     {info['atime']}")
    print(f"Права (октально):     {info['mode_octal']}")
    print(f"Права (символьно):    {info['mode_str']}\n")

    print(f"Текущий пользователь: {current_user()}\n")

    new_mode = 0o640
    updated = change_permissions(FILE_NAME, new_mode)
    print(f"Новые права:          {updated}")


if __name__ == "__main__":
    main()