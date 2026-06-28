import json
import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
GITHUB_DIR = ROOT_DIR / ".github"


@pytest.fixture(autouse=True)
def github_package_path():
    """Ensure the local repo and .github agent/skill packages are importable."""
    for path in (str(ROOT_DIR), str(GITHUB_DIR)):
        if path not in sys.path:
            sys.path.insert(0, path)
    yield
    for path in (str(ROOT_DIR), str(GITHUB_DIR)):
        if path in sys.path:
            sys.path.remove(path)


def test_comprehension_agent_analyze_returns_skill_output(monkeypatch):
    import agents.comprehension_agent as comp_mod
    from skills import SkillOutput

    expected = SkillOutput("repo summary", {"files": 1}, ["evidence item"])
    monkeypatch.setattr(comp_mod.analyze_repo_skill, "run", lambda repo_path: expected)

    agent = comp_mod.ComprehensionAgent()
    result = agent.analyze("dummy_repo")

    assert result is expected
    assert result.summary == "repo summary"
    assert result.details["files"] == 1
    assert result.evidence == ["evidence item"]


def test_comprehension_agent_ask_returns_skill_output(monkeypatch):
    import agents.comprehension_agent as comp_mod
    from skills import SkillOutput

    expected = SkillOutput("answer summary", {"answer": "yes"}, ["evidence"])
    monkeypatch.setattr(comp_mod.qna_skill, "run", lambda repo_path, question: expected)

    agent = comp_mod.ComprehensionAgent()
    result = agent.ask("dummy_repo", "What is this?")

    assert result is expected
    assert result.summary == "answer summary"
    assert result.details["answer"] == "yes"


def test_comprehension_agent_analyze_invalid_output_raises(monkeypatch):
    import agents.comprehension_agent as comp_mod

    monkeypatch.setattr(comp_mod.analyze_repo_skill, "run", lambda repo_path: None)

    agent = comp_mod.ComprehensionAgent()
    with pytest.raises(RuntimeError, match="invalid output"):
        agent.analyze("dummy_repo")


def test_architecture_agent_analyze_returns_skill_output(monkeypatch):
    import agents.architecture_agent as arch_mod
    from skills import SkillOutput

    expected = SkillOutput("architecture summary", {"layers": []}, [])
    monkeypatch.setattr(arch_mod.architecture_skill, "run", lambda repo_path: expected)

    agent = arch_mod.ArchitectureAgent()
    result = agent.analyze("dummy_repo")

    assert result.summary == "architecture summary"
    assert result.details["layers"] == []


def test_impact_agent_analyze_returns_skill_output(monkeypatch):
    import agents.impact_agent as impact_mod
    from skills import SkillOutput

    expected = SkillOutput("impact summary", {"affected": ["file.py"]}, ["evidence"])
    monkeypatch.setattr(impact_mod.impact_skill, "run", lambda repo_path, target_file: expected)

    agent = impact_mod.ImpactAgent()
    result = agent.analyze("dummy_repo", "file.py")

    assert result.summary == "impact summary"
    assert result.details["affected"] == ["file.py"]


def test_agent_runner_routes_each_slash_command(monkeypatch, tmp_path):
    import agents.agent_runner as runner_mod
    from skills import SkillOutput

    output_dir = tmp_path / "analysis-results"
    monkeypatch.setattr(runner_mod.AgentRunner, "OUTPUT_DIR", output_dir)

    fake_output = SkillOutput("ok summary", {"value": 42}, ["evidence"])
    monkeypatch.setattr(runner_mod.ComprehensionAgent, "analyze", lambda self, repo_path: fake_output)
    monkeypatch.setattr(runner_mod.ArchitectureAgent, "analyze", lambda self, repo_path: fake_output)
    monkeypatch.setattr(runner_mod.ImpactAgent, "analyze", lambda self, repo_path, target_file: fake_output)
    monkeypatch.setattr(runner_mod.ComprehensionAgent, "ask", lambda self, repo_path, question: fake_output)

    analyze_result = runner_mod.run_agent("/analyze", "dummy_repo")
    assert analyze_result["status"] == "success"
    assert analyze_result["command"] == "analyze"

    architecture_result = runner_mod.run_agent("/architecture", "dummy_repo")
    assert architecture_result["status"] == "success"
    assert architecture_result["command"] == "architecture"

    impact_result = runner_mod.run_agent("/impact", "dummy_repo", "file.py")
    assert impact_result["status"] == "success"
    assert impact_result["command"] == "impact"

    ask_result = runner_mod.run_agent("/ask", "dummy_repo", "What is the repo?")
    assert ask_result["status"] == "success"
    assert ask_result["command"] == "ask"

    output_files = list(output_dir.glob("*.json"))
    assert len(output_files) == 4


def test_agent_runner_returns_error_for_invalid_commands():
    import agents.agent_runner as runner_mod

    result = runner_mod.run_agent("/unknown", "dummy_repo")
    assert result["status"] == "error"
    assert "Unknown command" in result["message"]

    result = runner_mod.run_agent("/impact", "dummy_repo")
    assert result["status"] == "error"
    assert "requires target file" in result["message"]

    result = runner_mod.run_agent("/ask", "dummy_repo")
    assert result["status"] == "error"
    assert "requires a question" in result["message"]


@pytest.mark.parametrize(
    ("argv", "expected_command"),
    [
        (["/analyze", "dummy_repo"], "analyze"),
        (["/architecture", "dummy_repo"], "architecture"),
        (["/impact", "dummy_repo", "file.py"], "impact"),
        (["/ask", "dummy_repo", "What is this?"], "ask"),
    ],
)
def test_cli_main_supports_each_slash_command(monkeypatch, capsys, argv, expected_command):
    import agent_cli

    fake_result = {
        "status": "success",
        "command": expected_command,
        "summary": "ok",
        "details": {},
        "evidence": [],
    }
    monkeypatch.setattr(agent_cli, "run_agent", lambda command, repo_path, *args: fake_result)

    exit_code = agent_cli.main(argv)
    captured = capsys.readouterr()

    assert exit_code == 0
    assert json.loads(captured.out)["command"] == expected_command


def test_core_modules_work_without_backend_dependency(tmp_path):
    from core import build_graph, load_repository, parse_repository

    repo_dir = tmp_path / "sample_repo"
    repo_dir.mkdir()
    (repo_dir / "main.py").write_text(
        "from util import helper\n\n"
        "class Demo:\n"
        "    def run(self):\n"
        "        return helper()\n",
        encoding="utf-8",
    )
    (repo_dir / "util.py").write_text(
        "def helper():\n"
        "    return 2\n",
        encoding="utf-8",
    )

    repo_result = load_repository(str(repo_dir))
    assert repo_result["is_valid"] is True

    parse_result = parse_repository(str(repo_dir))
    assert parse_result["summary"]["total_files"] == 2

    graph_result = build_graph(str(repo_dir))
    assert graph_result["summary"]["total_nodes"] >= 2


def test_impact_skill_traces_dependencies(tmp_path):
    from skills import impact_skill

    repo_dir = tmp_path / "sample_repo"
    repo_dir.mkdir()
    (repo_dir / "main.py").write_text("from util import helper\n", encoding="utf-8")
    (repo_dir / "util.py").write_text("def helper():\n    return 1\n", encoding="utf-8")

    result = impact_skill.run(str(repo_dir), "util.py")

    assert result.summary.startswith("Impact analysis")
    assert result.details["target"] == "util.py"
    assert result.details["impacted_count"] >= 1


def test_documentation_skill_generates_markdown(tmp_path):
    from skills import documentation_skill

    repo_dir = tmp_path / "sample_repo"
    repo_dir.mkdir()
    (repo_dir / "main.py").write_text("def run():\n    return 1\n", encoding="utf-8")

    result = documentation_skill.run(str(repo_dir))

    assert "## Overview" in result.details["markdown"]
    assert "## Architecture" in result.details["markdown"]


def test_build_graph_saves_knowledge_graph(tmp_path):
    from core import build_graph

    repo_dir = tmp_path / "sample_repo"
    repo_dir.mkdir()
    (repo_dir / "main.py").write_text("from util import helper\n", encoding="utf-8")
    (repo_dir / "util.py").write_text("def helper():\n    return 1\n", encoding="utf-8")

    build_graph(str(repo_dir))
    knowledge_graph_path = repo_dir / ".knowledge-graph.json"

    assert knowledge_graph_path.exists()
    data = json.loads(knowledge_graph_path.read_text(encoding="utf-8"))
    assert "nodes" in data
    assert "edges" in data
