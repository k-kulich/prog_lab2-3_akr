import os
import platform
import sys
import time

try:
    import psutil
except ImportError: 
    psutil = None


def list_processes():
    """Возвращает список кортежей (pid, name, username) для всех процессов."""
    if psutil is None:
        raise RuntimeError("psutil не установлен")
    result = []
    for proc in psutil.process_iter(["pid", "name", "username"]):
        try:
            info = proc.info
            result.append((info["pid"], info["name"], info["username"]))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return result


def process_details(pid: int) -> dict:
    if psutil is None:
        raise RuntimeError("psutil не установлен")
    try:
        proc = psutil.Process(pid)
        with proc.oneshot():
            return {
                "pid": proc.pid,
                "name": proc.name(),
                "status": proc.status(),
                "username": proc.username(),
                "cpu_percent": proc.cpu_percent(interval=0.0),
                "memory_mb": round(proc.memory_info().rss / (1024 * 1024), 2),
                "create_time": time.ctime(proc.create_time()),
                "cmdline": proc.cmdline(),
            }
    except psutil.NoSuchProcess:
        raise ProcessLookupError(f"Процесс с PID={pid} не найден")
    except psutil.AccessDenied:
        raise PermissionError(f"Нет прав на чтение процесса PID={pid}")


def kill_process(pid: int) -> None:
    if psutil is None:
        raise RuntimeError("psutil не установлен")
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        proc.wait(timeout=3)
    except psutil.NoSuchProcess:
        raise ProcessLookupError(f"Процесс с PID={pid} не найден")
    except psutil.AccessDenied:
        raise PermissionError(f"Нет прав на завершение процесса PID={pid}")
    except psutil.TimeoutExpired:
        proc.kill()


def get_environment() -> dict:
    return dict(os.environ)


def set_environment_variable(name: str, value: str) -> None:
    if not name or "=" in name:
        raise ValueError("Некорректное имя переменной окружения")
    os.environ[name] = value


def unset_environment_variable(name: str) -> bool:
    if name in os.environ:
        del os.environ[name]
        return True
    return False


def set_process_priority(pid: int, priority: str) -> None:
    """priority ∈ {'low', 'normal', 'high'}"""
    if psutil is None:
        raise RuntimeError("psutil не установлен")
    mapping = {
        "low": psutil.BELOW_NORMAL_PRIORITY_CLASS if sys.platform == "win32" else 10,
        "normal": psutil.NORMAL_PRIORITY_CLASS if sys.platform == "win32" else 0,
        "high": psutil.ABOVE_NORMAL_PRIORITY_CLASS if sys.platform == "win32" else -10,
    }
    if priority not in mapping:
        raise ValueError("priority должен быть 'low', 'normal' или 'high'")
    try:
        proc = psutil.Process(pid)
        proc.nice(mapping[priority])
    except psutil.NoSuchProcess:
        raise ProcessLookupError(f"Процесс с PID={pid} не найден")
    except psutil.AccessDenied:
        raise PermissionError(f"Нет прав на изменение приоритета PID={pid}")


def system_info() -> dict:
    info = {
        "os": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python": sys.version.split()[0],
        "cwd": os.getcwd(),
    }
    if psutil is not None:
        info["cpu_count"] = psutil.cpu_count(logical=True)
        info["memory_total_mb"] = round(
            psutil.virtual_memory().total / (1024 * 1024), 2
        )
    return info

MENU = """
===== Системное меню =====
a) Показать список всех процессов
b) Детальная информация о процессе
c) Завершить процесс по PID
d) Показать / добавить переменные окружения
e) Изменить приоритет процесса
f) Показать информацию о системе
g) Выход
Выбор: """


def _show_processes():
    procs = list_processes()
    print(f"Всего процессов: {len(procs)}")
    for pid, name, user in procs[:50]:
        print(f"  PID={pid:<6} {name:<30} user={user}")
    if len(procs) > 50:
        print(f"  ... ещё {len(procs) - 50}")


def _show_process_details():
    try:
        pid = int(input("Введите PID: ").strip())
    except ValueError:
        print("Некорректный PID")
        return
    try:
        details = process_details(pid)
    except (ProcessLookupError, PermissionError) as exc:
        print(f"Ошибка: {exc}")
        return
    for k, v in details.items():
        print(f"  {k}: {v}")


def _kill_process():
    try:
        pid = int(input("Введите PID для завершения: ").strip())
    except ValueError:
        print("Некорректный PID")
        return
    try:
        kill_process(pid)
        print(f"Процесс PID={pid} завершён")
    except (ProcessLookupError, PermissionError) as exc:
        print(f"Ошибка: {exc}")


def _env_menu():
    print("1) Показать переменные окружения")
    print("2) Установить переменную")
    print("3) Удалить переменную")
    action = input("Действие: ").strip()
    if action == "1":
        for k, v in sorted(get_environment().items()):
            print(f"  {k}={v}")
    elif action == "2":
        name = input("Имя: ").strip()
        value = input("Значение: ").strip()
        try:
            set_environment_variable(name, value)
            print(f"Установлено: {name}={value}")
        except ValueError as exc:
            print(f"Ошибка: {exc}")
    elif action == "3":
        name = input("Имя: ").strip()
        print("Удалено" if unset_environment_variable(name) else "Не найдено")


def _priority_menu():
    try:
        pid = int(input("Введите PID: ").strip())
    except ValueError:
        print("Некорректный PID")
        return
    priority = input("Приоритет (low/normal/high): ").strip().lower()
    try:
        set_process_priority(pid, priority)
        print(f"Приоритет процесса PID={pid} изменён на {priority}")
    except (ProcessLookupError, PermissionError, ValueError) as exc:
        print(f"Ошибка: {exc}")


def _system_info():
    for k, v in system_info().items():
        print(f"  {k}: {v}")


def run_menu(input_func=input):
    actions = {
        "a": _show_processes,
        "b": _show_process_details,
        "c": _kill_process,
        "d": _env_menu,
        "e": _priority_menu,
        "f": _system_info,
    }
    while True:
        choice = input_func(MENU).strip().lower()
        if choice == "g":
            print("Выход.")
            return
        action = actions.get(choice)
        if action is None:
            print("Неизвестная опция")
        else:
            try:
                action()
            except Exception as exc:
                print(f"Непредвиденная ошибка: {exc}")


if __name__ == "__main__":
    run_menu()