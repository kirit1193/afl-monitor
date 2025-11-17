# AFL Overseer

A monitoring tool for AFL/AFL++ fuzzing campaigns. Points it at your sync directory and it shows you what's happening with your fuzzers.

[![PyPI version](https://img.shields.io/pypi/v/afl-overseer.svg)](https://pypi.org/project/afl-overseer/)
[![Python](https://img.shields.io/pypi/pyversions/afl-overseer.svg)](https://pypi.org/project/afl-overseer/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

## What it does

Reads AFL fuzzer_stats files and shows you:
- Which fuzzers are alive/dead/starting
- Execution speed and coverage
- Crashes and hangs
- CPU and memory usage per fuzzer
- Warning when things look wrong (dead fuzzers, low stability, slow execution)

You can use it in three ways:
- Terminal UI with live updates (default)
- Web dashboard with graphs
- One-shot output for scripts

Originally based on [afl-monitor](https://github.com/reflare/afl-monitor) by Paul S. Ziegler, but rewritten for Python 3.8+ with support for AFL++ 4.x features and a bunch of new stuff.

## Installation

**From PyPI:**
```bash
pip install afl-overseer
afl-overseer /path/to/sync_dir
```

**From source:**
```bash
git clone https://github.com/kirit1193/afl-overseer.git
cd afl-overseer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
chmod +x afl-overseer
./afl-overseer /path/to/sync_dir
```

Needs Python 3.8+ and works on Linux, macOS, or WSL2.

## Usage

**TUI (default):**
```bash
afl-overseer /path/to/sync_dir

# Keys:
#   q - quit
#   1/2/3 - compact/normal/detailed view
#   d - toggle showing dead fuzzers
```

**Web dashboard:**
```bash
# With TUI
afl-overseer -w /path/to/sync_dir

# Just web server (no TUI)
afl-overseer -w --headless /path/to/sync_dir

# Custom port
afl-overseer -w -p 3000 /path/to/sync_dir

# Then open http://localhost:8080
```

The web UI has:
- Real-time graphs (speed, coverage, crashes over time)
- Sortable fuzzer table (click column headers)
- System resource monitoring
- Dark/light theme
- REST API at `/api/stats`

**Static output:**
```bash
# One-time check
afl-overseer -s /path/to/sync_dir

# Detailed stats
afl-overseer -s -v /path/to/sync_dir

# Run command when new crashes found
afl-overseer -s -e './alert.sh' /path/to/sync_dir
```

## Command options

```
-t, --tui          TUI mode (default)
-s, --static       Static output (no updates)
-w, --web          Start web server
-p, --port PORT    Web server port (default: 8080)
--headless         Web server without TUI
-v, --verbose      Show per-fuzzer stats
-i, --interval N   Refresh interval in seconds (default: 5)
-d, --show-dead    Include dead fuzzers
-e, --execute CMD  Run command on new crashes
--help             Show help
--version          Show version
```

## Metrics tracked

All the standard AFL stuff:
- Execution speed, total execs, runtime
- Coverage (edge coverage %)
- Crashes, hangs, corpus size
- Cycles done, stability, timeouts

Plus AFL++ 4.x additions:
- Test cache stats (size, count, evictions)
- CPU affinity, peak RSS
- Edges found vs total edges
- Slowest execution time
- Execs since last crash
- And a bunch more (50+ fields total)

Also tracks per-fuzzer CPU and memory usage via psutil.

## Crash notifications

Run a script when new crashes are detected:
```bash
afl-overseer -s -e './notify.sh' /path/to/sync_dir
```

The script gets summary info on stdin:
```
AFL Overseer - New Crash Detected!

Timestamp: 2024-01-15 14:30:00
Total Crashes: 5
New Crashes: 2
Active Fuzzers: 8/10
Coverage: 12.34%
```

Example notification script:
```bash
#!/bin/bash
MESSAGE=$(cat)
curl -X POST https://hooks.slack.com/... -d "{\"text\": \"$MESSAGE\"}"
```

## Remote monitoring

Run headless on your fuzzing server:
```bash
afl-overseer -w --headless -p 8080 /sync_dir
```

SSH tunnel from your laptop:
```bash
ssh -L 8080:localhost:8080 user@fuzzer-server
```

Then open http://localhost:8080 in your browser.

Or set up a systemd service:
```ini
[Unit]
Description=AFL Overseer Web Dashboard
After=network.target

[Service]
Type=simple
User=fuzzer
WorkingDirectory=/home/fuzzer
ExecStart=/usr/local/bin/afl-overseer -w --headless -i 60 /fuzzing/sync_dir
Restart=always

[Install]
WantedBy=multi-user.target
```

## How it detects fuzzer status

- **Alive**: Process exists and responds to signals
- **Dead**: Process PID not found or fuzzer_stats hasn't been updated recently
- **Starting**: fuzzer_setup file newer than fuzzer_stats and recently modified

Warnings trigger when:
- Fuzzer is dead
- Timeout ratio ≥ 10%
- Execution speed < 100 execs/sec
- Cycles without finds > 10 (warning) or > 50 (critical)
- Stability < 80%
- Slowest execution > 100ms

## Performance

Tested with mock fuzzing setups:
- 4 fuzzers: ~7ms per scan
- 20 fuzzers: ~28ms per scan
- 100 fuzzers: ~111ms per scan

Roughly 600-900 fuzzers/sec throughput. Uses ThreadPoolExecutor for parallel processing and non-blocking CPU monitoring.

See `testing/benchmark.py` if you want to run benchmarks.

## Code structure

```
afl-overseer/
├── afl-overseer            # Main executable
├── src/
│   ├── cli.py              # CLI argument parsing
│   ├── tui.py              # Terminal UI (Textual)
│   ├── webserver.py        # Web server (aiohttp)
│   ├── models.py           # Data models
│   ├── parser.py           # Parses fuzzer_stats and plot_data
│   ├── process.py          # Process detection
│   ├── monitor.py          # Main monitoring logic
│   ├── utils.py            # Helper functions
│   └── output_terminal.py  # Terminal output formatting
└── testing/                # Test utilities
```

## Security notes

The web server is read-only (no forms, no user input, only GET requests). It just reads fuzzer_stats files and serves JSON.

That said, if you expose it to the internet:
- Use a reverse proxy (nginx) with rate limiting and SSL
- Or stick to SSH tunneling
- Set up firewall rules
- Keep dependencies updated

See [SECURITY.md](SECURITY.md) for more details.

## Differences from original afl-monitor

The original afl-monitor (Python 2.7) had some security issues with pickle usage and deprecated modules. This rewrite:
- Python 3.8+ with type hints
- No pickle or command injection
- Interactive TUI and web dashboard
- AFL++ 4.x support (50+ fields)
- Per-fuzzer resource monitoring
- Parallel processing

Thanks to Paul S. Ziegler for the original implementation.

## Troubleshooting

**"Permission denied" when checking processes:**
```bash
# Add your user to the fuzzer's group
sudo usermod -a -G fuzzer $USER
```

**"No fuzzers found":**

Check your directory structure. Should look like:
```
/sync_dir/
  ├── fuzzer01/
  │   └── fuzzer_stats
  ├── fuzzer02/
  │   └── fuzzer_stats
  └── ...
```

Point afl-overseer at `/sync_dir`, not `/sync_dir/fuzzer01`.

## License

MIT License - Copyright (c) 2024 kirit1193

Original afl-monitor: Apache License 2.0 - Copyright (c) 2017 Paul S. Ziegler, Reflare Ltd.

See [LICENSE](LICENSE) for details.

## Credits

- Original afl-monitor by Paul S. Ziegler
- AFL by Michal Zalewski
- AFL++ project and afl-whatsup

## Contributing

Issues and pull requests welcome at [GitHub](https://github.com/kirit1193/afl-overseer).
