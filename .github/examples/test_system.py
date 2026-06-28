"""
Example: Test the Agent System

This script demonstrates all components of the Agent + Skill system.
Run this to verify everything is working.

Usage:
    python -m .github.agents.examples.test_system
    
Or from Python:
    from .github.agents.examples import test_system
    test_system.run()
"""

import sys
import json
from pathlib import Path

# Get the workspace root (Capstone 2 folder)
workspace_root = Path(__file__).parent.parent.parent.parent
backend_path = workspace_root / "backend"

# Add paths to sys.path
for path in [str(backend_path), str(workspace_root), str(backend_path / "app")]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Ensure agents is in path
agent_path = Path(__file__).parent.parent
if str(agent_path) not in sys.path:
    sys.path.insert(0, str(agent_path))


def test_core_functions():
    """Test core engine functions."""
    print("\n" + "=" * 60)
    print("TEST 1: Core Functions")
    print("=" * 60)

    from core import parse_repository, build_graph, load_repository

    repo_path = "."  # Current repo

    print(f"\n1. Load Repository: {repo_path}")
    result = load_repository(repo_path)
    print(f"   ✅ Valid: {result.get('is_valid')}")
    print(f"   Path: {result.get('local_path')}")

    print(f"\n2. Parse Repository")
    result = parse_repository(repo_path)
    if "error" not in result:
        summary = result.get("summary", {})
        print(f"   ✅ Files: {summary.get('total_files')}")
        print(f"   Classes: {summary.get('total_classes')}")
        print(f"   Functions: {summary.get('total_functions')}")
    else:
        print(f"   ⚠️ Error: {result['error']}")

    print(f"\n3. Build Graph")
    result = build_graph(repo_path)
    if "error" not in result:
        summary = result.get("summary", {})
        print(f"   ✅ Graphs: {summary.get('total_graphs')}")
        print(f"   Nodes: {summary.get('total_nodes')}")
        print(f"   Edges: {summary.get('total_edges')}")
    else:
        print(f"   ⚠️ Error: {result['error']}")


def test_skills():
    """Test skill modules."""
    print("\n" + "=" * 60)
    print("TEST 2: Skills")
    print("=" * 60)

    from skills import (
        analyze_repo_skill,
        architecture_skill,
        qna_skill,
    )

    repo_path = "."

    print(f"\n1. Analyze Repository Skill")
    output = analyze_repo_skill.run(repo_path)
    print(f"   ✅ {output.summary[:80]}...")
    print(f"   Evidence: {len(output.evidence)} items")

    print(f"\n2. Architecture Skill")
    output = architecture_skill.run(repo_path)
    print(f"   ✅ {output.summary[:80]}...")
    print(f"   Layers: {list(output.details.get('layers', {}).keys())}")

    print(f"\n3. Q&A Skill")
    output = qna_skill.run(repo_path, "How many files are there?")
    print(f"   ✅ {output.summary}")


def test_agents():
    """Test agent orchestrators."""
    print("\n" + "=" * 60)
    print("TEST 3: Agents")
    print("=" * 60)

    from comprehension_agent import ComprehensionAgent
    from architecture_agent import ArchitectureAgent

    repo_path = "."

    print(f"\n1. Comprehension Agent")
    agent = ComprehensionAgent()
    output = agent.analyze(repo_path)
    print(f"   ✅ {output.summary[:80]}...")

    print(f"\n2. Architecture Agent")
    agent = ArchitectureAgent()
    output = agent.analyze(repo_path)
    print(f"   ✅ {output.summary[:80]}...")

    print(f"\n3. Comprehension Agent - Ask")
    agent = ComprehensionAgent()
    output = agent.ask(repo_path, "How many classes?")
    print(f"   ✅ {output.summary}")


def test_agent_runner():
    """Test the agent runner."""
    print("\n" + "=" * 60)
    print("TEST 4: Agent Runner (Command Routing)")
    print("=" * 60)

    from agent_runner import run_agent

    repo_path = "."

    print(f"\n1. /analyze command")
    result = run_agent("/analyze", repo_path)
    print(f"   ✅ Status: {result.get('status')}")
    print(f"   Summary: {result.get('summary')[:80]}...")

    print(f"\n2. /architecture command")
    result = run_agent("/architecture", repo_path)
    print(f"   ✅ Status: {result.get('status')}")

    print(f"\n3. /ask command")
    result = run_agent("/ask", repo_path, "How many files?")
    print(f"   ✅ Status: {result.get('status')}")
    print(f"   Summary: {result.get('summary')}")

    print(f"\n4. Output saved to:")
    output_dir = Path("output/analysis-results")
    if output_dir.exists():
        files = list(output_dir.glob("*.json"))
        for f in files[-3:]:  # Show last 3
            print(f"   📄 {f.name}")


def test_hooks():
    """Test the hook system."""
    print("\n" + "=" * 60)
    print("TEST 5: Hook System")
    print("=" * 60)

    from hooks import register, trigger, HookRegistry

    print(f"\n1. Register Hook")

    called = []

    def my_hook(repo_path: str):
        called.append(repo_path)

    register("on_analysis_complete", my_hook)
    print(f"   ✅ Hook registered")

    print(f"\n2. Trigger Hook")
    trigger("on_analysis_complete", "test_repo")
    print(f"   ✅ Hook triggered: {called}")


def test_output_format():
    """Test output file format."""
    print("\n" + "=" * 60)
    print("TEST 6: Output Format")
    print("=" * 60)

    output_dir = Path("output/analysis-results")
    if output_dir.exists():
        files = list(output_dir.glob("*.json"))
        if files:
            latest = sorted(files)[-1]
            print(f"\n1. Reading: {latest.name}")

            with open(latest) as f:
                data = json.load(f)

            print(f"   ✅ Command: {data.get('command')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Timestamp: {data.get('timestamp')}")
            print(f"   Summary: {data.get('summary')[:60]}...")
            print(f"   Evidence items: {len(data.get('evidence', []))}")
        else:
            print("\n   ⚠️ No output files found. Run /analyze first.")
    else:
        print("\n   ⚠️ Output directory not found.")


def run():
    """Run all tests."""
    print("\n")
    print(">> Agent System Test Suite")
    print("=" * 60)

    try:
        test_core_functions()
        test_skills()
        test_agents()
        test_agent_runner()
        test_hooks()
        test_output_format()

        print("\n" + "=" * 60)
        print("✅ All Tests Complete")
        print("=" * 60)
        print("\nNext Steps:")
        print("  1. Check output/analysis-results/ for generated reports")
        print("  2. Read IMPLEMENTATION_GUIDE.md for extension instructions")
        print("  3. Create new skills following the pattern in skills/")
        print("  4. Integrate with VS Code using agent_runner.py")
        print("\n")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    run()


