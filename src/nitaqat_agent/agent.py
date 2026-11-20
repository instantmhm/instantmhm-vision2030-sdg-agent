"""Bounded Anthropic tool orchestration with an offline replay."""

import json
from dataclasses import dataclass, field
from typing import Any

from anthropic import Anthropic
from anthropic.types import MessageParam, ToolParam, ToolUseBlock
from pydantic import BaseModel, ConfigDict, Field

from nitaqat_agent.models import Catalog, Language, Match, Recommendation, Report
from nitaqat_agent.prompts import SYSTEM
from nitaqat_agent.tools import analyze_matches, generate_report, load_catalog, recommend

STEPS = {
    "load_catalog": "Load the illustrative catalog and its provenance.",
    "analyze_matches": "Compute role coverage and missing skills locally.",
    "recommend": "Prepare catalog-grounded counselor and practice actions.",
    "generate_report": "Choose the first action and assemble the structured report.",
}


class NoArguments(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class ReportArguments(NoArguments):
    first_action: int = Field(ge=0, description="Zero-based index from the recommendations.")


def tool_definition(name: str) -> ToolParam:
    """Expose the schema for one stage."""
    arguments = ReportArguments if name == "generate_report" else NoArguments
    return ToolParam(name=name, description=STEPS[name], input_schema=arguments.model_json_schema())


@dataclass
class Session:
    labels: list[str]
    language: Language
    catalog: Catalog | None = None
    matches: list[Match] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    unrecognized: int = 0
    recommendations: list[Recommendation] = field(default_factory=list)

    def dispatch(self, name: str, arguments: Any) -> dict | list | Report:
        """Execute one stage, retaining local state across tool calls."""
        if name == "generate_report":
            index = ReportArguments.model_validate(arguments).first_action
            if index >= len(self.recommendations):
                raise ValueError("Claude selected an action outside the recommendation list.")
            actions = self.recommendations.copy()
            actions.insert(0, actions.pop(index))
            return generate_report(self.matches, actions, self.unrecognized, self.language)

        NoArguments.model_validate(arguments)
        if name == "load_catalog":
            self.catalog = load_catalog()
            return {"source": self.catalog.source, "role_count": len(self.catalog.roles)}
        if self.catalog is None:
            raise RuntimeError("Load the catalog before analysis or recommendation.")
        if name == "analyze_matches":
            self.matches, self.gaps, self.unrecognized = analyze_matches(
                self.catalog, self.labels, self.language
            )
            return {
                "matches": [match.model_dump() for match in self.matches],
                "unrecognized_count": self.unrecognized,
            }
        if name == "recommend":
            self.recommendations = recommend(self.catalog, self.matches, self.gaps, self.language)
            return [action.model_dump() for action in self.recommendations]
        raise ValueError(f"Unknown tool: {name}")


def run_agent(
    labels: list[str],
    language: Language,
    *,
    mock: bool,
    client: Anthropic | None = None,
    model: str = "claude-sonnet-4-6",
) -> Report:
    """Run all four stages and return only the tool-generated report."""
    session = Session(labels=labels, language=language)
    if not mock and client is None:
        raise ValueError("A Claude client is required in live mode.")

    messages: list[MessageParam] = [
        {"role": "user", "content": f"Prepare a career exploration report in {language}."}
    ]
    for name in STEPS:
        if mock:
            arguments = {"first_action": 0} if name == "generate_report" else {}
            call = ToolUseBlock(type="tool_use", id=f"mock_{name}", name=name, input=arguments)
        else:
            assert client is not None
            response = client.messages.create(
                model=model,
                max_tokens=512,
                system=SYSTEM,
                messages=messages,
                tools=[tool_definition(name)],
                tool_choice={"type": "tool", "name": name, "disable_parallel_tool_use": True},
            )
            calls = [block for block in response.content if isinstance(block, ToolUseBlock)]
            if response.stop_reason != "tool_use" or len(calls) != 1 or calls[0].name != name:
                raise ValueError(f"Claude did not complete the {name} stage.")
            call = calls[0]

        result = session.dispatch(call.name, call.input)
        if isinstance(result, Report):
            return result
        if not mock:
            messages.extend([
                {"role": "assistant", "content": [call.model_dump()]},
                {"role": "user", "content": [{
                    "type": "tool_result",
                    "tool_use_id": call.id,
                    "content": json.dumps(result, ensure_ascii=False),
                }]},
            ])
    raise RuntimeError("The report stage did not return a report.")
