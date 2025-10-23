"""
Perplexity AI Wrapper - CLI Interface
File: src/cli.py
"""
import click
import json
import asyncio
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from pathlib import Path

from core.client import PerplexityClient
from core.async_client import AsyncPerplexityClient
from core.models import SearchMode, AIModel, SourceType
from auth.cookie_manager import CookieManager
from auth.account_generator import AccountGenerator
from automation.web_driver import PerplexityWebDriver

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    Perplexity AI Wrapper - Unofficial API Client
    
    A comprehensive toolkit for interacting with Perplexity.ai
    """
    pass


# ============================================================================
# SEARCH COMMANDS
# ============================================================================

@cli.command()
@click.argument('query')
@click.option('--mode', '-m', type=click.Choice(['auto', 'pro', 'reasoning', 'deep_research']), 
              default='auto', help='Search mode')
@click.option('--model', type=str, help='AI model (e.g., gpt-4o, claude-3.7-sonnet)')
@click.option('--sources', '-s', multiple=True, help='Source types (web, scholar, social)')
@click.option('--stream', is_flag=True, help='Stream response')
@click.option('--output', '-o', type=click.Path(), help='Save output to file')
@click.option('--format', '-f', type=click.Choice(['text', 'json', 'markdown']), 
              default='text', help='Output format')
@click.option('--profile', '-p', help='Cookie profile to use')
def search(query, mode, model, sources, stream, output, format, profile):
    """
    Execute a search query
    
    Examples:
        perplexity search "What is quantum computing?"
        perplexity search "AI trends 2025" --mode pro --model gpt-4o
        perplexity search "Research paper" --sources scholar --format json
    """
    console.print(f"\n[bold cyan]Searching:[/bold cyan] {query}", style="bold")
    
    # Load cookies if profile specified
    cookies = None
    if profile:
        cookie_manager = CookieManager()
        cookies = cookie_manager.load_cookies(profile)
        if not cookies:
            console.print(f"[red]✗ Profile '{profile}' not found[/red]")
            return
        console.print(f"[green]✓ Loaded profile: {profile}[/green]")
    
    # Initialize client
    client = PerplexityClient(cookies=cookies)
    
    # Convert string inputs to enums
    search_mode = SearchMode(mode)
    ai_model = AIModel(model) if model else None
    source_types = [SourceType(s) for s in sources] if sources else None
    
    try:
        if stream:
            # Streaming mode
            console.print("\n[dim]Streaming response...[/dim]\n")
            for chunk in client.search(
                query=query,
                mode=search_mode,
                model=ai_model,
                sources=source_types,
                stream=True
            ):
                content = chunk.get('content', '')
                if content:
                    console.print(content, end='')
            console.print("\n")
        else:
            # Regular mode with spinner
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Searching...", total=None)
                
                response = client.search(
                    query=query,
                    mode=search_mode,
                    model=ai_model,
                    sources=source_types,
                    stream=False
                )
                
                progress.update(task, completed=True)
            
            # Display response
            _display_response(response, format)
            
            # Save to file if specified
            if output:
                _save_output(response, output, format)
                console.print(f"\n[green]✓ Saved to: {output}[/green]")
    
    except Exception as e:
        console.print(f"\n[red]✗ Error: {str(e)}[/red]")
        raise


@cli.command()
@click.option('--profile', '-p', help='Cookie profile to use')
def conversation(profile):
    """
    Start an interactive conversation session
    
    Example:
        perplexity conversation --profile my_account
    """
    cookies = None
    if profile:
        cookie_manager = CookieManager()
        cookies = cookie_manager.load_cookies(profile)
    
    client = PerplexityClient(cookies=cookies)
    conv_id = client.start_conversation()
    
    console.print("\n[bold green]Started Conversation[/bold green]")
    console.print(f"[dim]ID: {conv_id}[/dim]")
    console.print("\n[yellow]Type your questions (or 'quit' to exit, 'export' to save)[/yellow]\n")
    
    try:
        while True:
            query = console.input("\n[bold cyan]You:[/bold cyan] ")
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if query.lower() == 'export':
                export_format = console.input("Format (json/text/markdown): ") or 'text'
                export_data = client.export_conversation(format=export_format)
                filename = f"conversation_{conv_id[:8]}.{export_format}"
                with open(filename, 'w') as f:
                    f.write(export_data)
                console.print(f"[green]✓ Exported to: {filename}[/green]")
                continue
            
            if not query.strip():
                continue
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Thinking...", total=None)
                response = client.search(query, use_conversation=True)
                progress.update(task, completed=True)
            
            console.print(f"\n[bold magenta]Assistant:[/bold magenta]")
            console.print(response.answer)
            
            if response.sources:
                console.print("\n[dim]Sources:[/dim]")
                for idx, source in enumerate(response.sources[:3], 1):
                    console.print(f"  {idx}. {source.get('title', 'N/A')}")
    
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Conversation ended[/yellow]")
    
    # Offer to export
    if console.input("\nExport conversation? (y/N): ").lower() == 'y':
        export_format = console.input("Format (json/text/markdown): ") or 'text'
        export_data = client.export_conversation(format=export_format)
        filename = f"conversation_{conv_id[:8]}.{export_format}"
        with open(filename, 'w') as f:
            f.write(export_data)
        console.print(f"[green]✓ Exported to: {filename}[/green]")


@cli.command()
@click.argument('queries', nargs=-1)
@click.option('--mode', '-m', default='auto', help='Search mode')
@click.option('--output', '-o', type=click.Path(), help='Save results to file')
def batch(queries, mode, output):
    """
    Process multiple queries concurrently
    
    Example:
        perplexity batch "Query 1" "Query 2" "Query 3" --output results.json
    """
    if not queries:
        console.print("[red]No queries provided[/red]")
        return
    
    console.print(f"\n[bold]Processing {len(queries)} queries...[/bold]\n")
    
    async def run_batch():
        async with AsyncPerplexityClient() as client:
            with Progress(console=console) as progress:
                task = progress.add_task("Searching...", total=len(queries))
                
                responses = await client.batch_search(
                    list(queries),
                    mode=SearchMode(mode)
                )
                
                progress.update(task, completed=len(queries))
            
            return responses
    
    responses = asyncio.run(run_batch())
    
    # Display results
    table = Table(title="Batch Results")
    table.add_column("Query", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Answer Preview", style="white")
    
    for idx, (query, response) in enumerate(zip(queries, responses), 1):
        if isinstance(response, Exception):
            table.add_row(query, "[red]ERROR[/red]", str(response)[:50])
        else:
            table.add_row(query, "[green]✓[/green]", response.answer[:50] + "...")
    
    console.print(table)
    
    # Save if requested
    if output:
        results = []
        for query, response in zip(queries, responses):
            if not isinstance(response, Exception):
                results.append(response.to_dict())
        
        with open(output, 'w') as f:
            json.dump(results, f, indent=2)
        console.print(f"\n[green]✓ Saved to: {output}[/green]")


# ============================================================================
# COOKIE MANAGEMENT COMMANDS
# ============================================================================

@cli.group()
def cookies():
    """Manage authentication cookies"""
    pass


@cookies.command('extract')
@click.option('--browser', '-b', type=click.Choice(['chrome', 'firefox', 'edge']), 
              default='chrome', help='Browser to extract from')
@click.option('--profile', '-p', help='Profile name to save as')
def extract_cookies(browser, profile):
    """
    Extract cookies from browser
    
    Example:
        perplexity cookies extract --browser chrome --profile my_account
    """
    console.print(f"\n[cyan]Extracting cookies from {browser}...[/cyan]")
    
    try:
        cookie_manager = CookieManager()
        cookies_dict = cookie_manager.auto_extract(browser=browser)
        
        console.print(f"[green]✓ Extracted {len(cookies_dict)} cookies[/green]")
        
        if profile:
            cookie_manager.save_cookies(cookies_dict, name=profile)
            console.print(f"[green]✓ Saved as profile: {profile}[/green]")
        else:
            console.print("\n[yellow]Cookies (first 3):[/yellow]")
            for idx, (key, value) in enumerate(list(cookies_dict.items())[:3], 1):
                console.print(f"  {idx}. {key}: {value[:30]}...")
    
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")


@cookies.command('list')
def list_cookies():
    """List all saved cookie profiles"""
    cookie_manager = CookieManager()
    profiles = cookie_manager.list_profiles()
    
    if not profiles:
        console.print("[yellow]No saved profiles[/yellow]")
        return
    
    table = Table(title="Saved Cookie Profiles")
    table.add_column("Profile Name", style="cyan")
    table.add_column("Status", style="green")
    
    for profile in profiles:
        table.add_row(profile, "✓ Active")
    
    console.print(table)


@cookies.command('delete')
@click.argument('profile')
def delete_cookies(profile):
    """Delete a cookie profile"""
    cookie_manager = CookieManager()
    
    if cookie_manager.delete_profile(profile):
        console.print(f"[green]✓ Deleted profile: {profile}[/green]")
    else:
        console.print(f"[red]✗ Profile not found: {profile}[/red]")


# ============================================================================
# ACCOUNT GENERATION COMMANDS
# ============================================================================

@cli.group()
def account():
    """Account generation and management"""
    pass


@account.command('generate')
@click.option('--count', '-c', default=1, help='Number of accounts to generate')
@click.option('--emailnator-cookies', '-e', type=click.Path(exists=True), 
              help='Path to Emailnator cookies JSON')
@click.option('--delay', '-d', default=30, help='Delay between accounts (seconds)')
def generate_account(count, emailnator_cookies, delay):
    """
    Generate new Perplexity accounts
    
    Example:
        perplexity account generate --count 3 --emailnator-cookies cookies.json
    """
    if not emailnator_cookies:
        console.print("[red]✗ Emailnator cookies required[/red]")
        console.print("[yellow]Get them from: https://www.emailnator.com[/yellow]")
        return
    
    # Load emailnator cookies
    with open(emailnator_cookies, 'r') as f:
        en_cookies = json.load(f)
    
    console.print(f"\n[bold]Generating {count} account(s)...[/bold]\n")
    
    generator = AccountGenerator(
        emailnator_cookies=en_cookies,
        cookie_manager=CookieManager()
    )
    
    try:
        if count == 1:
            account = generator.create_account(save_profile=True)
            console.print(f"\n[green]✓ Account created: {account.email}[/green]")
        else:
            accounts = generator.create_multiple_accounts(count, delay=delay)
            console.print(f"\n[green]✓ Created {len(accounts)} accounts[/green]")
            
            # Show summary
            table = Table(title="Generated Accounts")
            table.add_column("Email", style="cyan")
            table.add_column("Status", style="green")
            
            for account in accounts:
                table.add_row(account.email, account.status)
            
            console.print(table)
    
    except Exception as e:
        console.print(f"\n[red]✗ Error: {str(e)}[/red]")


# ============================================================================
# WEB AUTOMATION COMMANDS
# ============================================================================

@cli.command()
@click.option('--headless', is_flag=True, help='Run in headless mode')
@click.option('--user-data-dir', type=click.Path(), help='Chrome profile directory')
def browser(headless, user_data_dir):
    """
    Start interactive browser session
    
    Example:
        perplexity browser --user-data-dir "C:\\Users\\User\\AppData\\Local\\Google\\Chrome\\User Data"
    """
    console.print("\n[bold cyan]Starting browser session...[/bold cyan]")
    
    driver = PerplexityWebDriver(
        headless=headless,
        user_data_dir=user_data_dir,
        stealth_mode=True
    )
    
    try:
        driver.start()
        driver.navigate_to_perplexity()
        
        console.print("\n[green]✓ Browser ready[/green]")
        driver.interactive_mode()
    
    finally:
        driver.close()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def _display_response(response, format):
    """Display search response in specified format"""
    if format == 'json':
        console.print_json(json.dumps(response.to_dict(), indent=2))
    
    elif format == 'markdown':
        md = Markdown(response.to_markdown())
        console.print(md)
    
    else:  # text
        console.print(f"\n[bold green]Answer:[/bold green]")
        console.print(response.answer)
        
        if response.sources:
            console.print(f"\n[bold cyan]Sources ({len(response.sources)}):[/bold cyan]")
            for idx, source in enumerate(response.sources[:5], 1):
                console.print(f"  {idx}. {source.get('title', 'N/A')}")
                console.print(f"     [dim]{source.get('url', '')}[/dim]")
        
        if response.related_questions:
            console.print(f"\n[bold yellow]Related Questions:[/bold yellow]")
            for q in response.related_questions[:3]:
                console.print(f"  • {q}")


def _save_output(response, filepath, format):
    """Save response to file"""
    filepath = Path(filepath)
    
    if format == 'json':
        with open(filepath, 'w') as f:
            json.dump(response.to_dict(), f, indent=2)
    
    elif format == 'markdown':
        with open(filepath, 'w') as f:
            f.write(response.to_markdown())
    
    else:  # text
        with open(filepath, 'w') as f:
            f.write(f"Query: {response.query}\n\n")
            f.write(f"Answer:\n{response.answer}\n\n")
            if response.sources:
                f.write("Sources:\n")
                for idx, source in enumerate(response.sources, 1):
                    f.write(f"{idx}. {source.get('title')}\n")
                    f.write(f"   {source.get('url')}\n")


def main():
    """Main entry point"""
    cli()


if __name__ == '__main__':
    main()