# Enhanced Filename Exposure - Implementation Roadmap

This document provides a practical, step-by-step implementation guide for the backward-compatible enhanced filename exposure system.

## Phase 1: Foundation (Week 1-2)
**Goal**: Establish backend infrastructure without breaking existing functionality

### Step 1.1: Database Extensions
```bash
# Create migration script
touch src/backend/base/langflow/alembic/versions/add_enhanced_file_metadata.py
```

**Migration Content:**
```python
"""Add enhanced file metadata table

Revision ID: enhanced_file_metadata_001
Revises: [previous_revision]
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers
revision = 'enhanced_file_metadata_001'
down_revision = '[previous_revision]'
branch_labels = None
depends_on = None

def upgrade():
    # Create new table for enhanced metadata
    op.create_table('file_metadata_enhanced',
        sa.Column('id', sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('original_filename', sa.String(), nullable=False),
        sa.Column('content_type', sa.String(), nullable=True),
        sa.Column('file_size', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('flow_id', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_file_metadata_enhanced_file_path', 'file_path'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    )

def downgrade():
    # Safe to drop new table - no existing data dependency
    op.drop_table('file_metadata_enhanced')
```

### Step 1.2: Backend API Extensions
```bash
# Create new API module
mkdir -p src/backend/base/langflow/api/v2
touch src/backend/base/langflow/api/v2/__init__.py
touch src/backend/base/langflow/api/v2/files.py
touch src/backend/base/langflow/api/v2/schemas.py
```

### Step 1.3: Feature Flag Implementation
```python
# Add to existing settings.py
class Settings(BaseSettings):
    # ... existing settings ...
    
    # Enhanced file functionality
    enable_enhanced_file_inputs: bool = Field(
        default=False,
        env="LANGFLOW_ENABLE_ENHANCED_FILES"
    )
```

### Step 1.4: Testing Phase 1
```bash
# Test database migration
python -m alembic upgrade head

# Test API endpoints
curl -X POST http://localhost:7860/api/v2/files/upload \
  -F "file=@test.txt" \
  -H "Authorization: Bearer $TOKEN"

# Verify backward compatibility
curl -X POST http://localhost:7860/api/v1/files/upload \
  -F "file=@test.txt" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Phase 2: Frontend Extensions (Week 3-4)
**Goal**: Create enhanced frontend components alongside existing ones

### Step 2.1: Enhanced Component Development
```bash
# Create enhanced file input component
mkdir -p src/frontend/src/components/core/parameterRenderComponent/components/enhancedFileInputComponent
touch src/frontend/src/components/core/parameterRenderComponent/components/enhancedFileInputComponent/index.tsx
```

### Step 2.2: Type System Extensions
```typescript
// Add to existing types/files.ts
export interface EnhancedFileMetadata {
  path: string;
  original_filename: string;
  content_type?: string;
  file_size?: number;
  upload_timestamp?: string;
}

export type FileInputValue = string | EnhancedFileMetadata;
```

### Step 2.3: Component Registration
```typescript
// Add to component registry
import { EnhancedFileInputComponent } from './enhancedFileInputComponent';

export const ENHANCED_COMPONENTS = {
  'enhanced-file-input': EnhancedFileInputComponent,
  // ... other enhanced components
};
```

### Step 2.4: Testing Phase 2
```bash
# Build frontend
cd src/frontend
npm run build

# Test enhanced components
npm run test:enhanced-file-input

# Test backward compatibility
npm run test:legacy-file-input
```

---

## Phase 3: Component Framework (Week 5-6)
**Goal**: Extend component framework with enhanced capabilities

### Step 3.1: Enhanced Input Classes
```bash
# Create enhanced input module
touch src/backend/base/langflow/inputs/enhanced_inputs.py
```

### Step 3.2: Compatibility Layer
```bash
# Create compatibility utilities
mkdir -p src/backend/base/langflow/compatibility
touch src/backend/base/langflow/compatibility/__init__.py
touch src/backend/base/langflow/compatibility/file_input_adapter.py
```

### Step 3.3: Migration Utilities
```bash
# Create migration service
mkdir -p src/backend/base/langflow/services/migration
touch src/backend/base/langflow/services/migration/__init__.py
touch src/backend/base/langflow/services/migration/file_migration.py
```

### Step 3.4: Testing Phase 3
```python
# Test enhanced components
def test_enhanced_file_metadata_extractor():
    component = EnhancedFileMetadataExtractor()
    
    # Test with enhanced input
    enhanced_input = FileMetadata(
        path="/path/to/file.pdf",
        original_filename="document.pdf"
    )
    component.input_file = enhanced_input
    result = component.extract_metadata()
    assert "document.pdf" in result.text
    
    # Test with legacy input
    legacy_input = "/path/to/file.pdf"
    component.input_file = legacy_input
    result = component.extract_metadata()
    assert result.text  # Should still work
```

---

## Phase 4: Integration & Migration (Week 7-8)
**Goal**: Integrate all components and provide migration tools

### Step 4.1: End-to-End Integration
```bash
# Test complete flow
python test_enhanced_flow.py
```

### Step 4.2: Migration Tools
```python
# Create migration CLI
@click.command()
@click.option('--batch-size', default=100)
def migrate_files(batch_size):
    """Migrate legacy files to enhanced metadata format."""
    service = FileMigrationService(get_session())
    migrated = service.bulk_migrate_files(batch_size)
    click.echo(f"Migrated {migrated} files")
```

### Step 4.3: Documentation
```bash
# Create comprehensive documentation
touch docs/enhanced_file_inputs.md
touch docs/migration_guide.md
touch docs/backward_compatibility.md
```

### Step 4.4: Performance Testing
```python
# Performance benchmarks
def benchmark_enhanced_vs_legacy():
    # Test file upload performance
    # Test metadata extraction performance
    # Test database query performance
    pass
```

---

## Deployment Strategy

### Development Environment
```bash
# Enable enhanced features
export LANGFLOW_ENABLE_ENHANCED_FILES=true

# Start development server
python -m langflow run --dev
```

### Staging Environment
```bash
# Deploy with feature flags
docker run -e LANGFLOW_ENABLE_ENHANCED_FILES=false langflow:enhanced

# Test migration
docker exec langflow python -m langflow.migration migrate-files
```

### Production Rollout
```bash
# Phase 1: Deploy with features disabled
kubectl apply -f langflow-enhanced-disabled.yaml

# Phase 2: Enable for specific users
kubectl patch configmap langflow-config --patch '{"data":{"LANGFLOW_ENABLE_ENHANCED_FILES":"true"}}'

# Phase 3: Full rollout
kubectl rollout restart deployment/langflow
```

---

## Validation Checklist

### Pre-Deployment
- [ ] All existing tests pass
- [ ] Database migration is reversible
- [ ] Feature flags work correctly
- [ ] Performance impact is acceptable
- [ ] Documentation is complete

### Post-Deployment
- [ ] Legacy components function unchanged
- [ ] Enhanced components work as expected
- [ ] No breaking changes detected
- [ ] Migration tools work correctly
- [ ] Rollback procedures tested

### Success Metrics
- [ ] Zero production incidents
- [ ] All existing flows continue to work
- [ ] Enhanced functionality is available
- [ ] Performance metrics within acceptable range
- [ ] User adoption of enhanced features begins

---

## Risk Mitigation

### High-Risk Scenarios
1. **Database Migration Failure**
   - Mitigation: Test on staging with production data copy
   - Rollback: Automated rollback scripts

2. **Frontend Component Conflicts**
   - Mitigation: Namespace enhanced components
   - Rollback: Feature flag to disable enhanced components

3. **Performance Degradation**
   - Mitigation: Performance testing and monitoring
   - Rollback: Disable enhanced features via feature flag

### Monitoring
```python
# Add monitoring for enhanced features
@monitor_performance
def enhanced_file_upload():
    # Track upload performance
    pass

@monitor_errors
def enhanced_metadata_extraction():
    # Track extraction errors
    pass
```

---

## Timeline Summary

| Phase | Duration | Key Deliverables | Risk Level |
|-------|----------|------------------|------------|
| 1 | 2 weeks | Backend foundation | Low |
| 2 | 2 weeks | Frontend components | Medium |
| 3 | 2 weeks | Component framework | Medium |
| 4 | 2 weeks | Integration & migration | High |

**Total Duration**: 8 weeks
**Go-Live**: Week 9 with gradual rollout

This roadmap ensures a safe, methodical implementation that preserves existing functionality while introducing enhanced capabilities.
