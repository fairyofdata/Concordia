import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import hygiene  # noqa: E402


def repo(tmp_path, files):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    for name, body in files.items():
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    subprocess.run(["git", "add", "-A", "-f"], cwd=tmp_path, check=True)
    return str(tmp_path)


def levels(found):
    return sorted((lvl, path) for lvl, path, _, _ in found)


def test_clean_repo_has_no_findings(tmp_path):
    root = repo(tmp_path, {"README.md": "# demo\n", "src/app.py": "print('hi')\n", ".env.example": "KEY=\n"})
    assert hygiene.check(root) == []


def test_forbidden_tracked_files_are_errors(tmp_path):
    root = repo(tmp_path, {"state.md": "x\n", "CLAUDE.local.md": "x\n", ".claude/settings.json": "{}\n",
                           "_private/a.md": "x\n", "notes.private.md": "x\n", ".env": "K=1\n", ".env.local": "K=1\n"})
    assert [lvl for lvl, *_ in hygiene.check(root)] == ["error"] * 7


def test_nested_state_md_is_allowed(tmp_path):
    root = repo(tmp_path, {"docs/state.md": "about state machines\n"})
    assert hygiene.check(root) == []


def test_home_paths_are_errors_but_placeholders_are_not(tmp_path):
    root = repo(tmp_path, {
        "a.md": r"see C:\Users\alice\proj" + "\n",
        "b.md": "see /home/bob/proj and /Users/carol/x\n",
        "c.md": r"C:\Users\<you>\proj, /home/runner/work, C:\Users\Public, ~/proj" + "\n",
        "d.md": "C:/Users/erin/proj\n",
    })
    assert levels(hygiene.check(root)) == [("error", "a.md"), ("error", "b.md"), ("error", "d.md")]


def test_project_number_is_warning_and_strict_fails(tmp_path):
    root = repo(tmp_path, {"a.md": "tracked as P-123\n"})
    assert levels(hygiene.check(root)) == [("warning", "a.md")]
    assert hygiene.main(["--root", root]) == 0
    assert hygiene.main(["--root", root, "--strict"]) == 1


def test_allow_file_skips_matching_paths(tmp_path):
    root = repo(tmp_path, {"fixtures/paths.txt": "/home/dave/x\n", ".concordia-allow": "# test data\nfixtures/*\n"})
    assert hygiene.check(root) == []
