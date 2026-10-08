# DVINESOUL DEFENCE

Version 0.2.0 — defensive cybersecurity workbench for Windows and Kali Linux, built with Python 3 and Tkinter.

## Windows: run the standalone application

A Windows build is produced by GitHub Actions. Open the repository's **Actions** tab, select the latest successful **Windows build** run, and download the `DvinesoulDefence-Windows-x64` artifact. Extract the ZIP and run `DvinesoulDefence.exe` from the extracted `DvinesoulDefence` folder. Keep the entire folder together; do not copy only the EXE.

The standalone build bundles the Python runtime, Tkinter UI components, Scapy, and Python-side dependencies. It does not need a separate Python installation on the target PC.

### Windows packet capture requirement

Live packet capture uses Scapy and requires **Npcap** to be installed on the Windows computer: https://npcap.com/

1. Install Npcap from its official website.
2. Restart the application after installation.
3. In **PACKET SNIFFER**, click **REFRESH INTERFACES** and select an interface.
4. If capture still fails, run the app with suitable Windows permissions and check Npcap/interface compatibility.

Npcap is a system-level packet-capture driver and is intentionally not embedded or silently installed by this project. Other tools do not require Npcap. Capture only networks you own or are explicitly authorized to monitor.

### Build on Windows yourself

Install Python 3.12 from https://www.python.org/downloads/windows/ using the official installer and ensure **Tcl/Tk and IDLE** are enabled. Then download/clone this repository and double-click `build_windows.bat`. The script installs the declared build dependencies, runs the core tests, and creates `dist\\DvinesoulDefence\\DvinesoulDefence.exe` plus its support files.

To run from source instead, double-click `run_windows.bat`. That route needs internet access for dependency installation and a compatible Python installation.

## Launch on Kali Linux

```bash
sudo apt update
sudo apt install python3-tk
python3 app/main.py
```

Optional passive packet capture:

```bash
sudo apt install python3-scapy
sudo python3 app/main.py
```

Run as root only when you specifically need packet-capture privileges; ordinary scanning and local auditing should run as your normal user. Scapy capture is optional. The other core functions use Python's standard library.

## Included tools

- TCP port inventory with bounded concurrency and explicit authorization confirmation.
- HTTP directory/path discovery using a supplied wordlist or a small built-in starter list.
- DNS subdomain resolution using a supplied wordlist or a small built-in starter list.
- Threat-surface inventory combining common TCP ports and optional HTTP path checks.
- Optional Scapy passive packet metadata capture with start/stop controls.
- Local system facts and dependency checks, with Windows-compatible username and disk-root reporting.
- Local password-strength heuristic and secure random password generation.
- JSON evidence export.

## Tests and Windows builds

The `.github/workflows/windows-build.yml` workflow runs the core unit tests and builds a Windows x64 standalone application on pushes and pull requests. Downloadable artifacts are available from successful workflow runs for a limited retention period; they are build artifacts, not a permanent release. A tagged GitHub Release can be added for longer-term distribution.

## Important limitations

This is an initial defensive workbench, not a commercial-grade vulnerability scanner. An open port or HTTP response is an observation, not proof of a vulnerability. Built-in wordlists are intentionally small; supply an appropriate wordlist for broader coverage. Packet capture requires Scapy plus the platform's packet-capture support and suitable privileges. Only assess assets you own or are explicitly authorized to test. The password strength score is a heuristic and must not be treated as a security guarantee. Passwords are not logged or exported.

## Troubleshooting

- If the GUI does not open from source, verify Tkinter: `python -m tkinter`.
- If a host cannot be resolved, check the hostname and DNS connectivity.
- If a web request fails, check the URL, connectivity, TLS configuration, and target permissions.
- If packet capture reports permission or interface errors on Windows, install/repair Npcap, refresh interfaces, and check capture permissions. On Kali, verify Scapy and interface permissions.
- If Windows Defender or another security product blocks the executable, verify the artifact came from this repository's workflow before deciding whether to allow it.
