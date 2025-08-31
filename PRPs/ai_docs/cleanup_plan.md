# File Cleanup and Organization Plan

**Generated**: 2025-08-31  
**Priority**: HIGH - Remove clutter before refactoring  
**Estimated Time**: 30 minutes

## Overview

The repository contains numerous test files, duplicates, and temporary files that should be organized or removed to improve maintainability.

## 📁 Files to Remove/Reorganize

### 1. Test Files in Root (Move to `tests/` directory)

**Current State**: 11 test files cluttering root directory

```bash
# Files to move:
./test_60sec_diarization.py
./test_backends.py
./test_diarization_final.py
./test_diarization_simple.py
./test_integration.py
./test_no_diarization.py
./test_real_audio.py
./test_transcription_monitor.py
./test_whisper_8767.py      # Keep this one - it's new and useful
./test_whisper_api.py
./test_whisper_integration.py
```

**Action**: Create proper test structure
```bash
# Create test directory structure
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p tests/fixtures

# Move test files
mv test_*diarization*.py tests/integration/
mv test_backends.py tests/integration/
mv test_integration.py tests/integration/
mv test_whisper_*.py tests/integration/
mv test_real_audio.py tests/fixtures/
mv test_transcription_monitor.py tests/unit/
```

### 2. Duplicate/Obsolete Files to Remove

**Files to DELETE**:
```bash
# Duplicate transcriber implementations
src/core/whisper_transcriber_improved.py  # Duplicate of whisper_transcriber.py
src/core/whisper_transcriber.py.bak       # Backup file

# Mock/diagnostic files (move to tests/fixtures if needed)
mock_whisper_server.py                    # Move to tests/fixtures/
diagnose_cuda_diarization.py              # Move to tests/diagnostics/

# Test results (should not be in repo)
test_result_test_ic_recorder.txt          # Delete
whisper_test_result.json                  # Delete

# Generated transcripts (add to .gitignore)
transcripts/*.txt                         # Delete all, add transcripts/ to .gitignore
```

### 3. Documentation Consolidation

**Current**: 7+ documentation files in root

**Proposed Structure**:
```bash
docs/
├── README.md                  # Keep in root (standard)
├── CHANGELOG.md              # Keep in root (standard)
├── developer/
│   ├── ONBOARDING.md         # Move from root
│   ├── TESTING.md            # Create from test info
│   ├── CLAUDE.md             # Keep in root (CI/CD needs it)
│   └── QUICKSTART.md         # Move from root
├── architecture/
│   ├── TRANSCRIPTION_BACKENDS.md  # Move from root
│   └── WHISPER_DIARIZATION_FIX.md # Move from root
└── guides/
    └── TROUBLESHOOTING.md    # Create if doesn't exist
```

### 4. Script Consolidation

**Scripts to organize**:
```bash
scripts/
├── run.py                    # Main entry point (keep in root)
├── setup_api_key.py         # Move to scripts/
└── run_tests.py             # Move to scripts/
```

### 5. Update .gitignore

**Add to .gitignore**:
```gitignore
# Test outputs
test_result_*.txt
*_test_result.json
*.bak

# Transcription outputs
transcripts/
*.txt

# Temporary files
*.tmp
*.temp
*_old.py
*_backup.py

# IDE specific
.cursor/
.idea/
.vscode/

# Cache
__pycache__/
*.pyc
.pytest_cache/
.mypy_cache/

# Environment
.env
.env.local
.env.*.local

# OS files
.DS_Store
Thumbs.db
```

## 🎯 Implementation Commands

### Phase 1: Backup Current State (2 minutes)
```bash
# Create backup branch
git checkout -b pre-cleanup-backup
git add -A
git commit -m "backup: pre-cleanup state"
git checkout dev
```

### Phase 2: Create New Structure (5 minutes)
```bash
# Create directories
mkdir -p tests/{unit,integration,fixtures,diagnostics}
mkdir -p docs/{developer,architecture,guides}
mkdir -p scripts

# Move test files
mv test_*diarization*.py tests/integration/
mv test_backends.py tests/integration/
mv test_integration.py tests/integration/
mv test_whisper_*.py tests/integration/
mv test_real_audio.py tests/fixtures/
mv test_transcription_monitor.py tests/unit/

# Move diagnostic tools
mv mock_whisper_server.py tests/fixtures/
mv diagnose_cuda_diarization.py tests/diagnostics/

# Move documentation
mv ONBOARDING.md docs/developer/
mv QUICKSTART.md docs/developer/
mv TRANSCRIPTION_BACKENDS.md docs/architecture/
mv WHISPER_DIARIZATION_FIX.md docs/architecture/

# Move scripts
mv setup_api_key.py scripts/
mv run_tests.py scripts/
```

### Phase 3: Remove Duplicates and Temp Files (5 minutes)
```bash
# Remove backup files
rm -f src/core/whisper_transcriber.py.bak
rm -f src/core/whisper_transcriber_improved.py

# Remove test outputs
rm -f test_result_*.txt
rm -f whisper_test_result.json

# Clean transcripts directory
rm -rf transcripts/*.txt

# Remove other temporary files
find . -name "*.bak" -delete
find . -name "*_old.py" -delete
find . -name "*_backup.py" -delete
```

### Phase 4: Update Imports (10 minutes)
```python
# Update imports in moved files
# Example for test files:
# OLD: from src.core.transcriber import Transcriber
# NEW: from src.core.transcriber import Transcriber (no change needed)

# Update run.py if scripts were referenced
# Update any documentation references
```

### Phase 5: Update Configuration Files (5 minutes)
```bash
# Update pytest.ini
cat > pytest.ini << 'EOF'
[tool.pytest.ini_options]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
EOF

# Update pyproject.toml or setup.cfg for test discovery
```

### Phase 6: Commit Cleanup (3 minutes)
```bash
# Stage changes
git add -A

# Review what will be committed
git status

# Commit with detailed message
git commit -m "refactor: major repository cleanup and reorganization

- Move all test files from root to tests/ directory structure
- Remove duplicate whisper_transcriber files
- Organize documentation into docs/ subdirectories  
- Move utility scripts to scripts/ directory
- Remove temporary files and test outputs
- Update .gitignore with comprehensive patterns
- Create proper test directory structure (unit/integration/fixtures)

This cleanup improves repository organization and reduces clutter
before the main refactoring effort begins."
```

## 📊 Before/After Metrics

### Before Cleanup:
- Root directory files: 35+
- Test files in root: 11
- Duplicate transcriber files: 2
- Backup files: 3
- Documentation files in root: 7

### After Cleanup:
- Root directory files: ~10 (only essential)
- Test files in root: 0 (all in tests/)
- Duplicate files: 0
- Backup files: 0
- Documentation organized in docs/

### Benefits:
- ✅ 70% reduction in root directory clutter
- ✅ Clear separation of concerns
- ✅ Improved test organization
- ✅ Better documentation structure
- ✅ Cleaner git history
- ✅ Easier navigation for developers

## ⚠️ Important Notes

1. **Keep CLAUDE.md in root** - Required for Claude Code integration
2. **Keep README.md in root** - GitHub standard
3. **Keep CHANGELOG.md in root** - Standard practice
4. **Keep run.py in root** - Main entry point
5. **Backup before cleanup** - Create branch first

## 🔄 Rollback Plan

If cleanup causes issues:
```bash
# Revert to backup branch
git checkout pre-cleanup-backup

# Or revert the cleanup commit
git revert HEAD
```

## Next Steps After Cleanup

1. Run tests to ensure nothing broke
2. Update CI/CD paths if needed
3. Update documentation with new file locations
4. Proceed with main refactoring plan

Total time: **30 minutes** for complete cleanup