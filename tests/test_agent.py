import json

import httpx
from anthropic import Anthropic
from typer.testing import CliRunner

from nitaqat_agent.agent import STEPS, run_agent
from nitaqat_agent.cli import app


def test_mock_cli_offline_in_arabic(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    result = CliRunner().invoke(
        app, ["match", "--mock", "--lang", "ar", "--skills", "إكسل، SQL"]
    )
    assert result.exit_code == 0, result.output
    report = json.loads(result.output)
    assert report["matches"][0]["role"] == "محلل بيانات مبتدئ"
    assert report["recommendations"][0]["sdg_target"] == "8.5"


def test_claude_protocol_uses_grounded_actions_and_excludes_raw_labels():
    calls = []

    def respond(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        name = body["tool_choice"]["name"]
        calls.append(name)
        assert "PRIVATE_LABEL" not in request.content.decode()
        if len(calls) > 1:
            assert body["messages"][-1]["content"][0]["tool_use_id"] == f"step_{len(calls) - 1}"
        arguments = {"first_action": 1} if name == "generate_report" else {}
        return httpx.Response(200, json={
            "type": "message",
            "id": f"message_{len(calls)}",
            "role": "assistant",
            "model": body["model"],
            "content": [{
                "type": "tool_use",
                "id": f"step_{len(calls)}",
                "name": name,
                "input": arguments,
            }],
            "stop_reason": "tool_use",
            "stop_sequence": None,
            "usage": {"input_tokens": 10, "output_tokens": 10},
        })

    transport = httpx.MockTransport(respond)
    with Anthropic(api_key="test-placeholder", http_client=httpx.Client(transport=transport)) as sdk:
        report = run_agent(["Excel", "SQL", "PRIVATE_LABEL"], "en", mock=False, client=sdk)
    assert calls == list(STEPS)
    assert report.unrecognized_count == 1
    assert [action.sdg_target for action in report.recommendations] == ["4.4", "8.5"]
