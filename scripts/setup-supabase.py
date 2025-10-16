#!/usr/bin/env python3
"""
Supabase Database Setup Script.

This script automates the setup of the OSOrganicAI database schema in Supabase.
It reads the schema.sql file and executes it against your Supabase project.

Usage:
    python scripts/setup-supabase.py --url https://xxx.supabase.co --key xxx

Options:
    --url URL          Supabase project URL
    --key KEY          Supabase service role key
    --schema PATH      Path to schema.sql (default: src/db/schema.sql)
    --reset            Drop all tables before creating (DESTRUCTIVE!)
    --dry-run          Show SQL that would be executed without running it
    --verbose          Show detailed output

Examples:
    # Basic setup
    python scripts/setup-supabase.py \\
        --url https://myproject.supabase.co \\
        --key eyJh...

    # Reset database (WARNING: destroys all data)
    python scripts/setup-supabase.py \\
        --url https://myproject.supabase.co \\
        --key eyJh... \\
        --reset

    # Dry run (see what would be executed)
    python scripts/setup-supabase.py \\
        --url https://myproject.supabase.co \\
        --key eyJh... \\
        --dry-run
"""

import argparse
import sys
import re
from pathlib import Path
from typing import Optional
from supabase import create_client, Client


class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color


def print_error(msg: str):
    """Print error message in red."""
    print(f"{Colors.RED}❌ Error: {msg}{Colors.NC}", file=sys.stderr)


def print_success(msg: str):
    """Print success message in green."""
    print(f"{Colors.GREEN}✅ {msg}{Colors.NC}")


def print_info(msg: str):
    """Print info message in blue."""
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.NC}")


def print_warning(msg: str):
    """Print warning message in yellow."""
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.NC}")


def print_header(msg: str):
    """Print section header."""
    print()
    print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}")
    print(f"{Colors.BLUE}{msg}{Colors.NC}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}")
    print()


def read_schema_file(schema_path: Path) -> str:
    """
    Read and return contents of schema.sql file.

    Args:
        schema_path: Path to schema.sql file

    Returns:
        str: SQL content

    Raises:
        FileNotFoundError: If schema file doesn't exist
    """
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with open(schema_path, 'r') as f:
        return f.read()


def split_sql_statements(sql: str) -> list[str]:
    """
    Split SQL script into individual statements.

    Args:
        sql: SQL script content

    Returns:
        List of individual SQL statements
    """
    # Remove comments
    sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)

    # Split by semicolon (naive approach, works for our schema)
    statements = [s.strip() for s in sql.split(';') if s.strip()]

    return statements


def execute_sql(client: Client, sql: str, dry_run: bool = False, verbose: bool = False) -> bool:
    """
    Execute SQL statement against Supabase.

    Args:
        client: Supabase client
        sql: SQL statement to execute
        dry_run: If True, only print SQL without executing
        verbose: Show detailed output

    Returns:
        bool: True if successful
    """
    if dry_run:
        print(f"{Colors.CYAN}[DRY RUN] Would execute:{Colors.NC}")
        print(sql[:200] + "..." if len(sql) > 200 else sql)
        print()
        return True

    if verbose:
        print(f"{Colors.CYAN}Executing:{Colors.NC}")
        print(sql[:200] + "..." if len(sql) > 200 else sql)

    try:
        # Execute SQL using Supabase PostgREST
        # Note: For raw SQL, we need to use the underlying PostgreSQL connection
        # This is a simplified version - in production, use psycopg2 or similar
        client.postgrest.rpc('exec_sql', {'query': sql}).execute()
        return True
    except Exception as e:
        print_error(f"Failed to execute SQL: {e}")
        if verbose:
            print(f"{Colors.RED}{str(e)}{Colors.NC}")
        return False


def verify_connection(client: Client) -> bool:
    """
    Verify connection to Supabase.

    Args:
        client: Supabase client

    Returns:
        bool: True if connection successful
    """
    try:
        # Try a simple query
        response = client.table('_supabase_schema_version').select('*').limit(1).execute()
        return True
    except:
        # Table might not exist, try another method
        try:
            # Try to list tables
            client.postgrest.schema()
            return True
        except Exception as e:
            print_error(f"Connection verification failed: {e}")
            return False


def get_existing_tables(client: Client) -> list[str]:
    """
    Get list of existing tables in the database.

    Args:
        client: Supabase client

    Returns:
        List of table names
    """
    try:
        # This is a simplified version
        # In production, query information_schema.tables
        return []
    except Exception as e:
        print_warning(f"Could not fetch existing tables: {e}")
        return []


def drop_tables(client: Client, dry_run: bool = False) -> bool:
    """
    Drop all OSOrganicAI tables.

    WARNING: This is destructive!

    Args:
        client: Supabase client
        dry_run: If True, only show what would be dropped

    Returns:
        bool: True if successful
    """
    tables = ['code_generations', 'agent_actions', 'conversations']

    print_warning("This will DROP all OSOrganicAI tables!")
    print_warning("All data will be PERMANENTLY DELETED!")

    if not dry_run:
        response = input("Are you sure? Type 'yes' to confirm: ")
        if response.lower() != 'yes':
            print_info("Aborted")
            return False

    for table in tables:
        sql = f"DROP TABLE IF EXISTS {table} CASCADE;"
        if dry_run:
            print(f"{Colors.CYAN}[DRY RUN] Would execute: {sql}{Colors.NC}")
        else:
            print_info(f"Dropping table: {table}")
            try:
                execute_sql(client, sql)
            except Exception as e:
                print_warning(f"Could not drop {table}: {e}")

    return True


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Setup OSOrganicAI database schema in Supabase',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--url',
        required=True,
        help='Supabase project URL (e.g., https://myproject.supabase.co)'
    )

    parser.add_argument(
        '--key',
        required=True,
        help='Supabase service role key'
    )

    parser.add_argument(
        '--schema',
        default='src/db/schema.sql',
        help='Path to schema.sql file (default: src/db/schema.sql)'
    )

    parser.add_argument(
        '--reset',
        action='store_true',
        help='Drop all tables before creating (DESTRUCTIVE!)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show SQL that would be executed without running it'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed output'
    )

    args = parser.parse_args()

    print_header("🗄️  OSOrganicAI Supabase Setup")

    # Validate schema file
    schema_path = Path(args.schema)
    if not schema_path.exists():
        print_error(f"Schema file not found: {schema_path}")
        print_info("Run this script from the OSOrganicAI repository root")
        sys.exit(1)

    print_info(f"Schema file: {schema_path}")
    print_info(f"Supabase URL: {args.url}")

    if args.dry_run:
        print_warning("DRY RUN MODE - No changes will be made")

    # Create Supabase client
    print_info("Connecting to Supabase...")
    try:
        client = create_client(args.url, args.key)
    except Exception as e:
        print_error(f"Failed to create Supabase client: {e}")
        sys.exit(1)

    # Verify connection
    print_info("Verifying connection...")
    if not args.dry_run:
        if not verify_connection(client):
            print_error("Connection verification failed")
            print_info("Please check your URL and service role key")
            sys.exit(1)
        print_success("Connected to Supabase")

    # Reset if requested
    if args.reset:
        print_header("⚠️  Resetting Database")
        if not drop_tables(client, args.dry_run):
            print_error("Reset failed")
            sys.exit(1)
        print_success("Database reset complete")

    # Read schema
    print_header("📖 Reading Schema")
    try:
        schema_sql = read_schema_file(schema_path)
        print_success(f"Schema loaded ({len(schema_sql)} characters)")
    except Exception as e:
        print_error(f"Failed to read schema: {e}")
        sys.exit(1)

    # Split into statements
    statements = split_sql_statements(schema_sql)
    print_info(f"Found {len(statements)} SQL statements")

    # Execute statements
    print_header("🚀 Executing Schema")

    success_count = 0
    failure_count = 0

    for i, statement in enumerate(statements, 1):
        # Skip empty statements
        if not statement.strip():
            continue

        # Determine statement type
        stmt_type = statement.split()[0].upper() if statement.split() else "UNKNOWN"

        if args.verbose:
            print(f"\n[{i}/{len(statements)}] {stmt_type}...")

        if execute_sql(client, statement, args.dry_run, args.verbose):
            success_count += 1
            if not args.verbose:
                print(".", end="", flush=True)
        else:
            failure_count += 1
            print_error(f"Statement {i} failed")

    print()  # New line after dots

    # Summary
    print_header("📊 Setup Summary")

    print(f"Total statements: {len(statements)}")
    print(f"Successful: {Colors.GREEN}{success_count}{Colors.NC}")

    if failure_count > 0:
        print(f"Failed: {Colors.RED}{failure_count}{Colors.NC}")
        print()
        print_error("Setup completed with errors")
        sys.exit(1)
    else:
        print()
        print_success("Database setup completed successfully!")

        if not args.dry_run:
            print()
            print("Next steps:")
            print("  1. Update your .env file with Supabase credentials")
            print("  2. Test the connection: python scripts/test-supabase-connection.py")
            print("  3. Deploy your application to Vercel")

    sys.exit(0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_warning("Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        if '--verbose' in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)
