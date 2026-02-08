# Archived Scripts

These scripts are kept for reference but are no longer used in active development.

## Golden File Generation (Replaced)

**Replaced by:** `generate_golden_datasets.py`

- `generate_echo_golden_files.py` - Manual golden file generation for echo bot
- `generate_json_golden_files.py` - JSON golden file generation (required running bot)
- `convert_xml_to_json_golden.py` - XML to JSON conversion utility

### Why Replaced?

The new unified `generate_golden_datasets.py` script:
- ✅ Automatically starts .NET bots (no manual setup)
- ✅ Generates golden files for all samples
- ✅ Uses .NET as canonical source
- ✅ Handles bot lifecycle management
- ✅ More robust error handling

See:
- `../generate_golden_datasets.py` - The new script
- `../../test-data/results/README.md` - Full documentation
- `../../.workspace/GOLDEN_DATASET_UPDATES.md` - Migration guide

## Cross-Platform Validation (Needs Update)

- `validate-outputs.py` - Validates Python vs .NET output consistency

### Why Archived?

This script uses the old directory structure:
- Old: `test-data/results/python/`, `test-data/results/shared/`
- New: `test-data/results/{sample}/golden/`

Needs to be updated to:
1. Read from new sample-based structure
2. Validate all languages against .NET golden files
3. Report cross-platform differences

## Migration Scripts (Completed)

These one-time migration scripts have been completed and are no longer needed:

### Documentation Migrations
- `migration/migrate-docs-content-to-typespec.py` - Migrated docs to TypeSpec format
- `migration/migrate-typespec-docs.py` - Migrated TypeSpec documentation format
- `refactor/split-docs-content.py` - Split large documentation files

These are kept for historical reference in case similar migrations are needed in the future.

## Using Archived Scripts

⚠️ **Warning:** These scripts may not work with the current codebase structure.

If you need functionality from an archived script:
1. Check if it's been replaced by a newer script
2. Review the "Why Archived?" section
3. Update the script for current structure before using
4. Consider whether the functionality should be restored or reimplemented

## Restoring Scripts

To restore a script from archive:
1. Update it for current structure
2. Test thoroughly
3. Move back to appropriate directory
4. Update relevant README.md
5. Remove from this archive README

---

## Notes

- Scripts in `.archive/` are not maintained
- They may reference old file structures or APIs
- Consult git history for context on when/why they were used
- Safe to delete if disk space is a concern
