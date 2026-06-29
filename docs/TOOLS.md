# NukeMCP tool reference

All tools require Nuke to be running with the NukeMCP addon's listener started. If not, every tool fails with the same clear connection error rather than hanging.

## Querying

| Tool | Params | Returns |
|---|---|---|
| `get_script_info` | — | Root knobs: frame range, fps, format, script path, modified flag |
| `list_nodes` | `filter_class?: str` | `name`, `class`, `xpos`/`ypos`, `selected` for every node (or only nodes of `filter_class`) |
| `get_node_graph` | `filter_class?: str` | Like `list_nodes`, plus `inputs` (connected node names by input index) and `outputs` (dependent node names) |
| `get_node_info` | `node_name: str` | Full knob dump for one node. Each knob reports `value`, `animated` (bool), and `expression` (the expression text, or null) — animated/expression-driven knobs are flagged rather than silently collapsed to their current-frame value |
| `get_selection` | — | Currently selected nodes (name + class). Reflects live state, which can change between calls |

## Editing

| Tool | Params | Notes |
|---|---|---|
| `create_node` | `node_class: str`, `knobs?: dict`, `xpos?/ypos?: int`, `inputs?: list[str]` | Per-knob and per-input errors are collected and returned alongside any that succeeded, rather than aborting on the first failure |
| `set_knob_values` | `node_name: str`, `knobs: dict` | Same partial-failure behavior as `create_node` |
| `connect_nodes` | `from_node: str`, `to_node: str`, `input_index: int = 0` | |
| `delete_node` | `node_name: str` | |
| `select_nodes` | `node_names: list[str]`, `additive: bool = False` | Clears existing selection first unless `additive` |

## Rendering

| Tool | Params | Notes |
|---|---|---|
| `render` | `node_name?: str`, `first_frame: int`, `last_frame: int` | Renders all Write nodes if `node_name` omitted. Can legitimately take a long time — blocks until done or the connection times out (60s default). `success`/`error` in the result is the authoritative signal; captured `stdout`/`stderr` is best-effort supplementary info |
| `get_node_screenshot` | `node_name: str`, `frame?: int` | Renders one frame to a temp PNG via a temporary Write node, returns it as an inline image, then deletes the temp file |

## Script I/O

| Tool | Params | Notes |
|---|---|---|
| `open_script` | `path: str` (absolute) | Replaces the current session entirely — `nuke.scriptOpen` always opens a new script, there's no merge option |
| `save_script` | `path: str` (absolute) | Result includes `overwrote_existing: bool` |

Relative paths are rejected immediately (before any round trip to Nuke).

## Escape hatch

| Tool | Params | Notes |
|---|---|---|
| `execute_nuke_code` | `code: str` | Runs arbitrary Python on Nuke's main thread with full `nuke`-API-plus-filesystem access. Assign to `__result__` to return a value; stdout/stderr are captured and returned alongside it. Prefer the structured tools above when they cover what you need — see [SECURITY.md](SECURITY.md) |

## Not in v1

A `list_node_classes`/`get_node_default_knobs` introspection tool (discover a node class's default knobs without creating one for real) was deliberately deferred. It's fully achievable today via `create_node` → `get_node_info` → `delete_node` (three calls instead of one); it was deferred because some node classes have creation-time side effects (dialogs, `knobChanged` callbacks assuming a real graph context) worth handling deliberately rather than rushing. The addon's handler registry (`nuke_addon/nukemcp_server/dispatch.py`) is a plain name→function dict specifically so adding this later doesn't require touching the dispatch or transport code.
