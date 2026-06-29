# Installing NukeMCP

This repo has two independent halves to install: the addon that runs inside Nuke, and the standalone MCP server process that your LLM client launches.

## 1. Install the Nuke-side addon

Add the addon's directory to `NUKE_PATH` so Nuke auto-loads its `menu.py` at startup. In `~/.zshrc` (or wherever your shell's environment is configured):

```bash
export NUKE_PATH="/Volumes/Vault/Projects/Dev/Nuke/NukeMCP/nuke_addon:$NUKE_PATH"
```

Restart your shell (or `source ~/.zshrc`), then launch Nuke. You should see a "NukeMCP" menu appear, and a line like this in the Script Editor / the terminal Nuke was launched from:

```
[NukeMCP] listener started on 127.0.0.1:9787
```

The listener auto-starts by default. To disable auto-start and use the menu's "Start Server" entry manually instead, set `NUKEMCP_AUTOSTART=0` in the same environment.

## 2. Install the MCP server's Python dependencies

```bash
cd /Volumes/Vault/Projects/Dev/Nuke/NukeMCP/server
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

(If you have [`uv`](https://docs.astral.sh/uv/) installed, `uv venv && uv pip install -e ".[dev]"` is faster and equivalent.)

This installs a `nukemcp` console script and makes `python -m nukemcp` work. Confirm with:

```bash
.venv/bin/python -m nukemcp --help 2>&1 | head -1   # should start the server (Ctrl+C to stop)
```

## 3. Register the server with your MCP client

Use the **absolute path to the venv's interpreter** — MCP client host processes typically don't inherit your interactive shell's `PATH`, so a bare `nukemcp` command will fail even though it works fine in your terminal.

**Claude Code:**

```bash
claude mcp add nukemcp -- /Volumes/Vault/Projects/Dev/Nuke/NukeMCP/server/.venv/bin/python -m nukemcp
```

**Claude Desktop / any client using a `claude_desktop_config.json`-style config:**

```json
{
  "mcpServers": {
    "nukemcp": {
      "command": "/Volumes/Vault/Projects/Dev/Nuke/NukeMCP/server/.venv/bin/python",
      "args": ["-m", "nukemcp"]
    }
  }
}
```

**Any other MCP-compatible client** (Gemini CLI, GPT-based agent frameworks, etc.): the same command + args form works — this is a standard stdio MCP server with no provider-specific code, so there's nothing else to configure per client.

## Notes

- The server only ever **attaches to an already-running, already-listening interactive Nuke session** — it never launches Nuke itself. Start Nuke first.
- If Nuke is busy (a modal dialog open, a manual render in progress, mid-drag in the UI), tool calls will block until Nuke's main thread is free, up to a 60 second timeout. This is expected — see [SECURITY.md](SECURITY.md) for why.
- If you see "Could not connect to Nuke on 127.0.0.1:9787", check that Nuke is running and the NukeMCP menu's listener is started.
