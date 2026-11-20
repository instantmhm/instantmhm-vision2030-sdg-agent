"""Bounded Anthropic tool orchestration with an offline replay."""

import json
from dataclasses import dataclass, field
from typing import Any

from anthropic import Anthropic
from anthropic.types import MessageParam, ToolParam, ToolUseBlock
from pydantic import BaseModel, ConfigDict, Field

from saudi_sme_agent.models import (
    Catalog,
    Goal,
    Language,
    Recommendation,
    Report,
    Route,
)
from saudi_sme_agent.prompts import SYSTEM
from saudi_sme_agent.tools import (
    build_checklist,
    generate_report,
    load_catalog,
    select_routes,
)

STEPS = {
    "load_catalog": "Load the official-source catalog.",
    "select_routes": "Filter routes for the chosen goal.",
    "build_checklist": "Build bilingual, source-linked actions.",
    "generate_report": "Choose the first action and assemble the structured report.",
}


class NoArguments(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class ReportArguments(NoArguments):
    first_action: int = Field(
        ge=0, description="Zero-based index from the recommendations."
    )


def tool_definition(name: str) -> ToolParam:
    """Expose the schema for one stage."""
    arguments = ReportArguments if name == "generate_report" else NoArguments
    return ToolParam(
        name=name, description=STEPS[name], input_schema=arguments.model_json_schema()
    )


@dataclass
class Session:
    goal: Goal
    language: Language
    catalog: Catalog | None = None
    routes: list[Route] = field(default_factory=list)
    checklist: list[Recommendation] = field(default_factory=list)

    def dispatch(self, name: str, arguments: Any) -> dict | list | Report:
        """Execute one stage and retain the catalog-backed evidence."""
        if name == "generate_report":
            index = ReportArguments.model_validate(arguments).first_action
            if index >= len(self.checklist):
                raise ValueError("Selected action is outside the checklist.")
            actions = self.checklist.copy()
            actions.insert(0, actions.pop(index))
            return generate_report(self.goal, self.language, actions)

        NoArguments.model_validate(arguments)
        if name == "load_catalog":
            self.catalog = load_catalog()
            return {"source": self.catalog.source}
        if self.catalog is None:
            raise RuntimeError("Load the catalog before selecting routes.")
        if name == "select_routes":
            self.routes = select_routes(self.catalog, self.goal)
            return {"route_ids": [route.id for route in self.routes]}
        if name == "build_checklist":
            self.checklist = build_checklist(self.routes, self.language)
            return [action.model_dump(mode="json") for action in self.checklist]
        raise ValueError(f"Unknown tool: {name}")


def run_agent(
    goal: Goal,
    language: Language,
    *,
    mock: bool,
    client: Anthropic | None = None,
    model: str = "claude-sonnet-4-6",
) -> Report:
    """Run all four stages and return only the tool-generated report."""
    session = Session(goal=goal, language=language)
    if not mock and client is None:
        raise ValueError("A Claude client is required in live mode.")

    messages: list[MessageParam] = [
        {
            "role": "user",
            "content": f"Prepare an SME report for {goal} in {language}.",
        }
    ]
    for name in STEPS:
        if mock:
            arguments = {"first_action": 0} if name == "generate_report" else {}
            call = ToolUseBlock(
                type="tool_use", id=f"mock_{name}", name=name, input=arguments
            )
        else:
            assert client is not None
            response = client.messages.create(
                model=model,
                max_tokens=512,
                system=SYSTEM,
                messages=messages,
                tools=[tool_definition(name)],
                tool_choice={
                    "type": "tool",
                    "name": name,
                    "disable_parallel_tool_use": True,
                },
            )
            calls = [
                block for block in response.content if isinstance(block, ToolUseBlock)
            ]
            if (
                response.stop_reason != "tool_use"
                or len(calls) != 1
                or calls[0].name != name
            ):
                raise ValueError(f"Claude did not complete the {name} stage.")
            call = calls[0]

        result = session.dispatch(call.name, call.input)
        if isinstance(result, Report):
            return result
        if not mock:
            messages.extend(
                [
                    {"role": "assistant", "content": [call.model_dump()]},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": call.id,
                                "content": json.dumps(result, ensure_ascii=False),
                            }
                        ],
                    },
                ]
            )
    raise RuntimeError("The report stage did not return a report.")
