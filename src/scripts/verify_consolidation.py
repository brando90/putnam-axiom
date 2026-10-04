#!/usr/bin/env python3
"""Check the consolidation without importing or running evaluation code.

Requires PyYAML. The default root assumes this file is installed at
src/scripts/verify_consolidation.py; use --root for another checkout.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

import yaml


class FunctionReference(str):
    """An inert replacement for the harness's executable !function tag."""


class TaskLoader(yaml.SafeLoader):
    pass


TaskLoader.add_constructor(
    "!function", lambda loader, node: FunctionReference(loader.construct_scalar(node))
)


def function_references(value):
    if isinstance(value, FunctionReference):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from function_references(child)
    elif isinstance(value, list):
        for child in value:
            yield from function_references(child)


def git(root, *args):
    result = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=False
    )
    if result.returncode:
        raise ValueError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def verify(root):
    errors = []
    counts = {}
    manifest_path = root / "paper_latex_and_notes/consolidation/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    def local_file(relative):
        if not isinstance(relative, str) or Path(relative).is_absolute():
            raise ValueError(f"Invalid repository-relative path: {relative!r}")
        path = (root / relative).resolve()
        if not path.is_relative_to(root):
            raise ValueError(f"Path escapes repository: {relative}")
        if not path.is_file():
            raise ValueError(f"Missing file: {relative}")
        return path

    for section, path_key in (("imports", "destination"), ("preserved_baseline", "path")):
        entries = manifest.get(section)
        if not isinstance(entries, list) or not entries:
            raise ValueError(f"Manifest {section} must be a nonempty list")
        checked = 0
        seen = set()
        for entry in entries:
            try:
                relative = entry[path_key]
                if relative in seen:
                    raise ValueError(f"Duplicate {section} path: {relative}")
                seen.add(relative)
                path = local_file(relative)
                expected = entry["sha256"]
                if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
                    raise ValueError(f"Invalid SHA-256 hash for {relative}")
                actual = hashlib.sha256(path.read_bytes()).hexdigest()
                if actual != expected:
                    raise ValueError(f"Hash mismatch: {relative}; expected {expected}, got {actual}")
                checked += 1
            except (KeyError, TypeError, OSError, ValueError) as exc:
                errors.append(f"{section}: {exc}")
        counts[section] = (checked, len(entries))

    tasks_root = root / "src/lm_evaluation_harness/tasks"
    yaml_paths = sorted(set(tasks_root.rglob("*.yaml")) | set(tasks_root.rglob("*.yml")))
    if not yaml_paths:
        errors.append("No active task YAML files found")
    utility_paths = sorted({path.parent / "utils.py" for path in yaml_paths})
    imported_paths = {entry["destination"] for entry in manifest["imports"]}
    definitions = {}
    compiled = 0
    for path in utility_paths:
        try:
            relative = str(path.relative_to(root))
            if relative not in imported_paths:
                raise ValueError(f"Active utility missing from import manifest: {relative}")
            local_file(relative)
            source = path.read_bytes()
            tree = ast.parse(source, filename=relative)
            compile(tree, relative, "exec")  # Validate syntax only; never execute or write bytecode.
            definitions[path] = {
                node.name for node in tree.body
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
            compiled += 1
        except (OSError, SyntaxError, ValueError) as exc:
            errors.append(f"Utility {path.relative_to(root)}: {exc}")

    raw_configs = {}
    include_links = 0
    function_count = 0
    for path in yaml_paths:
        try:
            local_file(str(path.relative_to(root)))
            config = yaml.load(path.read_text(encoding="utf-8"), Loader=TaskLoader)
            if not isinstance(config, dict):
                raise ValueError("Task configuration must be a mapping")
            raw_configs[path] = config
            for reference in function_references(config):
                function_count += 1
                match = re.fullmatch(r"utils\.([A-Za-z_]\w*)", reference)
                if not match or match.group(1) not in definitions.get(path.parent / "utils.py", set()):
                    errors.append(f"{path.relative_to(root)}: unresolved !function {reference}")
        except (OSError, ValueError, yaml.YAMLError) as exc:
            errors.append(f"Task {path.relative_to(root)}: {exc}")

    resolved = {}

    def resolve(path, stack=()):
        nonlocal include_links
        if path in stack:
            chain = " -> ".join(str(item.relative_to(root)) for item in (*stack, path))
            raise ValueError(f"Cyclic task includes: {chain}")
        if path in resolved:
            return resolved[path]
        config = raw_configs.get(path)
        if config is None:
            raise ValueError(f"No valid task configuration: {path.relative_to(root)}")
        inherited = {}
        includes = config.get("include", [])
        if isinstance(includes, str):
            includes = [includes]
        if not isinstance(includes, list):
            raise ValueError(f"Invalid include list: {path.relative_to(root)}")
        for include in includes:
            if not isinstance(include, str) or Path(include).is_absolute():
                raise ValueError(f"Invalid include in {path.relative_to(root)}: {include!r}")
            target = (path.parent / include).resolve()
            if target.parent != path.parent or not target.is_file():
                raise ValueError(f"Include must name an existing same-home file: {path.relative_to(root)} -> {include}")
            inherited.update(resolve(target, (*stack, path)))
            include_links += 1
        inherited.update({key: value for key, value in config.items() if key != "include"})
        resolved[path] = inherited
        return inherited

    names = {}
    for path in yaml_paths:
        try:
            config = resolve(path)
            name = config.get("task")
            if not isinstance(name, str) or not name.strip():
                raise ValueError(f"Missing task name after inheritance: {path.relative_to(root)}")
            if name in names:
                raise ValueError(f"Duplicate task name {name}: {names[name].relative_to(root)}, {path.relative_to(root)}")
            names[name] = path
        except ValueError as exc:
            errors.append(str(exc))

    index = git(root, "ls-files", "--stage", "-z")
    gitlinks = []
    tracked_local = []
    root_gitmodules = False
    for record in filter(None, index.split("\0")):
        metadata, path = record.split("\t", 1)
        if metadata.split()[0] == "160000":
            gitlinks.append(path)
        if path == ".local" or path.startswith(".local/"):
            tracked_local.append(path)
        if path == ".gitmodules":
            root_gitmodules = True
    if gitlinks:
        errors.append(f"Tracked gitlinks: {', '.join(gitlinks)}")
    if root_gitmodules:
        errors.append("Root .gitmodules is tracked; archived .gitmodules snapshots are permitted")
    if tracked_local:
        errors.append(f"Tracked .local files: {len(tracked_local)}")
    ignored = all(
        subprocess.run(
            ["git", "-C", str(root), "check-ignore", "--no-index", "-q", path],
            capture_output=True, text=True, check=False,
        ).returncode == 0
        for path in (".local/", ".local/consolidation-check")
    )
    if not ignored:
        errors.append(".local/ is not ignored")

    for section, (checked, total) in counts.items():
        print(f"{section}: {checked}/{total} SHA-256 hashes match")
    print(f"active tasks: {len(names)}/{len(yaml_paths)} unique inherited names; {include_links} include links; {function_count} function references")
    print(f"active utilities: {compiled}/{len(utility_paths)} compiled without execution")
    print(f"Git index: {len(gitlinks)} gitlinks; {int(root_gitmodules)} root submodule files; {len(tracked_local)} tracked .local files; .local ignored={ignored}")
    for error in errors:
        print(f"FAIL: {error}", file=sys.stderr)
    print(f"Consolidation verification: {'FAIL' if errors else 'PASS'} ({len(errors)} errors)")
    return 1 if errors else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent.parent)
    args = parser.parse_args()
    try:
        return verify(args.root.resolve())
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print(f"Consolidation verification: FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
