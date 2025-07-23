"""
dsl_parser.py

Purpose:
--------
Convert a subset of Mermaid.js DSL into a structured TaskGraph JSON format
used by our system. The parser is designed to be modular, extensible, and
capable of collecting all errors (syntax, semantic, structure) for debugging.

Key Features:
-------------
1. Preprocess DSL text (remove comments, normalize lines)
2. Parse node definitions and edge definitions separately
3. Support multiple node types: Param, MR, OP, Result, and control nodes (loop/if/etc.)
4. Parse edges with parameter order (in_1/out_2) and control flow labels (Yes/No)
5. Build expandable JSON structure (nodes, edges, runtime)
6. Validate DSL against a rule library (to be added later)
7. Return detailed debug info (error list) instead of halting on first error
"""

from typing import List, Dict, Tuple


# -------------------------------
# Public Interface
# -------------------------------

def parse_mermaid_dsl(dsl_text: str) -> Dict:
    """
    Main entry point for parsing Mermaid DSL.

    Args:
        dsl_text (str): Mermaid.js-formatted DSL string

    Returns:
        dict: {
            "nodes": [...],
            "edges": [...],
            "runtime": {...},     # minimal Markov-like state
            "errors": [...]       # list of error messages
        }

    Design:
        1. Preprocess DSL (clean text)
        2. Split into node and edge definitions
        3. Parse nodes → node objects
        4. Parse edges → edge objects
        5. Validate & collect errors
        6. Build JSON (static graph + runtime stub)
    """
    lines = preprocess_dsl(dsl_text)
    nodes_raw, edges_raw = split_nodes_edges(lines)
    
    # Placeholder: parse nodes and edges
    nodes = []   # Will hold parsed node dicts
    edges = []   # Will hold parsed edge dicts
    errors = []  # Collect syntax/semantic/structure errors
    
    # TODO: Call parse_nodes() and parse_edges() here in future
    # nodes, node_errors = parse_nodes(nodes_raw)
    # edges, edge_errors = parse_edges(edges_raw)
    # errors.extend(node_errors + edge_errors)

    # Build minimal runtime stub
    runtime = {
        "current_node": None,
        "previous_node": None,
        "next_node": None,
        "branch_decision": None,
        "loop_index": None
    }

    return {
        "nodes": nodes,
        "edges": edges,
        "runtime": runtime,
        "errors": errors
    }


# -------------------------------
# Step 1: Preprocess
# -------------------------------

def preprocess_dsl(dsl_text: str) -> List[str]:
    """
    Clean raw DSL text:
    - Ensure it starts with `flowchart TD`
    - Remove comments (// ...)
    - Remove blank lines
    - Normalize whitespace

    Returns:
        list[str]: Cleaned lines ready for parsing
    """
    lines = []
    errors = []

    # Split into lines & strip whitespace
    for i, line in enumerate(dsl_text.splitlines()):
        line = line.strip()
        # Skip comments and blank lines
        if not line or line.startswith("//"):
            continue
        lines.append(line)

    # Validate header
    if not lines or not lines[0].lower().startswith("flowchart td"):
        errors.append("Missing required header: 'flowchart TD'")
        # We keep parsing but note the error

    return lines


# -------------------------------
# Step 2: Split Node / Edge lines
# -------------------------------

def split_nodes_edges(lines: List[str]) -> Tuple[List[str], List[str]]:
    """
    Separate node definitions and edge definitions.

    Heuristic:
        - Node lines: contain '()' or '[]' or '{}'
        - Edge lines: contain '-->' (in/out/control connections)

    Returns:
        (nodes_raw, edges_raw): two lists of raw strings
    """
    nodes_raw = []
    edges_raw = []

    for line in lines:
        if "-->" in line:
            edges_raw.append(line)
        else:
            nodes_raw.append(line)

    return nodes_raw, edges_raw


# -------------------------------
# Step 3: Parse Nodes (future)
# -------------------------------

def parse_nodes(nodes_raw: List[str]) -> Tuple[List[Dict], List[str]]:
    """
    Parse raw node definitions into structured dicts.

    Node types:
        - Param_x("label")
        - MR_x(("label"))
        - OP_x["label"]
        - OP_if{"condition"}
        - Result["final"]

    Returns:
        nodes (list of dicts), errors (list of str)
    """
    # TODO: Implement with regex and rules
    return [], []


# -------------------------------
# Step 4: Parse Edges (future)
# -------------------------------

def parse_edges(edges_raw: List[str]) -> Tuple[List[Dict], List[str]]:
    """
    Parse raw edge definitions into structured dicts.

    Edge types:
        - Data input:  A -- in_1 --> B
        - Data output: A -- out_2 --> B
        - Control:     A --> B
        - Conditional: A -- Yes --> B

    Returns:
        edges (list of dicts), errors (list of str)
    """
    # TODO: Implement with regex and rules
    return [], []


# -------------------------------
# Step 5: Validation (future)
# -------------------------------

def validate_graph(nodes: List[Dict], edges: List[Dict]) -> List[str]:
    """
    Perform semantic & structural checks:
        - Node names must be unique
        - Edges must connect existing nodes
        - in_x/out_x numbering must not conflict
        - Yes/No edges must come from OP_if nodes

    Returns:
        errors (list of str)
    """
    # TODO: Implement
    return []

