#!/usr/bin/env python3
"""
CLI script to migrate legacy files to enhanced metadata format.

Usage:
    python migrate_enhanced_files.py --help
    python migrate_enhanced_files.py status
    python migrate_enhanced_files.py migrate --batch-size 50
    python migrate_enhanced_files.py migrate --user-id <user_id>
    python migrate_enhanced_files.py verify --file-path <path>
"""

import asyncio
import click
import sys
from pathlib import Path

# Add the src directory to the path so we can import langflow modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "backend" / "base"))

from langflow.services.migration.file_migration import (
    FileMigrationService,
    migrate_all_files,
    migrate_user_files,
    get_migration_status
)
from langflow.services.deps import get_session


@click.group()
def cli():
    """Enhanced File Migration CLI Tool."""
    pass


@cli.command()
@click.option('--format', type=click.Choice(['json', 'table']), default='table', help='Output format')
def status(format):
    """Show migration status and statistics."""
    
    async def _status():
        async with get_session() as session:
            stats = await get_migration_status(session)
            
            if format == 'json':
                import json
                click.echo(json.dumps(stats, indent=2))
            else:
                click.echo("=== Enhanced File Migration Status ===")
                click.echo(f"Total Legacy Files: {stats.get('total_legacy_files', 0)}")
                click.echo(f"Total Enhanced Files: {stats.get('total_enhanced_files', 0)}")
                click.echo(f"Migration Coverage: {stats.get('migration_coverage', 0):.1f}%")
                click.echo(f"Files Needing Migration: {stats.get('files_needing_migration', 0)}")
                
                if 'error' in stats:
                    click.echo(f"Error: {stats['error']}", err=True)
    
    asyncio.run(_status())


@cli.command()
@click.option('--batch-size', default=100, help='Number of files to process in each batch')
@click.option('--user-id', help='Migrate files for specific user only')
@click.option('--dry-run', is_flag=True, help='Show what would be migrated without making changes')
def migrate(batch_size, user_id, dry_run):
    """Migrate legacy files to enhanced metadata format."""
    
    async def _migrate():
        async with get_session() as session:
            if dry_run:
                click.echo("DRY RUN MODE - No changes will be made")
                # In dry run, just show statistics
                stats = await get_migration_status(session)
                click.echo(f"Would migrate {stats.get('files_needing_migration', 0)} files")
                return
            
            click.echo("Starting file migration...")
            
            if user_id:
                click.echo(f"Migrating files for user: {user_id}")
                result = await migrate_user_files(session, user_id, batch_size)
            else:
                click.echo("Migrating all files")
                result = await migrate_all_files(session, batch_size)
            
            # Display results
            click.echo("\n=== Migration Results ===")
            click.echo(f"Total Processed: {result['total_processed']}")
            click.echo(f"Successfully Migrated: {result['successfully_migrated']}")
            click.echo(f"Already Migrated: {result['already_migrated']}")
            click.echo(f"Failed: {result['failed']}")
            
            if result['errors']:
                click.echo("\nErrors:")
                for error in result['errors']:
                    click.echo(f"  - {error}")
            
            if result['successfully_migrated'] > 0:
                click.echo(f"\n✅ Successfully migrated {result['successfully_migrated']} files!")
            
            if result['failed'] > 0:
                click.echo(f"\n❌ {result['failed']} files failed to migrate")
    
    asyncio.run(_migrate())


@cli.command()
@click.option('--file-path', required=True, help='File path to verify')
def verify(file_path):
    """Verify migration status of a specific file."""
    
    async def _verify():
        async with get_session() as session:
            migration_service = FileMigrationService(session)
            result = await migration_service.verify_migration(file_path)
            
            click.echo(f"=== Verification Results for {file_path} ===")
            click.echo(f"Legacy File Exists: {'✅' if result['legacy_exists'] else '❌'}")
            click.echo(f"Enhanced Metadata Exists: {'✅' if result['enhanced_exists'] else '❌'}")
            click.echo(f"Original Filename Matches: {'✅' if result['original_filename_matches'] else '❌'}")
            click.echo(f"Migration Needed: {'⚠️ Yes' if result['migration_needed'] else '✅ No'}")
            
            if 'details' in result:
                details = result['details']
                if 'legacy_name' in details:
                    click.echo(f"Legacy Filename: {details['legacy_name']}")
                if 'enhanced_name' in details:
                    click.echo(f"Enhanced Filename: {details['enhanced_name']}")
            
            if 'error' in result:
                click.echo(f"Error: {result['error']}", err=True)
    
    asyncio.run(_verify())


@cli.command()
@click.option('--pattern', required=True, help='File name pattern to match')
@click.option('--batch-size', default=100, help='Number of files to process')
def migrate_pattern(pattern, batch_size):
    """Migrate files matching a specific pattern."""
    
    async def _migrate_pattern():
        async with get_session() as session:
            migration_service = FileMigrationService(session)
            
            click.echo(f"Migrating files matching pattern: {pattern}")
            result = await migration_service.migrate_files_by_pattern(pattern, batch_size)
            
            # Display results
            click.echo("\n=== Pattern Migration Results ===")
            click.echo(f"Total Processed: {result['total_processed']}")
            click.echo(f"Successfully Migrated: {result['successfully_migrated']}")
            click.echo(f"Already Migrated: {result['already_migrated']}")
            click.echo(f"Failed: {result['failed']}")
            
            if result['errors']:
                click.echo("\nErrors:")
                for error in result['errors']:
                    click.echo(f"  - {error}")
    
    asyncio.run(_migrate_pattern())


@cli.command()
@click.option('--file-path', required=True, help='File path to migrate')
@click.option('--original-filename', help='Original filename (if known)')
def migrate_single(file_path, original_filename):
    """Migrate a single file to enhanced metadata format."""
    
    async def _migrate_single():
        async with get_session() as session:
            migration_service = FileMigrationService(session)
            
            click.echo(f"Migrating single file: {file_path}")
            
            try:
                result = await migration_service.migrate_file_metadata(file_path, original_filename)
                
                if result:
                    click.echo("✅ File migrated successfully!")
                    click.echo(f"Original Filename: {result.original_filename}")
                    click.echo(f"File Path: {result.file_path}")
                    click.echo(f"Created At: {result.created_at}")
                else:
                    click.echo("❌ Migration failed")
                    
            except Exception as e:
                click.echo(f"❌ Error: {str(e)}", err=True)
    
    asyncio.run(_migrate_single())


@cli.command()
def test_connection():
    """Test database connection and enhanced metadata table."""
    
    async def _test():
        try:
            async with get_session() as session:
                from langflow.services.database.models.file_metadata import FileMetadataEnhanced
                from sqlmodel import select
                
                # Try to query the enhanced metadata table
                stmt = select(FileMetadataEnhanced).limit(1)
                result = await session.exec(stmt)
                
                click.echo("✅ Database connection successful")
                click.echo("✅ Enhanced metadata table accessible")
                
                # Count records
                count_stmt = select(FileMetadataEnhanced)
                count_result = await session.exec(count_stmt)
                count = len(count_result.all())
                
                click.echo(f"📊 Enhanced metadata records: {count}")
                
        except Exception as e:
            click.echo(f"❌ Database connection failed: {str(e)}", err=True)
            click.echo("\nTroubleshooting:")
            click.echo("1. Ensure the database migration has been run")
            click.echo("2. Check database connection settings")
            click.echo("3. Verify enhanced metadata table exists")
    
    asyncio.run(_test())


if __name__ == '__main__':
    cli()
