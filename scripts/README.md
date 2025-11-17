# Documentation Scripts

## capture_screenshots.py

Script to capture screenshots of the TUI and WebUI for documentation purposes.

**Requirements:**
```bash
pip install playwright pillow
python -m playwright install chromium
```

**Usage:**
```bash
python scripts/capture_screenshots.py
```

This will:
1. Start the web server on port 8899
2. Launch a browser and capture screenshots of all WebUI tabs
3. Save images to `assets/` directory
4. Provide instructions for TUI recording

**Note:** This script requires a machine with display support (X11/Wayland). It won't work in headless Docker containers.

**For TUI recording:**

Use one of these tools:
```bash
# asciinema (terminal session recording)
asciinema rec assets/tui-demo.cast
afl-overseer testing/mock_sync

# termtosvg (SVG animation)
termtosvg assets/tui-demo.svg
afl-overseer testing/mock_sync

# Or just take a manual screenshot
afl-overseer testing/mock_sync
# Then use your OS screenshot tool
```

## Output Files

Screenshots are saved to:
- `assets/webui-overview.png` - WebUI Overview tab
- `assets/webui-fuzzers.png` - WebUI Fuzzers tab
- `assets/webui-graphs.png` - WebUI Graphs tab
- `assets/tui-demo.cast` or `.svg` - TUI recording (manual)
