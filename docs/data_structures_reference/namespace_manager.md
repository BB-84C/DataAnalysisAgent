# Namespace Manager - Data Structure Reference

## Overview

This module implements the **Namespace & Result Manager** role in the system architecture.  
It manages MATLAB workspace snapshots, runtime-level variable tracking, execution logs, and provides structured outputs for debugging and workflow tracing.

---

## 1. Module-Level Attributes

### `current_snapshot: dict[str, dict]`
Latest workspace snapshot (not currently updated in code).

**Format:**
```json
{
  "<var_name>": {
    "class": "<MATLAB class name>",
    "size": "<rows>x<cols>"
  }
}
````

**Example:**

```json
{
  "topo":    {"class": "double", "size": "256x256"},
  "params":  {"class": "struct", "size": "1x1"},
  "filename":{"class": "char",   "size": "1x12"}
}
```

---

### `runtime_snapshots: dict[str, dict]`

Stores **start** and **end** workspace snapshots for each runtime.

**Format:**

```json
{
  "<runtime_EDID>": {
    "start": { "<var>": {"class": "...", "size": "..."} },
    "end":   { "<var>": {"class": "...", "size": "..."} } | null
  }
}
```

**Example:**

```json
{
  "runtime_OP_1": {
    "start": {
      "raw_path": {"class": "char", "size": "1x28"}
    },
    "end": null
  }
}
```

---

### `runtime_outputs: dict[str, dict]`

Stores the **diff** (new/modified variables) calculated at the end of a runtime.

**Format:**

```json
{
  "<runtime_EDID>": {
    "<var_name>": {
      "class": "<MATLAB class name>",
      "size":  "<rows>x<cols>",
      "status": "added" | "modded"
    }
  }
}
```

**Example:**

```json
{
  "runtime_OP_1": {
    "topo": {"class": "double", "size": "256x256", "status": "added"},
    "fft":  {"class": "double", "size": "256x256", "status": "added"}
  }
}
```

---

### `execution_log: list[dict]`

Global script call log (not tied to a specific runtime).

**Format:**

```json
[
  {"script": "<script_name>", "params": { /* parameters */ }},
  ...
]
```

**Example:**

```json
[
  {"script": "opensxm_auto", "params": {"path": "Data", "filename": "07_15_25_002.sxm", "pnum": "1"}},
  {"script": "polybackRow",  "params": {"figure_name": "fig_07_15_25_002", "order": 3}}
]
```

---

### `runtime_logs: dict[str, list[dict]]`

Runtime-specific script call logs.

**Format:**

```json
{
  "<runtime_EDID>": [
    {"script": "<script_name>", "params": { /* parameters */ }},
    ...
  ]
}
```

**Example:**

```json
{
  "runtime_OP_1": [
    {"script": "opensxm_auto", "params": {"path": "Data", "filename": "07_15_25_002.sxm", "pnum": "1"}},
    {"script": "fftamp",       "params": {"input_var": "topo"}}
  ]
}
```

---

## 2. Function Outputs

### `snapshot_workspace() -> dict[str, dict]`

Returns the current workspace snapshot.
See `current_snapshot` format for structure.

---

### `start_runtime(runtime_EDID: str) -> None`

Stores the start snapshot under:

```python
runtime_snapshots[runtime_EDID] = {
    "start": <snapshot>,
    "end": None
}
```

---

### `log_script_call(script_name: str, params: dict, runtime_EDID: str|None) -> None`

Appends a log entry to:

* `execution_log` (global)
* `runtime_logs[runtime_EDID]` (if provided)

**Log entry format:**

```json
{"script": "<script_name>", "params": { /* parameters */ }}
```

---

### `end_runtime(runtime_EDID: str) -> dict`

Calculates the diff between start and end snapshots.
Updates:

```python
runtime_snapshots[runtime_EDID]["end"] = end_snapshot
runtime_outputs[runtime_EDID] = diff
```

**Return format:**

```json
{
  "diff": { "<var_name>": {"class": "...", "size": "...", "status": "..."} },
  "log":  [ {"script": "...", "params": {...}}, ... ]
}
```

---

### `get_runtime_outputs(runtime_EDID: str) -> dict`

Returns:

```json
{
  "diff": { /* same as runtime_outputs[runtime_EDID] */ },
  "log":  [ /* same as runtime_logs[runtime_EDID] */ ]
}
```

---

### `get_runtime_status(runtime_EDID: str) -> str`

Possible values: `"pending" | "running" | "success" | "failed" | "unknown"`

---

## 3. Full Runtime Example

```json
{
  "runtime_snapshots": {
    "runtime_OP_1": {
      "start": {
        "raw_path": {"class": "char", "size": "1x28"}
      },
      "end": {
        "raw_path": {"class": "char",   "size": "1x28"},
        "topo":     {"class": "double", "size": "256x256"},
        "fft":      {"class": "double", "size": "256x256"}
      }
    }
  },
  "runtime_logs": {
    "runtime_OP_1": [
      {"script": "opensxm_auto", "params": {"path": "Data", "filename": "07_15_25_002.sxm", "pnum": "1"}},
      {"script": "fftamp",       "params": {"input_var": "topo"}}
    ]
  },
  "runtime_outputs": {
    "runtime_OP_3": {
      "topo": {"class": "double", "size": "256x256", "status": "added"},
      "fft":  {"class": "double", "size": "256x256", "status": "added"}
    }
  },
  "execution_log": [
    {"script": "opensxm_auto", "params": {"path": "Data", "filename": "07_15_25_002.sxm", "pnum": "1"}},
    {"script": "fftamp",       "params": {"input_var": "topo"}}
  ]
}
```
