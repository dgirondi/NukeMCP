# Security model

NukeMCP gives an LLM client real control over a running Nuke session, including (via `execute_nuke_code`) arbitrary code execution with the same filesystem access as the Nuke process itself. This is by design — it was the explicitly chosen capability level for this project — but it's worth being precise about the trust boundary.

## What's protected

- **The addon's socket binds to `127.0.0.1` only**, never `0.0.0.0`. It is not reachable from the network, only from processes running on the same machine, as the same user (or root). `DEFAULT_HOST` is the only value `start_listener()` ever binds to in v1; the `NUKEMCP_HOST` env var exists for flexibility but is not a supported way to widen the bind address.
- **`save_script`/`open_script` require an explicit absolute path.** Relative paths are rejected before any request is even sent. `save_script`'s result always states whether an existing file was overwritten.
- **`execute_nuke_code`'s tool description states plainly** that it has full Nuke-API-plus-filesystem reach, so the calling LLM (and any permission prompts your MCP client shows) has accurate information before invoking it.

## What's deliberately *not* protected, for now

**There is no authentication handshake on the socket.** Any local process on the machine, running as the same OS user, can connect to `127.0.0.1:9787` and issue commands — including `execute_nuke_code`. This matches the precedent set by Blender's MCP addon, which makes the same choice for the same reason: on a single-user workstation, a loopback-only bind is the standard trust boundary. A plaintext shared secret sent over the same loopback socket wouldn't meaningfully raise the bar against a co-resident-process threat model — any process that could intercept it could just as easily act on the filesystem directly.

**This decision should be revisited if a non-loopback transport is ever added** (the project explicitly excluded HTTP/SSE from v1). The moment the listener becomes reachable from anything other than the local machine, a real auth story (token, mTLS, etc.) becomes necessary — this is a deliberate, documented decision to revisit then, not a silent gap today.

## Practical implications

- Don't run NukeMCP's addon on a shared/multi-user machine where you don't trust other local users.
- Treat `execute_nuke_code` the way you'd treat giving someone a Python shell on your machine — because that's effectively what it is, scoped to Nuke's process.
- The structured tools (`create_node`, `set_knob_values`, etc.) are the safer default; reach for `execute_nuke_code` only when nothing else covers the need.
