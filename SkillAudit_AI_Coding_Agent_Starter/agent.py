"""Local AI coding agent: generate -> execute -> observe -> correct."""
import argparse, ast, difflib, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

SYSTEM = """You are a careful Python coding assistant.
Return ONLY the requested Python code or, when asked to edit project files, ONLY valid JSON
with this schema: {"files":{"relative/path.py":"complete updated file content"},"notes":"short summary"}.
Never use markdown fences. Do not delete unrelated code. Keep changes minimal.
For code-generation tasks, include the requested function and any assertions supplied by the user.
For project edits, only return files that should change. Never use absolute paths.
"""

def clean_code(s):
    s = s.strip()
    s = re.sub(r"^```(?:python)?\s*", "", s)
    s = re.sub(r"\s*```$", "", s)
    return s.strip() + "\n"

def groq_chat(messages, model=None):
    try:
        from groq import Groq
    except ImportError as e:
        raise RuntimeError("Install dependencies first: pip install -r requirements.txt") from e
    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError("Set GROQ_API_KEY with your Groq API key, then retry.")
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    response = client.chat.completions.create(
        model=model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        messages=messages, temperature=0.1
    )
    return response.choices[0].message.content or ""

def run_python(code, timeout=8, cwd=None):
    """Run code in a separate Python process with a timeout; this is not an OS-level sandbox."""
    with tempfile.TemporaryDirectory(prefix="sa_agent_") as td:
        script = Path(td) / "candidate.py"
        script.write_text(code, encoding="utf-8")
        try:
            p = subprocess.run(
                [sys.executable, "-I", str(script)], cwd=cwd or td,
                capture_output=True, text=True, timeout=timeout,
                env={"PATH": os.environ.get("PATH", ""), "PYTHONIOENCODING": "utf-8"}
            )
            return {"returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr, "passed": p.returncode == 0}
        except subprocess.TimeoutExpired as e:
            return {"returncode": -1, "stdout": e.stdout or "", "stderr": (e.stderr or "") + "\nTIMEOUT", "passed": False}

def ask_code(task, model=None):
    raw = groq_chat([
        {"role":"system","content":SYSTEM},
        {"role":"user","content":"Generate a complete Python script for this task. Print useful output. Task:\n"+task}
    ], model)
    code = clean_code(raw)
    ast.parse(code)
    return code

def generate_mode(task, output, model=None):
    code = ask_code(task, model)
    Path(output).write_text(code, encoding="utf-8")
    print("----- GENERATED CODE -----")
    print(code)
    print(f"Saved: {output}")

def loop_mode(task, output, model=None, attempts=3, timeout=8):
    code = ask_code(task, model)
    for i in range(1, attempts+1):
        print(f"\n===== ATTEMPT {i}/{attempts} =====\n{code}")
        result = run_python(code, timeout=timeout)
        print("RESULT:", json.dumps(result, ensure_ascii=False, indent=2))
        if result["passed"]:
            Path(output).write_text(code, encoding="utf-8")
            print(f"PASS. Saved: {output}")
            return True
        if i < attempts:
            code = clean_code(groq_chat([
                {"role":"system","content":SYSTEM},
                {"role":"user","content":f"The following generated Python script failed. Fix it and return ONLY the complete corrected Python script.\nTASK:\n{task}\nCODE:\n{code}\nRETURN CODE: {result['returncode']}\nSTDOUT:\n{result['stdout']}\nSTDERR:\n{result['stderr']}"}
            ], model))
            ast.parse(code)
    print("FAILED after maximum attempts; no final file saved.")
    return False

def summarize_project(project):
    lines = []
    for p in sorted(Path(project).rglob("*.py")):
        if any(part in {".git", ".venv", "venv", "__pycache__"} for part in p.parts):
            continue
        try:
            source = p.read_text(encoding="utf-8")
            tree = ast.parse(source)
            names = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    names.append(f"{type(node).__name__} {node.name} (line {node.lineno})")
            rel = p.relative_to(project).as_posix()
            lines.append(f"{rel}: {', '.join(names) or 'module-level code'}")
        except Exception as e:
            lines.append(f"{p.relative_to(project).as_posix()}: unable to parse ({e})")
    return "\n".join(lines) or "(No Python files found.)"

def safe_relative(project, name):
    p = (Path(project) / name).resolve()
    base = Path(project).resolve()
    if p != base and base not in p.parents:
        raise ValueError(f"Refusing path outside project: {name}")
    return p

def edit_project(project, task, model=None, dry_run=False, timeout=15):
    project = Path(project).resolve()
    context = summarize_project(project)
    snippets = {}
    for p in project.rglob("*.py"):
        if any(part in {".git", ".venv", "venv", "__pycache__"} for part in p.parts):
            continue
        try:
            rel = p.relative_to(project).as_posix()
            snippets[rel] = p.read_text(encoding="utf-8")
        except OSError:
            pass
    prompt = (
        "Modify this small Python project to fulfil the task. Return ONLY valid JSON in schema "
        '{"files":{"relative/path.py":"complete updated content"},"notes":"summary"}. '
        "Only include files to change. Keep unrelated content. No markdown.\n"
        f"TASK:\n{task}\n\nPROJECT SUMMARY:\n{context}\n\nPROJECT FILES:\n"
        + json.dumps(snippets, ensure_ascii=False)
    )
    raw = groq_chat([{"role":"system","content":SYSTEM},{"role":"user","content":prompt}], model)
    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    raw = re.sub(r"\s*```$", "", raw)
    plan = json.loads(raw)
    changes = plan.get("files", {})
    if not changes:
        raise RuntimeError("Model returned no file changes.")
    old = {}
    new = {}
    for name, content in changes.items():
        target = safe_relative(project, name)
        if not target.suffix == ".py":
            raise ValueError("Only .py file edits are allowed in this demo agent.")
        old[name] = target.read_text(encoding="utf-8") if target.exists() else ""
        ast.parse(content) if target.suffix == ".py" else None
        new[name] = content
    for name in new:
        print(f"\n===== DIFF: {name} =====")
        print("".join(difflib.unified_diff(old[name].splitlines(True), new[name].splitlines(True),
              fromfile=f"a/{name}", tofile=f"b/{name}")))
    if dry_run:
        print("\nDRY RUN: no files changed.")
        return True
    # Back up before edits.
    backup = project / ".agent_backups" / "before_edit"
    backup.mkdir(parents=True, exist_ok=True)
    for name, content in old.items():
        bp = backup / name
        bp.parent.mkdir(parents=True, exist_ok=True)
        bp.write_text(content, encoding="utf-8")
    for name, content in new.items():
        target = safe_relative(project, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    tests = sorted(project.rglob("test_*.py"))
    if tests:
        test_file = tests[0]
        result = subprocess.run([sys.executable, str(test_file)], cwd=str(project),
                                capture_output=True, text=True, timeout=timeout)
        print("TEST RESULT:", result.stdout, result.stderr, "returncode=", result.returncode)
        if result.returncode:
            print("Tests failed. Original files are backed up in .agent_backups/before_edit.")
            return False
    else:
        print("No test_*.py file found; run the project's tests manually.")
    print("Project edit applied. Review the diff and run all project tests.")
    return True

def main():
    ap = argparse.ArgumentParser(description="SkillAudit AI Coding Agent")
    sub = ap.add_subparsers(dest="command", required=True)
    g = sub.add_parser("generate", help="Week 1: natural-language-to-code")
    g.add_argument("--task", required=True); g.add_argument("--output", default="generated.py"); g.add_argument("--model")
    l = sub.add_parser("loop", help="Week 2: execute and self-correct")
    l.add_argument("--task", required=True); l.add_argument("--output", default="generated.py"); l.add_argument("--model")
    l.add_argument("--attempts", type=int, choices=[1,2,3], default=3); l.add_argument("--timeout", type=int, default=8)
    e = sub.add_parser("edit", help="Weeks 3-4: multi-file project editing")
    e.add_argument("--project", required=True); e.add_argument("--task", required=True); e.add_argument("--model")
    e.add_argument("--dry-run", action="store_true"); e.add_argument("--timeout", type=int, default=15)
    args = ap.parse_args()
    try:
        if args.command == "generate": generate_mode(args.task, args.output, args.model)
        elif args.command == "loop": loop_mode(args.task, args.output, args.model, args.attempts, args.timeout)
        else: edit_project(args.project, args.task, args.model, args.dry_run, args.timeout)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr); sys.exit(1)

if __name__ == "__main__":
    main()
