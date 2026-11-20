"""Typer entry point for bilingual career exploration."""

import os
from enum import Enum
from typing import Annotated

import typer
from anthropic import Anthropic, APIError
from dotenv import load_dotenv

from saudi_sme_agent.agent import run_agent

app = typer.Typer(help="Find official Saudi SME licensing and financing routes.")


class OutputLanguage(str, Enum):
    """Supported report locales."""

    english = "en"
    arabic = "ar"


class NavigationGoal(str, Enum):
    """Supported checklist scopes."""

    licensing = "licensing"
    financing = "financing"
    both = "both"


@app.callback()
def main() -> None:
    """Bilingual Saudi SME navigation."""


@app.command()
def guide(
    goal: Annotated[
        str,
        typer.Option(help="licensing / الترخيص, financing / التمويل, both / كلاهما"),
    ],
    language: Annotated[
        OutputLanguage, typer.Option("--lang")
    ] = OutputLanguage.english,
    mock: Annotated[bool, typer.Option(help="Run locally without API access.")] = False,
) -> None:
    """Print a source-linked SME checklist as JSON."""
    aliases = {"الترخيص": "licensing", "التمويل": "financing", "كلاهما": "both"}
    normalized = goal.strip().casefold()
    try:
        selected_goal = NavigationGoal(aliases.get(normalized, normalized))
    except ValueError as error:
        message = (
            "اختر الترخيص أو التمويل أو كلاهما."
            if language == OutputLanguage.arabic
            else "Choose licensing, financing, or both."
        )
        raise typer.BadParameter(message, param_hint="--goal") from error
    client = None
    model = "claude-sonnet-4-6"
    if not mock:
        load_dotenv()
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            message = (
                "اضبط ANTHROPIC_API_KEY أو استخدم --mock."
                if language == OutputLanguage.arabic
                else "Set ANTHROPIC_API_KEY or use --mock."
            )
            typer.echo(message, err=True)
            raise typer.Exit(2)
        model = os.getenv("ANTHROPIC_MODEL") or model
        client = Anthropic(api_key=api_key, timeout=30.0, max_retries=1)
    try:
        report = run_agent(
            selected_goal.value,
            "ar" if language == OutputLanguage.arabic else "en",
            mock=mock,
            client=client,
            model=model,
        )
    except (APIError, OSError, ValueError) as error:
        message = (
            "تعذر إنشاء التقرير. تحقق من إعدادات النموذج والكتالوج."
            if language == OutputLanguage.arabic
            else "Could not generate the report. Check the model settings and catalog."
        )
        typer.echo(f"{message} ({type(error).__name__})", err=True)
        raise typer.Exit(1) from error
    typer.echo(report.model_dump_json(indent=2))
