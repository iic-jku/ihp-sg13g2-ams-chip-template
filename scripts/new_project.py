# SPDX-FileCopyrightText: 2026 Simon Dorrer and Harald Pretl
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
#
# Starts a new chip from this template, called by `make project NAME=<name> [DRY_RUN=1] [FORCE=1]`.
# Every change is planned in memory first. Only a plan that passed every check runs `make clean` and writes to the tree.
# The script deletes itself at the end, a derived chip has no use for it.

import argparse
import os
import posixpath
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

# ------------------------------------------------------------------------------------------------
# Per-template data, the only part that differs between the template instances
# ------------------------------------------------------------------------------------------------

# Deleted together with everything below them
TEMPLATE_ONLY_PATHS = ["tutorial", ".github/workflows/quarto-publish.yml", "doc/ihp-structure-proposals", "CITATION.cff"]

# Emptied, the folder itself stays because `make release` writes into it
TEMPLATE_ONLY_CONTENTS = ["release"]

# Replaced by a fresh file
EMPTIED_FILES = {"ToDo.md": "# ToDo List\n"}

# Files that put the template's identity on the die
IDENTITY_FILES = [
    ("ip/sg13g2_ip__jku_names/logo/jku_names.png", "the names of the template authors"),
    ("flow/logo/chip_logo_mono.png", "the AMS CHIP artwork, drawn on TopMetal2"),
    ("ip/sg13g2_ip__jku/logo/jku_logo.png", "the JKU logo"),
]

NEXT_STEPS = [
    "flow/librelane/config.yaml: DIE_AREA, the pad ring and the MACROS placements",
    "packaging/config.yaml: the PINOUT map",
    "doc/specifications.md, doc/pinout.md, doc/floorplan.md and the description in README.md",
    "the regression target in the Makefile tests the counter and inverter macros, point it at your own macros once you replace them",
]

# Recommended name of the repository and its folder: REPO_PREFIX + NAME
REPO_PREFIX = "ihp-sg13g2-"

# ------------------------------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
SELF = Path(__file__).resolve().relative_to(ROOT).as_posix()
OLD = "chip"
SUFFIXES = ("_top", "_core", "_logo")
FIG_DIR = "doc/fig"

NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")
BEGIN_RE = re.compile(r"^\s*(?:#|<!--)\s*template-only\b")
END_RE = re.compile(r"^\s*(?:#|<!--)\s*/template-only\b")
PROSE_RE = re.compile(r"\b(?:chip (?:design )?template|template chip)\b", re.IGNORECASE)
TREE_RE = re.compile(r"^((?:│  |   )*)(├─ |└─ )(.*)$")
DIR_ICON = "📁 "
PROSE_MAX_BYTES = 1_000_000  # the prose scan skips larger files (netlists, Liberty)
MAX_HITS = 5                 # problems listed per file and kind


class Refused(Exception):
    """A check failed before anything was changed."""


class Plan:
    pass


# Helpers ----------------------------------------------------------------------------------------

def git(*args):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    return r.stdout.decode("utf-8", "replace").strip() if r.returncode == 0 else None


def under(path, roots):
    return any(path == r or path.startswith(r + "/") for r in roots)


def in_contents(path):
    return any(path.startswith(r + "/") for r in TEMPLATE_ONLY_CONTENTS)


def read_text(path):
    """Returns (bom, text) of a UTF-8 text file, None for a binary or non-UTF-8 file."""
    with open(ROOT / path, "rb") as fh:
        data = fh.read(8192)
        if b"\0" in data:
            return None
        data += fh.read()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return None
    return (True, text[1:]) if text.startswith("﻿") else (False, text)


def write_text(path, bom, text):
    (ROOT / path).write_bytes((("﻿" if bom else "") + text).encode("utf-8"))


def newline_of(text):
    return "\r\n" if "\r\n" in text else "\n"


def line_at(text, pos):
    return text.count("\n", 0, pos) + 1


def alternation(words):
    return "|".join(re.escape(w) for w in sorted(words, key=len, reverse=True))


def ref_pattern(ref, is_dir=False):
    """A relative path as a link target: not part of a longer path or a URL."""
    return re.compile(r"(?<![\w./-])" + re.escape(ref) + ("/" if is_dir else r"(?![\w.-])"))


def link_pattern(ref):
    """A relative path as the target of a Markdown or HTML link or image."""
    return re.compile(r"(?:\]\(|(?:src|href)=[\"'])" + re.escape(ref) + r"(?=[)\"'#?\s])")


def relpath(path, start_file):
    return posixpath.relpath(path, posixpath.dirname(start_file) or ".")


def repo_id(url):
    url = re.sub(r"^[a-z+]+://", "", url.strip().lower())
    url = re.sub(r"^[^@/]+@", "", url)
    host = url.split("/", 1)[0]
    if ":" in host:
        url = url.replace(":", "/", 1)
    return re.sub(r"(\.git)?/*$", "", url)


def remove(path):
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    elif path.exists() or path.is_symlink():
        path.unlink()


def prune_empty(folder):
    while folder and (ROOT / folder).is_dir() and not any((ROOT / folder).iterdir()):
        (ROOT / folder).rmdir()
        folder = posixpath.dirname(folder)


# Checks -----------------------------------------------------------------------------------------

def check_name(args):
    name = args.name.strip()
    if args.name_origin == "environment":
        raise Refused(f"NAME={name} comes from the environment. Pass it on the command line: make project NAME=<name>.")
    if not name:
        raise Refused("Set NAME to the name of the new chip: make project NAME=<name>.")
    if not NAME_RE.match(name):
        raise Refused(f"NAME '{name}' must be a lowercase letter followed by lowercase letters, digits or underscores.")
    if name == OLD:
        raise Refused(f"NAME must differ from '{OLD}'.")
    for folder in ("macros", "ip"):
        if (ROOT / folder / name).exists():
            raise Refused(f"NAME '{name}' is taken by {folder}/{name}/, its top cell would clash with the chip. Pick another NAME.")
    return name


def check_top():
    m = re.search(r"^TOP\s*[:?]?=\s*(\S+)", (ROOT / "Makefile").read_text(encoding="utf-8"), re.M)
    top = m.group(1) if m else None
    if top != OLD + "_top":
        raise Refused(f"TOP in the Makefile is {top or 'not set'}, but make project only runs on the template (TOP = {OLD}_top).")


def template_info():
    url = version = None
    cff = ROOT / "CITATION.cff"
    if cff.is_file():
        text = cff.read_text(encoding="utf-8")
        m = re.search(r"^url:\s*['\"]?([^'\"\s]+)", text, re.M)
        url = m.group(1) if m else None
        m = re.search(r"^version:\s*['\"]?([^'\"\s]+)", text, re.M)
        version = m.group(1) if m else None
    # A repository made with "Use this template" has no tags, so CITATION.cff is the fallback
    version = git("describe", "--tags") or version or "unknown version"
    slug = url.rstrip("/").rsplit("/", 1)[-1] if url else "the template"
    return slug, url, version


def git_checks(args, plan):
    issues = []
    if git("rev-parse", "--is-inside-work-tree") != "true":
        issues.append("This folder is not a git checkout, so nothing can undo the changes.")
    else:
        status = git("status", "--porcelain", "--ignore-submodules=all")
        if status:
            lines = status.splitlines()
            listing = "\n".join("  " + line for line in lines[:10]) + ("\n  ..." if len(lines) > 10 else "")
            issues.append("The git tree has uncommitted changes. Commit or stash them first, so that git can undo this run:\n" + listing)
        origin = git("remote", "get-url", "origin")
        if origin and plan.url and repo_id(origin) == repo_id(plan.url):
            issues.append(f"origin is the template itself ({origin}). Create your own repository from the template first.")
    if issues and not args.force and not args.dry_run:
        raise Refused("\n".join(issues) + "\nFORCE=1 skips these checks.")
    plan.warnings += issues


def list_files():
    if git("rev-parse", "--is-inside-work-tree") == "true":
        out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True).stdout
        files = [f for f in out.decode("utf-8").split("\0") if f]
    else:
        files = []
        for folder, dirs, names in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d != ".git"]
            files += [Path(folder, n).relative_to(ROOT).as_posix() for n in names]
    return sorted(f for f in files if (ROOT / f).is_file() and not (ROOT / f).is_symlink())


def clean_paths():
    """The paths `make clean` deletes, read from its dry run, so that the plan can leave them out."""
    r = subprocess.run(["make", "--no-print-directory", "-n", "clean"], cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        raise Refused("make -n clean failed:\n" + r.stderr.strip())
    paths = []
    for line in r.stdout.splitlines():
        try:
            words = shlex.split(line)
        except ValueError:
            continue
        if words and words[0] == "rm":
            paths += [posixpath.normpath(w) for w in words[1:] if not w.startswith("-")]
    return paths


# Edits ------------------------------------------------------------------------------------------

def strip_blocks(text, path):
    if "template-only" not in text:
        return text, 0
    out, start, count = [], None, 0
    for number, line in enumerate(text.splitlines(keepends=True), 1):
        if BEGIN_RE.match(line):
            if start:
                raise Refused(f"{path}:{number}: a template-only block opens inside the one opened in line {start}.")
            start, count = number, count + 1
        elif END_RE.match(line):
            if not start:
                raise Refused(f"{path}:{number}: /template-only closes no open block.")
            start = None
        elif not start:
            out.append(line)
    if start:
        raise Refused(f"{path}:{start}: this template-only block is never closed.")
    return "".join(out), count


def rescue(text, deleted):
    """Moves the deleted files that a kept file still links to into FIG_DIR and rewrites the links."""
    roots = TEMPLATE_ONLY_PATHS + TEMPLATE_ONLY_CONTENTS
    keys = {posixpath.basename(r) for r in roots}
    linked = set()
    for f, t in text.items():
        if any(k in t for k in keys):
            linked |= {p for p in deleted if link_pattern(relpath(p, f)).search(t)}
    moves = {}
    for p in sorted(linked):
        parent = posixpath.dirname(p)
        if posixpath.basename(parent) == posixpath.splitext(posixpath.basename(p))[0] and parent not in roots:
            # A figure folder fig/<name>/<name>.<ext> moves as a whole, with its sources
            for q in deleted:
                if q.startswith(parent + "/"):
                    moves[q] = posixpath.join(FIG_DIR, posixpath.basename(parent), posixpath.relpath(q, parent))
        else:
            moves[p] = posixpath.join(FIG_DIR, posixpath.basename(p))
    for f in text:
        for old, new in moves.items():
            if posixpath.basename(old) in text[f]:
                target = relpath(new, f)
                text[f] = ref_pattern(relpath(old, f)).sub(lambda _: target, text[f])
    return moves


def parse_tree(lines):
    root = {"name": "", "label": lines[0], "children": []}
    stack = [root]
    for line in lines[1:]:
        m = TREE_RE.match(line)
        depth = len(m.group(1)) // 3 if m else len(stack)
        if not m or depth >= len(stack):
            return None
        label = m.group(3)
        name = label[len(DIR_ICON):].rstrip("/") if label.startswith(DIR_ICON) else label
        node = {"name": name, "label": label, "children": []}
        del stack[depth + 1:]
        stack[depth]["children"].append(node)
        stack.append(node)
    return root


def render_tree(root):
    lines = [root["label"]]

    def walk(node, prefix):
        for i, child in enumerate(node["children"]):
            last = i == len(node["children"]) - 1
            lines.append(prefix + ("└─ " if last else "├─ ") + child["label"])
            walk(child, prefix + ("   " if last else "│  "))

    walk(root, "")
    return lines


def prune_tree(node, prefix=""):
    kept = []
    for child in node["children"]:
        path = prefix + child["name"]
        if under(path, TEMPLATE_ONLY_PATHS + [SELF]):
            continue
        if path in TEMPLATE_ONLY_CONTENTS:
            child["children"] = []
        prune_tree(child, path + "/")
        kept.append(child)
    node["children"] = kept


def add_tree_dir(root, path):
    node, parts = root, path.split("/")
    for depth, part in enumerate(parts):
        match = next((c for c in node["children"] if c["name"] == part), None)
        if match is None:
            if depth < len(parts) - 1:
                return
            dirs = [c for c in node["children"] if c["label"].startswith(DIR_ICON)]
            pos = next((i for i, c in enumerate(dirs) if c["name"].lower() > part.lower()), len(dirs))
            node["children"].insert(pos, {"name": part, "label": DIR_ICON + part + "/", "children": []})
            return
        node = match


def sort_renamed(node, rename):
    """Re-sorts the folders whose entries get renamed: folders first, then files, each case-insensitively."""
    if any(rename(c["name"]) != c["name"] for c in node["children"]):
        node["children"].sort(key=lambda c: (not c["label"].startswith(DIR_ICON), rename(c["name"]).lower()))
    for child in node["children"]:
        sort_renamed(child, rename)


def edit_readme(text, plan, rename):
    lines = text.splitlines(keepends=True)
    bare = [line.rstrip("\r\n") for line in lines]
    start = next((i for i, line in enumerate(bare[:-1]) if line.strip() == "```text" and bare[i + 1].startswith(DIR_ICON)), None)
    end = next((i for i in range(start + 1, len(bare)) if bare[i].strip() == "```"), None) if start is not None else None
    tree = parse_tree(bare[start + 1:end]) if end else None
    if tree is None or render_tree(tree) != bare[start + 1:end]:
        plan.warnings.append("README.md: the directory tree has an unexpected format and was left as it is, update it by hand.")
    else:
        prune_tree(tree)
        if any(new.startswith(FIG_DIR + "/") for new in plan.moves.values()):
            add_tree_dir(tree, FIG_DIR)
        sort_renamed(tree, rename)
        tree["label"] = DIR_ICON + ROOT.name + "/"
        eol = lines[start + 1][len(bare[start + 1]):] or "\n"
        lines[start + 1:end] = [line + eol for line in render_tree(tree)]
    nl = newline_of(text)
    link = f"[{plan.slug}]({plan.url})" if plan.url else plan.slug
    header = (f"# {plan.name}{nl}{nl}Started from {link} `{plan.version}` with `make project`.{nl}{nl}"
              f"TODO: describe the chip, its main specifications and its status.{nl}{nl}")
    return header + "".join(lines)


# Plan -------------------------------------------------------------------------------------------

def make_plan(args):
    plan = Plan()
    plan.name = check_name(args)
    check_top()
    plan.slug, plan.url, plan.version = template_info()
    plan.warnings = []
    git_checks(args, plan)

    pairs = {}
    for suffix in SUFFIXES:
        pairs[OLD + suffix] = plan.name + suffix
        pairs[(OLD + suffix).upper()] = (plan.name + suffix).upper()
    plan.pairs = pairs
    token_re = re.compile(alternation(pairs))

    def rename(s):
        return token_re.sub(lambda m: pairs[m.group(0)], s)

    taken_re = re.compile(r"(?<![A-Za-z0-9])(?:" + alternation(pairs.values()) + ")")

    files = list_files()
    plan.clean = clean_paths()
    plan.cleaned = [f for f in files if under(f, plan.clean)]
    files = [f for f in files if not under(f, plan.clean)]
    plan.deleted = [f for f in files if under(f, TEMPLATE_ONLY_PATHS) or in_contents(f)]
    deleted = set(plan.deleted)
    kept = [f for f in files if f not in deleted and f != SELF]

    original, bom = {}, set()
    for f in kept:
        content = read_text(f)
        if content:
            bom |= {f} if content[0] else set()
            original[f] = content[1]
    text = dict(original)

    plan.blocks = {}
    for f in text:
        text[f], count = strip_blocks(text[f], f)
        if count:
            plan.blocks[f] = count

    # Checked after the template-only blocks are gone, text that is about to be deleted cannot block a name
    for f in kept:
        m = taken_re.search(f) or (taken_re.search(text[f]) if f in text else None)
        if m:
            raise Refused(f"'{m.group(0)}' appears in {f} already, the rename would merge two names. Pick another NAME.")

    plan.moves = rescue(text, plan.deleted)
    plan.deleted = [f for f in plan.deleted if f not in plan.moves]
    for old in plan.moves:
        kept.append(old)
        content = read_text(old)
        if content:
            bom |= {old} if content[0] else set()
            original[old] = text[old] = content[1]

    if "README.md" in text:
        text["README.md"] = edit_readme(text["README.md"], plan, rename)
    plan.emptied = [f for f in EMPTIED_FILES if f in text]
    for f in plan.emptied:
        text[f] = EMPTIED_FILES[f].replace("\n", newline_of(original[f]))

    plan.dst, plan.replaced = {}, {}
    for f in kept:
        plan.dst[f] = rename(plan.moves.get(f, f))
        if f in text:
            count = len(token_re.findall(text[f]))
            if count:
                plan.replaced[f] = count
                text[f] = rename(text[f])
    sources = {}
    for src, dst in plan.dst.items():
        if dst in sources:
            raise Refused(f"{sources[dst]} and {src} would both become {dst}.")
        sources[dst] = src
        if dst != src and (ROOT / dst).exists() and plan.dst.get(dst, dst) == dst and not under(dst, plan.clean):
            raise Refused(f"{src} would overwrite {dst}.")
    plan.data = {f: (f in bom, text[f]) for f in text if text[f] != original[f]}
    plan.text = {plan.dst[f]: t for f, t in text.items()}
    return plan


# Apply and check --------------------------------------------------------------------------------

def apply(plan):
    print("Running make clean ...")
    if subprocess.run(["make", "--no-print-directory", "clean"], cwd=ROOT, stdout=subprocess.DEVNULL).returncode:
        sys.exit("make project: make clean failed, nothing else was changed.")
    lost = [f for f in plan.dst if not (ROOT / f).exists()]
    if lost:
        sys.exit("make project: make clean deleted files the plan keeps, nothing else was changed:\n" + "\n".join("  " + f for f in lost))
    for src, dst in plan.dst.items():
        data = plan.data.get(src)
        if src == dst:
            if data:
                write_text(src, *data)
            continue
        (ROOT / dst).parent.mkdir(parents=True, exist_ok=True)
        if data:
            write_text(dst, *data)
            shutil.copymode(ROOT / src, ROOT / dst)
            (ROOT / src).unlink()
        else:
            os.replace(ROOT / src, ROOT / dst)
        prune_empty(posixpath.dirname(src))
    for path in TEMPLATE_ONLY_PATHS:
        remove(ROOT / path)
    for path in TEMPLATE_ONLY_CONTENTS:
        if (ROOT / path).is_dir():
            for child in (ROOT / path).iterdir():
                remove(child)
    (ROOT / SELF).unlink()


def deleted_refs(plan):
    refs = {(f, False) for f in plan.deleted} | {(f, False) for f in plan.moves} | {(SELF, False)}
    for f in plan.deleted:
        folder = posixpath.dirname(f)
        while folder and folder not in TEMPLATE_ONLY_CONTENTS and under(folder, TEMPLATE_ONLY_PATHS + TEMPLATE_ONLY_CONTENTS):
            refs.add((folder, True))
            folder = posixpath.dirname(folder)
    return sorted(refs)


def self_check(plan):
    problems = []
    new_re = re.compile(alternation(plan.pairs.values()))
    old_re = re.compile(alternation(plan.pairs))
    refs = deleted_refs(plan)
    keys = {posixpath.basename(path) for path, _ in refs}
    for path in sorted(set(plan.dst.values())):
        if old_re.search(new_re.sub("\0", path)):
            problems.append(f"{path}: the file name still carries an old name")
        content = read_text(path) if (ROOT / path).is_file() else None
        if content is None:
            continue
        text = content[1]
        masked = new_re.sub("\0", text)
        hits = [f"{path}:{line_at(masked, m.start())}: {m.group(0)} is left" for m in old_re.finditer(masked)]
        if any(k in text for k in keys):
            for ref, is_dir in refs:
                pattern = ref_pattern(relpath(ref, path), is_dir)
                hits += [f"{path}:{line_at(text, m.start())}: links to the deleted {ref}{'/' if is_dir else ''}" for m in pattern.finditer(text)]
        for number, line in enumerate(text.splitlines(), 1):
            if BEGIN_RE.match(line) or END_RE.match(line):
                hits.append(f"{path}:{number}: a template-only marker is left")
        problems += hits[:MAX_HITS] + ([f"{path}: {len(hits) - MAX_HITS} more"] if len(hits) > MAX_HITS else [])
    if shutil.which("reuse"):
        r = subprocess.run(["reuse", "lint"], cwd=ROOT, capture_output=True, text=True)
        plan.reuse = "passed" if r.returncode == 0 else "failed"
        if r.returncode:
            problems.append("reuse lint failed:\n" + "\n".join("    " + line for line in r.stdout.strip().splitlines()[-30:]))
    else:
        plan.reuse = "not installed here, the License Check workflow runs it in CI"
    return problems


# Report -----------------------------------------------------------------------------------------

def summary(plan):
    rows = [("make clean", f"{len(plan.cleaned)} tracked outputs of {OLD}_top")]
    if plan.blocks:
        rows.append(("template-only blocks", f"{sum(plan.blocks.values())} in {len(plan.blocks)} files: "
                     + ", ".join(f"{f} ({n})" for f, n in sorted(plan.blocks.items()))))
    parts = []
    for root in TEMPLATE_ONLY_PATHS:
        if any(under(f, [root]) for f in plan.deleted):
            parts.append(root + ("/" if any(f.startswith(root + "/") for f in plan.deleted) else ""))
    for root in TEMPLATE_ONLY_CONTENTS:
        if any(f.startswith(root + "/") for f in plan.deleted):
            parts.append(f"the content of {root}/")
    rows.append(("deleted", f"{len(plan.deleted)} files: " + ", ".join(parts)))
    if plan.moves:
        folders = sorted({posixpath.dirname(new) for new in plan.moves.values()})
        rows.append((f"moved to {FIG_DIR}/", f"{len(plan.moves)} files still linked from kept files: " + ", ".join(f + "/" for f in folders)))
    renamed = [src for src, dst in plan.dst.items() if dst != plan.moves.get(src, src)]
    rows.append(("renamed", f"{len(renamed)} files"))
    rows.append(("names replaced", f"{sum(plan.replaced.values())} in {len(plan.replaced)} files"))
    if plan.emptied:
        rows.append(("emptied", ", ".join(plan.emptied)))
    rows.append(("removed itself", f"{SELF} and the project target"))
    width = max(len(k) for k, _ in rows)
    return "\n".join(f"  {k.ljust(width)}  {v}" for k, v in rows)


def prose_lines(plan):
    hits = []
    for path, text in sorted(plan.text.items()):
        if len(text) <= PROSE_MAX_BYTES:
            hits += [f"{path}:{n}" for n, line in enumerate(text.splitlines(), 1) if PROSE_RE.search(line)]
    return hits


def folder_hint(plan, dry_run):
    """The steps to rename the repository and its folder to REPO_PREFIX + NAME, empty when the folder has that name."""
    want = REPO_PREFIX + plan.name
    if ROOT.name == want:
        return []
    origin = git("remote", "get-url", "origin")
    steps = []
    if origin and plan.url and repo_id(origin) == repo_id(plan.url):
        steps.append(f"create your own repository {want} from the template and point origin at it: git remote set-url origin <its URL>")
    elif origin:
        steps.append(f"rename the remote repository to {want} as well (on GitHub: Settings > General, the old URLs redirect)")
        steps.append("git remote set-url origin " + re.sub(r"[^/:]+?(\.git)?/*$", lambda m: want + (m.group(1) or ""), origin))
    # Windows refuses to rename a folder that a program has open
    steps.append(f"close VS Code and every terminal in the folder, then in its parent folder: mv {ROOT.name} {want}")
    if not dry_run:
        steps.append(f"change the root line of the directory tree in README.md to {DIR_ICON}{want}/")
    intro = f"The folder is {ROOT.name}, the recommended name is {want}. " + (
        "Rename it before the real run, then the directory tree in README.md gets the new name as well:" if dry_run else "To rename it:")
    return [intro] + [f"  {i}. {step}" for i, step in enumerate(steps, 1)]


def report(plan, problems=None, dry_run=False):
    print(f"\nmake project: {plan.name} from {plan.slug} {plan.version}" + (" (dry run, nothing was changed)" if dry_run else ""))
    for warning in plan.warnings:
        print("\nWarning: " + warning)
    print("\n" + summary(plan))
    if dry_run:
        print("\nFiles that get a new name:")
        for src, dst in sorted(plan.dst.items()):
            if src != dst:
                print(f"  {src} -> {dst}")
        print("\nOld names replaced per file:")
        for f, n in sorted(plan.replaced.items()):
            print(f"  {n:5d}  {f}")
    else:
        if problems:
            print(f"\nThe self-check found {len(problems)} problems:")
            print("\n".join("  " + p for p in problems))
            print("\nThe tree is changed. Fix the problems by hand, or undo everything with: git reset --hard && git clean -fd")
        else:
            print("\nSelf-check passed: no old name, no link into a deleted path and no marker is left.")
        print(f"reuse lint: {plan.reuse}.")
    identity = [(plan.dst.get(f, f), what) for f, what in IDENTITY_FILES if (ROOT / f).exists() or f in plan.dst]
    if identity:
        width = max(len(f) for f, _ in identity)
        print("\nReplace these before a tapeout, they put the template's identity on the die:")
        print("\n".join(f"  {f.ljust(width)}  {what}" for f, what in identity))
    prose = prose_lines(plan)
    if prose:
        print("\nLines that still call the chip a template, rewrite them where they no longer fit"
              + (" (line numbers of the result):" if dry_run else ":"))
        print("\n".join("  " + hit for hit in prose))
    hint = folder_hint(plan, dry_run)
    if hint:
        print("\n" + "\n".join(hint))
    if not dry_run:
        print("\nNext steps:")
        print("\n".join("  - " + step for step in NEXT_STEPS))
        print("  - review the result with git status and git diff, undo everything with: git reset --hard && git clean -fd")
        print(f"  - commit it: git add -A && git commit -m \"started {plan.name} from {plan.slug}\"")
        print("  - build the chip: make init-submodules, then make build-top (or make all, which also fetches the submodule)")


def main():
    parser = argparse.ArgumentParser(description="Start a new chip from this template.")
    parser.add_argument("--name", default="")
    parser.add_argument("--name-origin", default="command line")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        plan = make_plan(args)
    except Refused as e:
        print(f"make project: {e}\nNothing was changed.", file=sys.stderr)
        return 1
    if args.dry_run:
        report(plan, dry_run=True)
        return 0
    apply(plan)
    problems = self_check(plan)
    report(plan, problems)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
