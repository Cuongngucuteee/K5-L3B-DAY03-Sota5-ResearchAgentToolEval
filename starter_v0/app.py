"""Agent chat and dataset evaluation UI. Run: python -m streamlit run app.py."""
from __future__ import annotations

from contextlib import redirect_stdout
from datetime import datetime
from io import StringIO
import json
import os
from pathlib import Path
from uuid import uuid4

import streamlit as st

from agent import ResearchAgent
from providers import make_provider
from run_eval import (
    ROOT, DATA_DIR, case_messages, evaluate_phase_b, load_cases, load_dataset_info, print_table,
    summarize, validate_expected_tools,
)
from tools import load_tool_declarations, to_openai_tools
from versioning import file_hash

MODEL = "gemini-3.5-flash"


def safe_error(exc: Exception) -> str:
    message = f"{type(exc).__name__}: {exc}"
    for name, value in os.environ.items():
        if value and any(word in name.upper() for word in ("KEY", "TOKEN", "SECRET", "PASSWORD")):
            message = message.replace(value, "[redacted]")
    return message


def run_case(
    case: dict, *, provider, system_prompt: str,
    tools: list[dict], model: str | None = None, suite: str = "base",
) -> dict:
    """Run one UI eval case using the same steps and output schema as the CLI."""
    agent = ResearchAgent(provider, system_prompt=system_prompt, tools=tools, model=model)
    try:
        tool_choice = None if case["expect"].get("no_tool") else "required"
        run = agent.run(case_messages(case), tool_choice=tool_choice)
        calls = [{"name": call.name, "args": call.args} for call in run.tool_calls]
        result = evaluate_phase_b(case, calls, run.text)
        tool_results = run.tool_results
    except Exception as exc:
        calls = []
        tool_results = []
        result = {
            "passed": False,
            "failure_type": "provider_error",
            "case_failure_type": case.get("failure_type"),
            "observed_mismatch": "provider_error",
            "failures": [f"{type(exc).__name__}: {str(exc)}"],
            "actual_tool_calls": [],
            "actual_text": None,
            "routing_correct": False,
            "args_correct": False,
        }
    return {
        "id": case["id"],
        "phase": case["phase"],
        "suite": suite,
        "case_suite": case.get("suite", suite),
        "is_multiturn": "turns" in case,
        "metadata": case.get("metadata", {}),
        "input": case.get("input") or case.get("query") or case.get("turns"),
        "expect": case["expect"],
        "result": result,
        "tool_results": tool_results,
    }


def run_cases(dataset: Path, cases: list[dict]) -> None:
    """Run UI cases once each and reuse the CLI scoring and summary helpers."""
    prompt_path = ROOT / "artifacts/system_prompt.md"
    tools_path = ROOT / "artifacts/tools.yaml"
    prompt = prompt_path.read_text(encoding="utf-8")
    declarations = load_tool_declarations(tools_path)
    validate_expected_tools(cases, declarations, dataset)
    tools = to_openai_tools(declarations)
    provider = make_provider("gemini")
    suite = dataset.stem.removeprefix("eval_")
    if suite not in {"base", "group", "cross", "extension"}:
        suite = "base"
    payload = {
        "run_id": f"streamlit_gemini_{uuid4().hex}",
        "phase": "B", "suite": suite, "provider": "gemini", "model": MODEL,
        "system_prompt": str(prompt_path), "tools": str(tools_path),
        "prompt_hash": file_hash(prompt_path), "tools_hash": file_hash(tools_path),
        "eval_cases": str(dataset), **load_dataset_info(dataset),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "summary": {}, "results": [],
    }
    st.session_state.eval_run = payload
    st.session_state.pop("save_error", None)
    progress = st.progress(0.0)
    current = st.empty()
    for index, case in enumerate(cases):
        current.text(f"Running {case['id']}… ({index + 1}/{len(cases)})")
        payload["results"].append(run_case(
            case, provider=provider, system_prompt=prompt,
            tools=tools, model=MODEL, suite=suite,
        ))
        payload["summary"] = summarize(payload["results"])
        progress.progress((index + 1) / len(cases))
    current.empty()
    output_path = ROOT / "runs" / f"{payload['run_id']}.json"
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    except OSError as exc:
        st.session_state.save_error = safe_error(exc)


def render_evaluation() -> None:
    st.title("Research Agent · Dataset testing")
    st.caption(f"{MODEL} · Same agent execution and scoring as run_eval.py")
    datasets = sorted(DATA_DIR.glob("eval_*.json"))
    if not datasets:
        st.info("No evaluation datasets found in data/.")
        st.stop()
    dataset = st.selectbox("Dataset", datasets, format_func=lambda path: path.name)
    try:
        cases = load_cases(dataset, "B")
    except Exception as exc:
        st.error(f"Could not load dataset: {safe_error(exc)}")
        st.stop()
    if not cases:
        st.info("This dataset has no phase B cases.")
        st.stop()
    selected_case = st.selectbox("Case", cases, format_func=lambda case: case["id"])
    with st.expander("Case input and expected output"):
        st.json(selected_case)
    has_key = bool(os.getenv("GEMINI_API_KEY"))
    if not has_key:
        st.warning("Set GEMINI_API_KEY in starter_v0/.env, then restart the app.")
    single, batch = st.columns(2)
    run_single = single.button("Run selected case", disabled=not has_key, use_container_width=True)
    run_batch = batch.button(f"Run entire dataset ({len(cases)} cases)", disabled=not has_key, use_container_width=True)
    if run_single or run_batch:
        try:
            run_cases(dataset, cases if run_batch else [selected_case])
        except Exception as exc:
            st.error(f"Could not run evaluation: {safe_error(exc)}")
    payload = st.session_state.get("eval_run")
    if payload and payload["results"]:
        st.caption(f"Results: {Path(payload['eval_cases']).name} · {len(payload['results'])} case(s)")
        table = StringIO()
        with redirect_stdout(table):
            print_table(payload["results"], payload["summary"])
        st.code(table.getvalue(), language="text")
        st.json({"summary": payload["summary"], "results": payload["results"]})
        if st.session_state.get("save_error"):
            st.warning("Could not save the run to disk. Download the results to keep a copy.")
        st.download_button(
            "Download results JSON", data=json.dumps(payload, ensure_ascii=False, indent=2, default=str),
            file_name=f"{payload['run_id']}.json", mime="application/json",
        )


def render_chat() -> None:
    st.title("Research Agent · Chat")
    st.caption(f"{MODEL} · One agent run per message")
    if "agent_chat" not in st.session_state:
        st.session_state.agent_chat = {"id": uuid4().hex, "turns": [], "history": []}
    if st.button("New chat"):
        st.session_state.agent_chat = {"id": uuid4().hex, "turns": [], "history": []}
        st.rerun()
    chat = st.session_state.agent_chat
    if not os.getenv("GEMINI_API_KEY"):
        st.warning("Set GEMINI_API_KEY in starter_v0/.env, then restart the app.")
    for turn in chat["turns"]:
        with st.chat_message("user"):
            st.markdown(turn["user"])
        with st.chat_message("assistant"):
            if "error" in turn:
                st.error(turn["error"])
            else:
                if turn["output"]["text"]:
                    st.markdown(turn["output"]["text"])
                st.json(turn["output"])
    if chat["turns"]:
        st.download_button(
            "Download chat JSON", data=json.dumps(chat["turns"], ensure_ascii=False, indent=2, default=str),
            file_name=f"chat_{chat['id']}.json", mime="application/json",
        )
    if st.session_state.get("chat_save_error"):
        st.warning("Could not save the chat to disk. Download the chat to keep a copy.")
    text = st.chat_input("Message your research agent…", disabled=not bool(os.getenv("GEMINI_API_KEY")))
    if text and text.strip():
        text = text.strip()
        turn = {"user": text}
        try:
            prompt = (ROOT / "artifacts/system_prompt.md").read_text(encoding="utf-8")
            tools = to_openai_tools(load_tool_declarations(ROOT / "artifacts/tools.yaml"))
            with st.spinner("Running agent once…"):
                agent = ResearchAgent(make_provider("gemini"), system_prompt=prompt, tools=tools, model=MODEL)
                run = agent.run([*chat["history"], {"role": "user", "content": text}])
            output = {
                "text": run.text,
                "tool_calls": [{"name": call.name, "args": call.args} for call in run.tool_calls],
                "tool_results": run.tool_results,
            }
            turn["output"] = output
            chat["history"].extend([
                {"role": "user", "content": text},
                {"role": "assistant", "content": json.dumps(output, ensure_ascii=False, default=str)},
            ])
        except Exception as exc:
            turn["error"] = safe_error(exc)
        chat["turns"].append(turn)
        try:
            path = ROOT / "transcripts" / f"chat_{chat['id']}.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"model": MODEL, "turns": chat["turns"]}, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
            st.session_state.pop("chat_save_error", None)
        except OSError as exc:
            st.session_state.chat_save_error = safe_error(exc)
        st.rerun()


def main() -> None:
    st.set_page_config(page_title="Research Agent", page_icon="🔎", layout="wide")
    mode = st.sidebar.radio("Workspace", ["Chat", "Dataset evaluation"])
    if mode == "Chat":
        render_chat()
    else:
        render_evaluation()


if __name__ == "__main__":
    main()
