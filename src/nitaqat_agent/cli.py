"""Typer entry point for bilingual career exploration."""

import os
from enum import Enum
from typing import Annotated

import typer
from anthropic import Anthropic, APIError
from dotenv import load_dotenv

from nitaqat_agent.agent import run_agent

app = typer.Typer(help="Explore illustrative Saudi career paths from skill labels.")


class OutputLanguage(str, Enum):
    """Supported report locales."""

    english = "en"
    arabic = "ar"


@app.callback()
def main() -> None:
    """Bilingual job–skill matching for career exploration."""


@app.command()
def match(
    skills: Annotated[str, typer.Option(help="Comma-separated skill labels in Arabic or English.")],
    language: Annotated[OutputLanguage, typer.Option("--lang")] = OutputLanguage.english,
    mock: Annotated[bool, typer.Option(help="Run locally without API access.")] = False,
) -> None:
    """Print a structured career exploration report as JSON."""
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
            skills.replace("،", ",").split(","),
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
