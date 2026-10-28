# SkillAudit.ai — AI Coding Agent Internship Project

A local-first Python coding agent built with Groq's API. It accepts natural-language tasks, generates Python code, executes it in a separate process with a timeout, captures execution results, and can attempt bounded self-correction. It also supports project summaries and multi-file Python edits with diffs, backups, and a dry-run mode.

> **Project status:** The calculator sample project's local unit-test suite has passed **7 tests**. Other task evidence should be recorded only after the corresponding tasks have actually been run.

## Features

- Natural-language to Python code generation
- Subprocess execution with captured output and timeout
- Bounded retry/self-correction loop
- Python project context summaries
- Multi-file edits with unified diffs
- Backups before applying edits
- `--dry-run` to inspect proposed changes before applying them

## Requirements

- Python 3.10 or later
- A Groq API key from [Groq Console](https://console.groq.com/)
- Internet access for Groq API calls

Groq model names, API availability, and free-tier limits can change over time.

## Setup — Windows PowerShell

Run these commands from the `SkillAudit_AI_Coding_Agent_Starter` project directory, one at a time:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:GROQ_API_KEY="YOUR_KEY_HERE"
```

Replace `YOUR_KEY_HERE` with your own API key. **Never commit your API key to GitHub.**

If PowerShell blocks virtual-environment activation, install dependencies using:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:GROQ_API_KEY="YOUR_KEY_HERE"
```

Set the API key in the same terminal session in which you run the agent. The configured model can be overridden with the `GROQ_MODEL` environment variable if needed.

## Week 1 — Generate code

Example:

```powershell
python agent.py generate --task "Write a function is_prime(n) and print is_prime(7)" --output generated.py
```

Suggested practice tasks — run each task and retain evidence of the actual output:

1. Reverse a string.
2. Check whether an integer is prime.
3. Compute factorial.
4. Count vowels in a string.
5. Remove duplicates from a list while preserving order.
6. Find the second-largest number in a list.
7. Count word frequencies in a sentence.
8. Merge two dictionaries by adding values for shared keys.

## Week 2 — Execute, observe, and self-correct

Example:

```powershell
python agent.py loop --task "Write reverse_text(s), then assert reverse_text('abc') == 'cba' and print PASS" --output reverse.py
```

The loop runs generated code in a separate Python process, captures execution details, and allows up to three attempts. For a retry demonstration, inspect the attempt logs and report only what actually happened. Model behaviour is nondeterministic, so do not claim that self-correction succeeded unless the logs demonstrate it.

Suggested evidence: five distinct assertion-based tasks, their terminal outputs, and any retry logs.

## Week 3 — Project context and multi-file edits

Start with a dry run:

```powershell
python agent.py edit --project ./sample_project --task "Update divide so division by zero raises ValueError, and add a unit test for that behaviour" --dry-run
```

Inspect the proposed diff. If it is correct, apply the edit by running the same command without `--dry-run`:

```powershell
python agent.py edit --project ./sample_project --task "Update divide so division by zero raises ValueError, and add a unit test for that behaviour"
```

Backups of edited files are stored under `sample_project/.agent_backups/before_edit/`.

## Week 4 — End-to-end CLI demonstration

Use the empty-list average case as an example:

```powershell
python agent.py edit --project ./sample_project --task "Fix average() so empty input raises ValueError, and add a unit test for the behaviour" --dry-run
```

Review the diff first. Remove `--dry-run` to apply the change, then run the test suite.

### Run the calculator tests

From the project directory:

```powershell
python -m unittest discover -s sample_project -p "test_*.py" -v
```

The current local calculator test suite has been run successfully: **7 tests passed**.

## Architecture

1. **Generate:** Send a natural-language task to Groq with a code-generation prompt.
2. **Execute:** Save candidate code and launch it in a separate Python process.
3. **Observe:** Capture standard output, standard error, return code, and timeout status.
4. **Correct:** Provide failure context to the model for a bounded number of retry attempts.
5. **Edit projects:** Summarize Python files, prepare JSON-based edits and unified diffs, create backups, and support `--dry-run`.

## Safety and limitations

- A separate process and timeout can reduce some risks, but **they are not a true security sandbox**.
- Do not run untrusted generated code on a machine containing secrets or sensitive files. Prefer a disposable VM/container with restricted permissions.
- The agent limits project edits to `.py` files and checks paths to help prevent directory traversal.
- This is a learning prototype, not production-ready autonomous software. Review every proposed diff and test result.
- API model names, availability, and usage limits can change. Configure `GROQ_MODEL` when you need to select another supported model.

## Optional demo recording

A demo recording is optional unless the SkillAudit.ai submission instructions explicitly mark it as required.

Suggested 2–4 minute outline:

1. Show `agent.py`, this README, and `sample_project/`.
2. Run a Week 1 generation example.
3. Run a Week 2 loop and show the real attempt logs.
4. Show a Week 3 dry-run diff, apply a reviewed change, and run tests.
5. Show the passing calculator test output.
6. Open the GitHub repository and explain the generate → execute → observe → correct workflow.

Do not show API keys or claim outcomes that were not observed.

## Submission checklist

- [x] Project pushed to GitHub.
- [x] Calculator sample project updated and its 7-test local suite passed.
- [ ] Run at least eight distinct Week 1 tasks and save their outputs.
- [ ] Run five assertion-based Week 2 tasks and save their actual outcomes.
- [ ] Confirm and retain evidence for the required multi-file editing workflow.
- [ ] Submit the GitHub repository link to SkillAudit.ai.
- [ ] Publish the internship work on LinkedIn and submit the post URL if required by the internship instructions.
- [ ] Record an end-to-end demo only if SkillAudit.ai explicitly requires it.

## Suggested LinkedIn caption

Built a local-first AI Coding Agent with Python and Groq as part of my SkillAudit.ai internship. The project explores natural-language code generation, subprocess execution with timeouts, bounded retry attempts, and multi-file edits with diffs and backups. I also verified the calculator sample project's seven unit tests locally. I'm continuing to learn how to make agentic coding workflows more reliable and safer.

#SkillAuditInternship #Python #AI #LLM #CodingAgents
