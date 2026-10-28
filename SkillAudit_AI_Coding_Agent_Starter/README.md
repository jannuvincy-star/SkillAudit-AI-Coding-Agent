# SkillAudit.ai — AI Coding Agent Internship Project

A local-first Python coding agent using Groq's API. It combines natural-language code generation, subprocess execution with a timeout, a bounded self-correction loop, project context summaries, multi-file edits, diffs, backups, and a dry-run mode.

## Requirements
- Python 3.10+
- A Groq API key from https://console.groq.com/ (free tier availability and limits can change)
- Internet access for Groq API calls

## Setup (Windows PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:GROQ_API_KEY="YOUR_KEY_HERE"
```
Do not commit your API key. If PowerShell blocks activation, run `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` and set the environment variable in that terminal.

## Week 1 — Generate code
```powershell
python agent.py generate --task "Write a function is_prime(n) and print is_prime(7)" --output generated.py
```
Try at least eight tasks covering strings, maths, lists and dictionaries:
1. Reverse a string.
2. Check whether an integer is prime.
3. Compute factorial.
4. Count vowels in a string.
5. Remove duplicates from a list while preserving order.
6. Find the second-largest number in a list.
7. Count word frequencies in a sentence.
8. Merge two dictionaries by adding values for shared keys.

## Week 2 — Execute, observe, self-correct
The generated script runs in a separate Python process with captured output and a timeout; up to three attempts are logged.
```powershell
python agent.py loop --task "Write reverse_text(s), then assert reverse_text('abc') == 'cba' and print PASS" --output reverse.py
```
For a self-correction demo, intentionally request a script with a test assertion that is likely to fail, then show the attempt logs. Model behaviour is nondeterministic, so do not claim a self-correction happened unless the recording actually shows it.

## Week 3 — Multi-file context and edits
```powershell
python agent.py edit --project ./sample_project --task "Update divide so division by zero raises ValueError, and add a unit test for that behaviour" --dry-run
```
Review the diff first. Apply the edit only after inspecting the proposed changes:
```powershell
python agent.py edit --project ./sample_project --task "Update divide so division by zero raises ValueError, and add a unit test for that behaviour"
```
The agent backs up edited files under `sample_project/.agent_backups/before_edit/`.

## Week 4 — CLI portfolio demonstration
```powershell
python agent.py edit --project ./sample_project --task "Fix average() so empty input raises ValueError, and add a unit test for the behaviour" --dry-run
```
Then remove `--dry-run` to apply. Show a genuine bug in the supplied small calculator project, the diff, the tests, and the attempt logs.

## Architecture
1. **Generate**: natural-language task is sent to Groq with a code-only system prompt.
2. **Execute**: candidate code is saved temporarily and launched in a separate Python process.
3. **Observe**: stdout, stderr, return code and timeout are captured and logged.
4. **Correct**: failure context is sent back to the model, up to three attempts.
5. **Project editing**: AST-based Python file summary, project context, JSON edits, unified diffs, backups, and `--dry-run`.

## Safety and limitations
- The timeout and separate process reduce risk but **are not a true security sandbox**. Do not run code against sensitive files or on a machine containing secrets. Use a disposable VM/container with restricted permissions for untrusted code.
- The agent intentionally limits project edits to `.py` files and checks paths to prevent directory traversal.
- This is a learning prototype, not production-ready autonomous software. Review every diff and test result.
- Groq model names, free-tier limits and API availability may change; set `GROQ_MODEL` if the default model is unavailable.

## Suggested demo recording (2–4 minutes)
1. Show `agent.py`, `README.md`, and `sample_project/`.
2. Run Week 1 generation.
3. Run Week 2 loop and show attempt logs. Record only what genuinely occurs.
4. Run Week 3 with `--dry-run`, show the two-file diff, then apply and run tests.
5. Run Week 4 on the empty-list average bug, show the dry-run diff, apply it, and run tests.
6. Show the GitHub repository URL and explain the generate → execute → observe → correct loop.

## Submission checklist
- [ ] Push this project to your GitHub repository.
- [ ] Run at least eight distinct Week 1 tasks and retain terminal screenshots/logs.
- [ ] Run five assertion-based Week 2 tasks; record actual outcomes.
- [ ] Demonstrate a coordinated multi-file edit and successful tests.
- [ ] Record the final end-to-end demo.
- [ ] Paste the GitHub repo and recording links into SkillAudit.ai.
- [ ] Post internship work on LinkedIn and paste the post URL in the relevant submission field.

## Suggested LinkedIn caption
Built a local-first AI Coding Agent with Python and Groq as part of my SkillAudit.ai internship. It generates code from natural-language tasks, executes candidates in a separate process with timeouts, captures failures, retries fixes, and proposes multi-file changes with diffs and backups. I’m continuing to improve the reliability and safety of agentic coding workflows. #SkillAuditInternship #Python #AI #LLM #CodingAgents
