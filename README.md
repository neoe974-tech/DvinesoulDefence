# DVINESOUL DEFENCE

Version 0.2.0 — integrated Kali/Linux desktop workbench built with Python 3 and Tkinter.

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

Run as root only when you specifically need packet capture privileges; ordinary scanning and local auditing should run as your normal user. Scapy capture is optional. The other core functions use Python's standard library.

## Included real functions

- TCP port inventory with bounded concurrency and explicit authorization confirmation.
- HTTP directory/path discovery using a supplied wordlist or a small built-in starter list.
- DNS subdomain resolution using a supplied wordlist or a small built-in starter list.
- Threat-surface inventory combining common TCP ports and optional HTTP path checks.
- Optional Scapy passive packet metadata capture with start/stop controls.
- Local system facts and dependency checks.
- Local password-strength heuristic and secure random password generation.
- JSON evidence export.

## Important limitations

This is a working initial integration, not a commercial-grade vulnerability scanner. An open port or HTTP response is an observation, not proof of a vulnerability. Built-in wordlists are intentionally small; supply an appropriate wordlist for broader coverage. Packet capture requires Scapy, suitable privileges, and a supported interface. Only assess assets you own or are explicitly authorized to test. The password strength score is a heuristic and must not be treated as a security guarantee. Passwords are not logged or exported.

## Troubleshooting

- If the GUI does not open, verify Tkinter: `python3 -m tkinter`.
- If a host cannot be resolved, check the hostname and DNS connectivity.
- If a web request fails, check the URL, connectivity, TLS configuration, and target permissions.
- If packet capture reports permission or interface errors, verify the interface and Scapy installation; do not run the entire app as root unless needed.
# DvinesoulDefence
