from sqlmodel import Session, select
from langflow.services.database.models.file_metadata import FileMetadataService, FileMetadataEnhanced
from langflow.services.database.models.file import File as LegacyFile
from typing import Optional, List, Dict, Any
import os
import asyncio
from pathlib import Path


class FileMigrationService:
    """Service to migrate legacy files to enhanced metadata format."""
    
    def __init__(self, session: Session):
        self.session = session
        self.metadata_service = FileMetadataService(session)
    
    async def migrate_file_metadata(self, file_path: str, original_filename: Optional[str] = None) -> Optional[FileMetadataEnhanced]:
        """Migrate a single file to enhanced metadata format."""
        
        # Check if already migrated
        existing = await self.metadata_service.get_file_metadata(file_path)
        if existing:
            return existing
        
        # If original filename not provided, try to extract from legacy file table
        if not original_filename:
            original_filename = await self._get_original_filename_from_legacy(file_path)
        
        if not original_filename:
            # Fallback to basename
            original_filename = os.path.basename(file_path)
        
        # Create enhanced metadata from available data
        enhanced = await self.metadata_service.create_file_metadata(
            file_path=file_path,
            original_filename=original_filename,
            content_type=None,  # Not available in legacy
            file_size=self._get_file_size(file_path),
        )
        
        return enhanced
    
    async def _get_original_filename_from_legacy(self, file_path: str) -> Optional[str]:
        """Try to get original filename from legacy file table."""
        try:
            # Extract relative path for database lookup
            path_obj = Path(file_path)
            if len(path_obj.parts) >= 2:
                relative_path = f"{path_obj.parts[-2]}/{path_obj.parts[-1]}"
                
                # Query legacy file table
                stmt = select(LegacyFile).where(LegacyFile.path == relative_path)
                result = await self.session.exec(stmt)
                legacy_file = result.first()
                
                if legacy_file:
                    return legacy_file.name
                    
        except Exception as e:
            print(f"Error getting original filename from legacy table: {e}")
        
        return None
    
    def _get_file_size(self, file_path: str) -> Optional[int]:
        """Get file size if file exists."""
        try:
            if os.path.exists(file_path):
                return os.path.getsize(file_path)
        except Exception:
            pass
        return None
    
    async def bulk_migrate_files(self, batch_size: int = 100, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Migrate all legacy files in batches."""
        
        migration_stats = {
            "total_processed": 0,
            "successfully_migrated": 0,
            "already_migrated": 0,
            "failed": 0,
            "errors": []
        }
        
        try:
            # Get all legacy files that haven't been migrated
            query = select(LegacyFile)
            if user_id:
                query = query.where(LegacyFile.user_id == user_id)
            
            query = query.limit(batch_size)
            results = await self.session.exec(query)
            legacy_files = results.all()
            
            for legacy_file in legacy_files:
                migration_stats["total_processed"] += 1
                
                try:
                    # Check if already migrated
                    existing = await self.metadata_service.get_file_metadata(legacy_file.path)
                    if existing:
                        migration_stats["already_migrated"] += 1
                        continue
                    
                    # Migrate the file
                    enhanced = await self.migrate_file_metadata(
                        file_path=legacy_file.path,
                        original_filename=legacy_file.name
                    )
                    
                    if enhanced:
                        migration_stats["successfully_migrated"] += 1
                    else:
                        migration_stats["failed"] += 1
                        migration_stats["errors"].append(f"Failed to create enhanced metadata for {legacy_file.path}")
                        
                except Exception as e:
                    migration_stats["failed"] += 1
                    migration_stats["errors"].append(f"Error migrating {legacy_file.path}: {str(e)}")
            
        except Exception as e:
            migration_stats["errors"].append(f"Bulk migration error: {str(e)}")
        
        return migration_stats
    
    async def migrate_files_by_pattern(self, file_pattern: str, batch_size: int = 100) -> Dict[str, Any]:
        """Migrate files matching a specific pattern."""
        
        migration_stats = {
            "total_processed": 0,
            "successfully_migrated": 0,
            "already_migrated": 0,
            "failed": 0,
            "errors": []
        }
        
        try:
            # Get files matching pattern
            stmt = select(LegacyFile).where(LegacyFile.name.like(f"%{file_pattern}%")).limit(batch_size)
            results = await self.session.exec(stmt)
            matching_files = results.all()
            
            for legacy_file in matching_files:
                migration_stats["total_processed"] += 1
                
                try:
                    enhanced = await self.migrate_file_metadata(
                        file_path=legacy_file.path,
                        original_filename=legacy_file.name
                    )
                    
                    if enhanced:
                        migration_stats["successfully_migrated"] += 1
                    else:
                        migration_stats["failed"] += 1
                        
                except Exception as e:
                    migration_stats["failed"] += 1
                    migration_stats["errors"].append(f"Error migrating {legacy_file.path}: {str(e)}")
            
        except Exception as e:
            migration_stats["errors"].append(f"Pattern migration error: {str(e)}")
        
        return migration_stats
    
    async def verify_migration(self, file_path: str) -> Dict[str, Any]:
        """Verify that a file has been properly migrated."""
        
        verification_result = {
            "file_path": file_path,
            "legacy_exists": False,
            "enhanced_exists": False,
            "original_filename_matches": False,
            "migration_needed": False,
            "details": {}
        }
        
        try:
            # Check legacy file
            path_obj = Path(file_path)
            if len(path_obj.parts) >= 2:
                relative_path = f"{path_obj.parts[-2]}/{path_obj.parts[-1]}"
                
                stmt = select(LegacyFile).where(LegacyFile.path == relative_path)
                result = await self.session.exec(stmt)
                legacy_file = result.first()
                
                if legacy_file:
                    verification_result["legacy_exists"] = True
                    verification_result["details"]["legacy_name"] = legacy_file.name
            
            # Check enhanced metadata
            enhanced = await self.metadata_service.get_file_metadata(file_path)
            if enhanced:
                verification_result["enhanced_exists"] = True
                verification_result["details"]["enhanced_name"] = enhanced.original_filename
                
                # Check if names match
                if legacy_file and enhanced:
                    verification_result["original_filename_matches"] = (
                        legacy_file.name == enhanced.original_filename
                    )
            
            # Determine if migration is needed
            verification_result["migration_needed"] = (
                verification_result["legacy_exists"] and not verification_result["enhanced_exists"]
            )
            
        except Exception as e:
            verification_result["error"] = str(e)
        
        return verification_result
    
    async def get_migration_statistics(self) -> Dict[str, Any]:
        """Get overall migration statistics."""
        
        stats = {
            "total_legacy_files": 0,
            "total_enhanced_files": 0,
            "migration_coverage": 0.0,
            "files_needing_migration": 0
        }
        
        try:
            # Count legacy files
            legacy_count_stmt = select(LegacyFile)
            legacy_results = await self.session.exec(legacy_count_stmt)
            stats["total_legacy_files"] = len(legacy_results.all())
            
            # Count enhanced files
            enhanced_count_stmt = select(FileMetadataEnhanced)
            enhanced_results = await self.session.exec(enhanced_count_stmt)
            stats["total_enhanced_files"] = len(enhanced_results.all())
            
            # Calculate coverage
            if stats["total_legacy_files"] > 0:
                stats["migration_coverage"] = (
                    stats["total_enhanced_files"] / stats["total_legacy_files"]
                ) * 100
            
            stats["files_needing_migration"] = max(
                0, stats["total_legacy_files"] - stats["total_enhanced_files"]
            )
            
        except Exception as e:
            stats["error"] = str(e)
        
        return stats


# CLI utility functions
async def migrate_all_files(session: Session, batch_size: int = 100) -> Dict[str, Any]:
    """Utility function to migrate all files."""
    migration_service = FileMigrationService(session)
    return await migration_service.bulk_migrate_files(batch_size)


async def migrate_user_files(session: Session, user_id: str, batch_size: int = 100) -> Dict[str, Any]:
    """Utility function to migrate files for a specific user."""
    migration_service = FileMigrationService(session)
    return await migration_service.bulk_migrate_files(batch_size, user_id)


async def get_migration_status(session: Session) -> Dict[str, Any]:
    """Utility function to get migration status."""
    migration_service = FileMigrationService(session)
    return await migration_service.get_migration_statistics()
