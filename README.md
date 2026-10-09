# DvinesoulDefence

**A practical defensive cybersecurity workbench for Windows and Kali Linux.**

DvinesoulDefence is a Python/Tkinter desktop application for authorized security checks, local system inspection, and lightweight evidence collection. It brings several useful defensive utilities into one interface, with a Windows x64 standalone build produced by GitHub Actions.

<p align="center">
  <a href="https://github.com/neoe974-tech/DvinesoulDefence/actions/workflows/windows-build.yml"><img src="https://github.com/neoe974-tech/DvinesoulDefence/actions/workflows/windows-build.yml/badge.svg" alt="Windows build status"></a>
  <img src="https://img.shields.io/badge/Python-3.12%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Kali%20Linux-555" alt="Platforms">
  <img src="https://img.shields.io/badge/Focus-Defensive%20Security-2ea44f" alt="Defensive security">
  <img src="https://img.shields.io/badge/License-Not%20specified-lightgrey" alt="License not specified">
</p>

> **Use responsibly:** Scan or capture traffic only on systems and networks you own or have explicit permission to assess. This project is an early-stage defensive utility, not a substitute for a full security assessment.

## Features

| Module | Purpose |
| --- | --- |
| **Threat-surface inventory** | Combines common TCP-port checks with optional HTTP path checks. |
| **TCP port inventory** | Checks selected TCP ports with bounded concurrency and authorization confirmation. |
| **HTTP path discovery** | Checks paths using a supplied wordlist or a small built-in starter list. |
| **DNS subdomain checks** | Resolves candidate subdomains from a supplied or starter wordlist. |
| **Packet sniffer** | Optional passive packet-metadata capture with start/stop controls. |
| **System audit** | Displays local system facts and checks selected dependencies. |
| **Password tools** | Generates random passwords and estimates password strength locally. Passwords are not logged or exported. |
| **Keylogger Lab** | A visible, app-local keyboard-event test area for security demonstrations. It records key names/modifiers only while active and does not capture keystrokes from other applications. |
| **Evidence export** | Exports supported findings and observations as JSON. |

## Get the Windows application

A Windows x64 standalone build is published as a GitHub Actions artifact.

1. Open [**Windows build workflow runs**](https://github.com/neoe974-tech/DvinesoulDefence/actions/workflows/windows-build.yml).
2. Open the latest successful run.
3. In **Artifacts**, download `DvinesoulDefence-Windows-x64`.
4. Extract the ZIP and run `DvinesoulDefence.exe` from the extracted `DvinesoulDefence` folder.

Keep the extracted folder and its support files together; do not move the EXE by itself. Workflow artifacts are temporary and expire according to GitHub's retention policy.

## Packet capture requirements

Live packet capture uses Scapy and requires platform-specific capture support.

### Windows

1. Install [Npcap](https://npcap.com/) from its official website.
2. Restart DvinesoulDefence.
3. Open **PACKET SNIFFER**, select **REFRESH INTERFACES**, and choose the correct network interface.
4. If capture fails, check Npcap installation, interface availability, and permissions.

Npcap is a system-level driver and is not bundled or silently installed by this project. Packet capture is optional; other core features can be used without it.

### Kali Linux

Install Tkinter and launch the application:

```bash
sudo apt update
sudo apt install python3-tk
python3 app/main.py
```

For optional Scapy packet capture:

```bash
sudo apt install python3-scapy
sudo python3 app/main.py
```

Use elevated privileges only when needed for packet capture. Prefer running the application as your normal user for ordinary checks.

## Run from source on Windows

1. Install Python from [python.org](https://www.python.org/downloads/windows/). Python 3.12 is used by the automated Windows build.
2. Ensure the installer includes Tcl/Tk.
3. Clone or download this repository.
4. Run `run_windows.bat` to launch from source, or `build_windows.bat` to run tests and create a standalone build.

Building from source requires a compatible Python installation and internet access to install dependencies.

## Development and quality checks

The [Windows build workflow](https://github.com/neoe974-tech/DvinesoulDefence/actions/workflows/windows-build.yml) runs the core tests, packages a standalone Windows application, and uploads the result as an artifact.

To run the core tests locally:

```bash
python -m unittest discover -s tests -v
```

## Project limitations

- This is an early-stage defensive workbench, not a commercial-grade vulnerability scanner.
- An open port or an HTTP response is an observation, not proof of a vulnerability.
- Built-in wordlists are small. Use an appropriate wordlist when broader coverage is needed.
- Packet capture depends on Scapy, operating-system support, interface selection, and permissions.
- The password-strength result is a heuristic, not a security guarantee.
- The Keylogger Lab is intentionally limited to its visible in-app test field; it is not an OS-wide keylogger.
- Only assess assets you own or are explicitly authorized to test.

## Troubleshooting

- **The GUI does not open from source:** check Tkinter with `python -m tkinter`.
- **A hostname does not resolve:** verify the hostname and DNS connectivity.
- **A web request fails:** check the URL, network connectivity, TLS settings, and target permissions.
- **Packet capture fails:** verify Scapy, Npcap (Windows), the selected interface, and required permissions.
- **Windows security software flags a build:** verify that you downloaded the artifact from this repository's official Actions workflow before deciding how to proceed.

## Roadmap

- Improve packet-sniffer diagnostics and cross-platform reliability.
- Expand automated tests around individual tools and error handling.
- Add versioned releases and clearer installation notes as the project stabilizes.

---

**Maintainer:** [neoe974-tech](https://github.com/neoe974-tech)  
**Repository:** [DvinesoulDefence](https://github.com/neoe974-tech/DvinesoulDefence)
