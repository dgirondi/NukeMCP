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

## 2. Install the MCP server

Two ways to do this — pick one.

### Option A: Claude Desktop extension (easiest)

`server/` is packaged as a Claude Desktop Extension (`.mcpb` bundle, built with Anthropic's `@anthropic-ai/mcpb` packer). Build it once:

```bash
cd /Volumes/Vault/Projects/Dev/Nuke/NukeMCP
npx @anthropic-ai/mcpb pack server nukemcp.mcpb
```

Then double-click `nukemcp.mcpb` (or use Claude Desktop's "install extension from file") to install it. Claude Desktop runs `uv run nukemcp` itself using its own bundled `uv` — no manual venv setup, no system Python dependency. If you ever moved the addon's `NUKEMCP_HOST`/`NUKEMCP_PORT` off the defaults, set the matching values in the extension's settings in Claude Desktop (exposed as "Nuke addon host"/"Nuke addon port").

This only installs the **server-side** half — step 1 above (the Nuke addon + `NUKE_PATH`) is still required regardless of which install method you use here.

### Option B: uv (for Claude Code, or if you don't use the Desktop extension flow)

Install [`uv`](https://docs.astral.sh/uv/) if you don't already have it (`brew install uv` on macOS), then:

```bash
cd /Volumes/Vault/Projects/Dev/Nuke/NukeMCP/server
uv sync --extra dev
```

uv resolves dependencies from the committed `uv.lock` and creates a `.venv` automatically. Confirm with:

```bash
uv run nukemcp --help 2>&1 | head -1   # should start the server (Ctrl+C to stop)
```

## 3. Register the server with your MCP client

(Skip this section if you installed via the Claude Desktop extension above — that registers itself.)

**Claude Code:**

```bash
claude mcp add nukemcp -- uv --directory /Volumes/Vault/Projects/Dev/Nuke/NukeMCP/server run nukemcp
```

**Claude Desktop / any client using a `claude_desktop_config.json`-style config:**

```json
{
  "mcpServers": {
    "nukemcp": {
      "command": "uv",
      "args": ["--directory", "/Volumes/Vault/Projects/Dev/Nuke/NukeMCP/server", "run", "nukemcp"]
    }
  }
}
```

**Any other MCP-compatible client** (Gemini CLI, GPT-based agent frameworks, etc.): the same command + args form works — this is a standard stdio MCP server with no provider-specific code, so there's nothing else to configure per client.

## Notes

- The server only ever **attaches to an already-running, already-listening interactive Nuke session** — it never launches Nuke itself. Start Nuke first.
- If Nuke is busy (a modal dialog open, a manual render in progress, mid-drag in the UI), tool calls will block until Nuke's main thread is free, up to a 60 second timeout. This is expected — see [SECURITY.md](SECURITY.md) for why.
- If you see "Could not connect to Nuke on 127.0.0.1:9787", check that Nuke is running and the NukeMCP menu's listener is started.
