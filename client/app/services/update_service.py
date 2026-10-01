import os
import sys
import subprocess
from pathlib import Path
from urllib.parse import urlencode

import requests

from app.utils.version import APP_VERSION


VERSION_URL = (
    "https://my-scroll-videos-2026.s3.amazonaws.com/exe/version.json"
)


class UpdateService:
    """Checks S3 for a newer MyStoreApp version and starts the updater."""

    def __init__(self):
        self.version_url = VERSION_URL

    @staticmethod
    def _version_tuple(version):
        try:
            parts = str(version).strip().lstrip("v").split(".")
            return tuple(int(part) for part in parts)
        except (ValueError, AttributeError):
            return (0,)

    def check_for_update(self):
        """
        Return:
            None if there is no update or the check fails.
            dict with version/download_url if an update is available.
        """
        try:
            # Cache-busting query parameter so a newly uploaded version.json
            # is not served from a browser/proxy cache.
            url = self.version_url + "?" + urlencode(
                {"t": str(int(__import__("time").time()))}
            )

            response = requests.get(
                url,
                timeout=5,
                headers={"Cache-Control": "no-cache"},
            )
            response.raise_for_status()

            data = response.json()

            latest_version = str(data.get("version", "")).strip()
            download_url = str(data.get("download_url", "")).strip()

            if not latest_version or not download_url:
                return None

            if self._version_tuple(latest_version) <= self._version_tuple(
                APP_VERSION
            ):
                return None

            return {
                "current_version": APP_VERSION,
                "latest_version": latest_version,
                "download_url": download_url,
            }

        except Exception as exc:
            print(f"Update check failed: {exc}")
            return None

    @staticmethod
    def get_updater_path():
        """
        In a PyInstaller build, updater.exe must be beside MyStoreApp.exe.
        """
        if getattr(sys, "frozen", False):
            app_dir = Path(sys.executable).resolve().parent
        else:
            # Development mode: updater is expected beside a manually tested
            # executable in dist/MyStoreApp.
            app_dir = Path(__file__).resolve().parents[2] / "dist" / "MyStoreApp"

        return app_dir / "MyStoreAppUpdater.exe"

    @staticmethod
    def get_application_path():
        if getattr(sys, "frozen", False):
            return Path(sys.executable).resolve()

        # In development mode this is only used for diagnostics.
        return Path(sys.executable).resolve()

    def start_update(self, download_url):
        """
        Start the updater and return True if it was launched.
        The updater waits for this application to close, downloads the new EXE,
        replaces it, and starts it again.
        """
        updater_path = self.get_updater_path()
        application_path = self.get_application_path()

        if not updater_path.exists():
            raise FileNotFoundError(
                f"MyStoreAppUpdater.exe was not found:\n{updater_path}"
            )

        if not getattr(sys, "frozen", False):
            raise RuntimeError(
                "Run the packaged MyStoreApp.exe to test the updater."
            )

        subprocess.Popen(
            [
                str(updater_path),
                str(os.getpid()),
                str(application_path),
                download_url,
            ],
            cwd=str(updater_path.parent),
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )

        return True
