# Notes & Configuration

* Logos live under `assets/logos/`.
* GitHub Actions will automatically build a Windows executable via PyInstaller when you push to `main`.
* The resulting `.exe` can be found in the workflow’s **Artifacts** after a successful run.
* The `.iss` installer script (in `installer/`) can be used with Inno Setup to make an installer manually if desired.
