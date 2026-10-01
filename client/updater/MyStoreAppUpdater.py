import os
import sys
import time
import subprocess
import urllib.request


def is_process_running(pid: int) -> bool:
    """Check whether the main application process is still running."""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}"],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

        return str(pid) in result.stdout

    except Exception:
        return False


def download_file(url: str, destination: str):
    """Download the updated MyStoreApp.exe."""
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "MyStoreApp-Updater/1.0"
        },
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        with open(destination, "wb") as file:

            while True:
                chunk = response.read(1024 * 1024)

                if not chunk:
                    break

                file.write(chunk)


def main():

    # Expected:
    #
    # MyStoreAppUpdater.exe
    #     <main_pid>
    #     <target_exe>
    #     <download_url>
    #
    # Example:
    #
    # MyStoreAppUpdater.exe 1234
    #     "C:\...\MyStoreApp.exe"
    #     "https://.../MyStoreApp.exe"

    if len(sys.argv) != 4:

        print(
            "Usage: MyStoreAppUpdater.exe "
            "<main_pid> <target_exe> <download_url>"
        )

        return 1

    try:
        main_pid = int(sys.argv[1])

    except ValueError:

        print("Invalid process ID.")

        return 1

    target_exe = os.path.abspath(sys.argv[2])

    download_url = sys.argv[3]

    app_dir = os.path.dirname(target_exe)

    # Temporary file used while downloading.
    temp_exe = os.path.join(
        app_dir,
        "MyStoreApp.update.exe"
    )

    # --------------------------------------------------
    # 1. Wait for MyStoreApp.exe to close
    # --------------------------------------------------

    for _ in range(30):

        if not is_process_running(main_pid):

            break

        time.sleep(0.5)

    # --------------------------------------------------
    # 2. Download new EXE
    # --------------------------------------------------

    try:

        if os.path.exists(temp_exe):

            os.remove(temp_exe)

        print("Downloading update...")

        download_file(
            download_url,
            temp_exe
        )

    except Exception as exc:

        print(
            f"Download failed: {exc}"
        )

        try:

            if os.path.exists(temp_exe):

                os.remove(temp_exe)

        except Exception:
            pass

        return 1

    # --------------------------------------------------
    # 3. Replace old EXE
    # --------------------------------------------------

    replaced = False

    for _ in range(20):

        try:

            os.replace(
                temp_exe,
                target_exe
            )

            replaced = True

            break

        except PermissionError:

            time.sleep(0.5)

        except OSError:

            time.sleep(0.5)

    if not replaced:

        print(
            "Could not replace the existing MyStoreApp.exe."
        )

        try:

            if os.path.exists(temp_exe):

                os.remove(temp_exe)

        except Exception:
            pass

        return 1

    # --------------------------------------------------
    # 4. Start updated application
    # --------------------------------------------------

    try:

        subprocess.Popen(
            [target_exe],
            cwd=app_dir,
            close_fds=True,
        )

    except Exception as exc:

        print(
            f"Updated application could not be started: {exc}"
        )

        return 1

    return 0


if __name__ == "__main__":

    sys.exit(main())