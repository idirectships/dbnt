"""DBNT CLI - Four letters to make AI better."""

import click

from dbnt.adapters.claude_code import ClaudeCodeAdapter
from dbnt.adapters.generic import GenericAdapter
from dbnt.core import check_dissonance, encode_failure, encode_success
from dbnt.signals import detect_signal


@click.group()
@click.version_option()
def main():
    """DBNT - Do Better Next Time

    Universal learning protocol for AI systems.
    Not anger-driven. Signal-driven.

    Four letters. Better AI.
    """
    pass


@main.command()
@click.option(
    "--adapter",
    type=click.Choice(["claude-code", "generic"]),
    default="generic",
    help="System to install into",
)
def install(adapter: str):
    """Install DBNT into your AI system."""
    if adapter == "claude-code":
        ClaudeCodeAdapter().install()
    else:
        GenericAdapter().install()

    click.echo("Installation complete. Start encoding learnings!")


@main.command()
@click.option(
    "--adapter",
    type=click.Choice(["claude-code", "generic"]),
    default="generic",
)
def uninstall(adapter: str):
    """Remove DBNT from your AI system."""
    if adapter == "claude-code":
        ClaudeCodeAdapter().uninstall()
    else:
        GenericAdapter().uninstall()


@main.command()
@click.argument("text")
def detect(text: str):
    """Detect signal type from text.

    Example: dbnt detect "that's perfect"
    """
    signal = detect_signal(text)
    click.echo(f"Type: {signal.type.value}")
    click.echo(f"Strength: {signal.strength.value}")
    click.echo(f"Weight: {signal.weight}")
    if signal.match:
        click.echo(f"Match: {signal.match}")
    click.echo(f"Should encode: {signal.should_encode()}")


@main.command()
@click.argument("pattern")
@click.option(
    "--category",
    "-c",
    type=click.Choice(["format", "code", "explain", "tool", "comm"]),
    required=True,
    help="Success category",
)
@click.option("--context", "-x", default="", help="Why it worked")
def success(pattern: str, category: str, context: str):
    """Encode a success pattern (DBGT).

    Example: dbnt success "Used dataclass for config" -c code -x "Clean and typed"
    """
    rule = encode_success(
        category=category,
        pattern=pattern,
        context=context or "User approved this pattern",
    )
    click.echo(f"Encoded success: {rule.id}")
    click.echo(f"Category: {rule.category.value}")
    click.echo(f"Weight: {rule.weight}")


@main.command()
@click.argument("pattern")
@click.option(
    "--category",
    "-c",
    type=click.Choice(["protocol", "preference", "waste", "gap", "integration"]),
    required=True,
    help="Failure category",
)
@click.option("--context", "-x", default="", help="Why it failed")
def failure(pattern: str, category: str, context: str):
    """Encode a failure pattern (DBNT).

    Example: dbnt failure "Used npm instead of pnpm" -c protocol -x "Project requires pnpm"
    """
    rule = encode_failure(
        category=category,
        pattern=pattern,
        context=context or "This pattern caused issues",
    )
    click.echo(f"Encoded failure: {rule.id}")
    click.echo(f"Category: {rule.category.value}")
    click.echo(f"Weight: {rule.weight}")


@main.command()
def dissonance():
    """Check learning dissonance.

    Shows the balance between success and failure encoding.
    Target: 60% success, 40% failure.
    """
    result = check_dissonance()

    click.echo(f"\nDissonance Score: {result.score:.1%}")
    click.echo(f"Status: {result.status}")
    click.echo("\nRules:")
    click.echo(f"  Success: {result.success_count} (weight: {result.success_weight})")
    click.echo(f"  Failure: {result.failure_count} (weight: {result.failure_weight})")

    if result.recommendation:
        click.echo(f"\nRecommendation: {result.recommendation}")

    # Visual bar
    total = result.success_count + result.failure_count
    if total > 0:
        success_pct = result.success_count / total
        bar_len = 30
        success_bar = int(success_pct * bar_len)
        failure_bar = bar_len - success_bar
        click.echo(f"\n[{'█' * success_bar}{'░' * failure_bar}] {success_pct:.0%} success")


@main.command()
def status():
    """Show DBNT status and stats."""
    result = check_dissonance()

    click.echo("DBNT Status")
    click.echo("=" * 40)

    # Check adapters
    cc = ClaudeCodeAdapter()
    gen = GenericAdapter()

    click.echo("\nAdapters:")
    click.echo(f"  Claude Code: {'✓ installed' if cc.is_installed() else '✗ not installed'}")
    click.echo(f"  Generic: {'✓ installed' if gen.is_installed() else '✗ not installed'}")

    click.echo(f"\nRules: {result.success_count + result.failure_count} total")
    click.echo(f"  Success: {result.success_count}")
    click.echo(f"  Failure: {result.failure_count}")
    click.echo(f"\nDissonance: {result.score:.1%} ({result.status})")


if __name__ == "__main__":
    main()
