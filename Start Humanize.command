#!/bin/bash
# Double-click to open the Humanize kit in your browser. Keep this window open while you use it.
cd "$(dirname "$0")"
if command -v python3 >/dev/null 2>&1; then
  python3 tools/app.py
else
  echo
  echo "Python 3 is not installed on this computer."
  echo "Get it free from https://www.python.org/downloads/ then double-click this file again."
  echo
  read -r -p "Press Enter to close."
fi
