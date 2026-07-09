# NukeMCP tool reference

All tools require Nuke to be running with the NukeMCP addon's listener started. If not, every tool fails with the same clear connection error rather than hanging.

All tools that modify the script (create, edit, delete, connect, animate, batch) are wrapped in a Nuke undo group and can be undone with Cmd+Z / Ctrl+Z.

## Querying

| Tool | Params | Returns |
|---|---|---|
| `get_script_info` | — | Root knobs: frame range, fps, format, script path, modified flag |
| `list_nodes` | `filter_class?: str`, `recurse_groups?: bool` | `name`, `class`, `xpos`/`ypos`, `selected` for every node |
| `get_node_graph` | `filter_class?: str`, `recurse_groups?: bool` | Like `list_nodes`, plus `inputs` (connected node names by input index) and `outputs` |
| `get_node_info` | `node_name: str` | Full knob dump for one node. Each knob reports `value`, `animated` (bool), and `expression` (text or null) |
| `get_selection` | — | Currently selected nodes (name + class). Reflects live state |
| `get_node_errors` | `recurse_groups?: bool` | Every node with a current error — name, class, and message |
| `get_node_metadata` | `node_name: str`, `frame?: int` | Embedded image metadata (EXR tags, colorspace, camera info, etc.) — most useful on Read nodes |

## Discovery

| Tool | Params | Returns |
|---|---|---|
| `list_node_classes` | `category?: str` | Available node classes grouped by Nodes-menu category. Use before `create_node` to discover what's available |
| `get_node_default_knobs` | `node_class: str` | Default knob values for a node class, by creating a temporary node, reading its knobs, and immediately deleting it |

## Editing

| Tool | Params | Notes |
|---|---|---|
| `create_node` | `node_class: str`, `knobs?: dict`, `xpos?/ypos?: int`, `inputs?: list[str]` | Per-knob and per-input errors collected and returned, rather than aborting on first failure |
| `set_knob_values` | `node_name: str`, `knobs: dict` | Same partial-failure behavior as `create_node` |
| `connect_nodes` | `from_node: str`, `to_node: str`, `input_index: int = 0` | |
| `delete_node` | `node_name: str` | |
| `duplicate_node` | `node_name: str`, `xpos_offset: int = 100`, `ypos_offset: int = 0` | Copies all knob values via script round-trip |
| `select_nodes` | `node_names: list[str]`, `additive: bool = False` | Clears existing selection first unless `additive` |

## Animation

| Tool | Params | Notes |
|---|---|---|
| `set_knob_expression` | `node_name: str`, `knob_name: str`, `expression: str`, `field_index?: int` | Set a Nuke expression. Pass empty string to clear |
| `set_knob_keyframe` | `node_name: str`, `knob_name: str`, `frame: float`, `value: float`, `field_index?: int` | Set one keyframe; enables animation on the knob if not already animated |
| `remove_knob_animation` | `node_name: str`, `knob_name: str`, `field_index?: int` | Remove all animation curves and expressions, leaving the knob static |

## Viewer

| Tool | Params | Notes |
|---|---|---|
| `get_viewer_node` | — | Active Viewer node info: what it's connected to, current frame, gain, gamma |
| `set_viewer_input` | `node_name: str`, `input_index: int = 0` | Connect a node to the Viewer (input 0 = A, 1 = B) |
| `zoom_to_node` | `node_name: str` | Pan and zoom the Node Graph to centre on the given node |

## Rendering

| Tool | Params | Notes |
|---|---|---|
| `render` | `node_name?: str`, `first_frame: int`, `last_frame: int` | Renders all Write nodes if `node_name` omitted. Blocks until done (or 60s timeout). `success`/`error` is authoritative; `stdout`/`stderr` is supplementary |
| `get_node_screenshot` | `node_name: str`, `frame?: int` | Renders one frame via a temporary Write node, returns it as an inline image |

## Script I/O

| Tool | Params | Notes |
|---|---|---|
| `open_script` | `path: str` (absolute) | Replaces the current session — there is no merge option for `scriptOpen` |
| `save_script` | `path: str` (absolute) | Result includes `overwrote_existing: bool` |
| `merge_script` | `path: str` (absolute) | Import nodes from another .nk into the current script without replacing it |

Relative paths are rejected immediately (before any round trip to Nuke).

## Batch

| Tool | Params | Notes |
|---|---|---|
| `batch` | `operations: list[dict]`, `label?: str`, `stop_on_error?: bool` | Execute multiple operations as one atomic, undoable action. Each operation is `{"tool": "<name>", "params": {...}}`. Returns per-operation results |

Use `batch` when building multi-node graphs: one undo group, one round trip.

## Escape hatch

| Tool | Params | Notes |
|---|---|---|
| `execute_nuke_code` | `code: str` | Runs arbitrary Python on Nuke's main thread with full `nuke`-API-plus-filesystem access. Assign to `__result__` to return a value; stdout/stderr are captured. Prefer structured tools — see [SECURITY.md](SECURITY.md) |
