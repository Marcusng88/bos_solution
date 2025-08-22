# Database Consolidation Plan: Migrate from my_competitors to competitors table

## Overview
This document outlines the step-by-step process to consolidate the database schema and codebase to use only the `competitors` table instead of the `my_competitors` table. The goal is to eliminate duplication and ensure all competitor-related operations use a single, unified table structure.

## Current State Analysis

### Current Tables Structure

#### `competitors` table (13 columns)
- `id` (UUID, Primary Key)
- `user_id` (VARCHAR(255), NOT NULL)
- `name` (VARCHAR(255), NOT NULL)
- `description` (TEXT, nullable)
- `website_url` (VARCHAR(500), nullable)
- `social_media_handles` (JSONB, nullable) - Store platform:handle mappings
- `platforms` (TEXT[], nullable) - Array of platforms to monitor (e.g., ["youtube", "instagram", "twitter"])
- `industry` (VARCHAR(100), nullable)
- `status` (monitoring_status, default 'active')
- `created_at` (TIMESTAMPTZ, default NOW())
- `updated_at` (TIMESTAMPTZ, default NOW())
- `last_scan_at` (TIMESTAMPTZ, nullable)
- `scan_frequency_minutes` (INTEGER, default 60)

#### `my_competitors` table (7 columns)
- `id` (UUID, Primary Key)
- `user_id` (VARCHAR(255), NOT NULL)
- `competitor_name` (VARCHAR(255), NOT NULL)
- `website_url` (VARCHAR(500), nullable)
- `active_platforms` (TEXT[], NOT NULL)
- `created_at` (TIMESTAMPTZ, default NOW())
- `updated_at` (TIMESTAMPTZ, default NOW())

### Key Differences to Resolve
1. **Column mapping**:
   - `my_competitors.competitor_name` → `competitors.name`
   - `my_competitors.active_platforms` → `competitors.platforms` (keep as TEXT[] array)
   - `competitors.social_media_handles` remains as JSONB for storing actual handle values
2. **Missing columns in competitors**: Need to add default values for new columns
3. **Data migration**: Existing data in `my_competitors` needs to be moved to `competitors`
4. **Dual platform storage**: 
   - `platforms` (TEXT[]) stores which platforms to monitor
   - `social_media_handles` (JSONB) stores actual handle values like {"youtube": "@username", "instagram": "@handle"}

## Step-by-Step Implementation Plan

### Phase 1: Database Schema Updates

#### Step 1.1: Update database_schema.sql
**File**: `bos_solution/database_schema.sql`

**Changes needed**:
1. **Remove the `my_competitors` table** completely (lines 320-335)
2. **Update the `competitors` table** to ensure it has all necessary columns:
   - Verify `status` column has default 'active'
   - Verify `last_scan_at` and `scan_frequency_minutes` have appropriate defaults
   - **Add `platforms` column** (TEXT[]) to store which platforms to monitor
   - Ensure `social_media_handles` (JSONB) can store actual handle values
   - Ensure `platforms` (TEXT[]) can store platform arrays like ["youtube", "instagram"]

**Specific changes**:
```sql
-- Remove this entire section:
-- CREATE TABLE my_competitors ( ... );

-- Add platforms column to competitors table if it doesn't exist:
ALTER TABLE competitors ADD COLUMN IF NOT EXISTS platforms TEXT[];

-- Update competitors table constraints if needed:
ALTER TABLE competitors ALTER COLUMN status SET DEFAULT 'active';
ALTER TABLE competitors ALTER COLUMN scan_frequency_minutes SET DEFAULT 60;
```

#### Step 1.2: Update database.py
**File**: `bos_solution/backend/app/core/database.py`

**Changes needed**:
1. **Remove any references** to `my_competitors` table
2. **Ensure Base class** is properly configured for the `competitors` table
3. **Update any table creation logic** to only create the `competitors` table

### Phase 2: Model Updates

#### Step 2.1: Update Competitor Model
**File**: `bos_solution/backend/app/models/competitor.py`

**Changes needed**:
1. **Verify all columns** match the updated database schema
2. **Add default values** for new columns:
   - `status` default to 'active'
   - `last_scan_at` default to NULL
   - `scan_frequency_minutes` default to 60
3. **Ensure proper relationships** with other tables

#### Step 2.2: Remove MyCompetitor Model
**File**: `bos_solution/backend/app/models/my_competitor.py`

**Action**: **Delete this file completely**

**Reason**: No longer needed since we're consolidating to the `competitors` table

### Phase 3: Service Layer Updates

#### Step 3.1: Update Monitoring Service
**File**: `bos_solution/backend/app/services/monitoring_service.py`

**Changes needed**:
1. **Update all references** from `MyCompetitor` to `Competitor`
2. **Update import statements** to use the correct model
3. **Verify all database queries** use the `competitors` table
4. **Update any hardcoded table names** in SQL queries

#### Step 3.2: Update Supabase Client
**File**: `bos_solution/backend/app/core/supabase_client.py`

**Changes needed**:
1. **Replace all `my_competitors` table references** with `competitors`
2. **Update column mappings**:
   - `competitor_name` → `name`
   - `active_platforms` → `platforms` (keep as TEXT[] array)
   - `social_media_handles` remains as JSONB for storing actual handle values
3. **Update all CRUD operations** to use the correct table and column names
4. **Handle data transformation**:
   - `active_platforms` array → `platforms` array (direct mapping)
   - `social_media_handles` JSONB for storing actual handle values when available

**Specific method updates needed**:
- `create_competitor()` → use `competitors` table
- `get_user_competitors()` → use `competitors` table
- `update_competitor()` → use `competitors` table
- `delete_competitor()` → use `competitors` table

### Phase 4: API Endpoint Updates

#### Step 4.1: Update Competitors Endpoint
**File**: `bos_solution/backend/app/api/v1/endpoints/competitors.py`

**Changes needed**:
1. **Update all database operations** to use `competitors` table
2. **Update column mappings** in request/response models
3. **Handle data transformation** for platform arrays
4. **Update validation logic** for new required fields

#### Step 4.2: Update My Competitors Endpoint
**File**: `bos_solution/backend/app/api/v1/endpoints/my_competitors.py`

**Action**: **Delete this file completely**

**Reason**: Functionality will be consolidated into the main `competitors` endpoint

#### Step 4.3: Update API Router
**File**: `bos_solution/backend/app/api/v1/api.py`

**Changes needed**:
1. **Remove import** for `my_competitors` endpoint
2. **Remove router inclusion** for `my_competitors`
3. **Ensure all competitor operations** go through the main `competitors` endpoint

### Phase 5: Frontend Updates

#### Step 5.1: Update API Client
**File**: `bos_solution/frontend/lib/api-client.ts` (or similar)

**Changes needed**:
1. **Update all API calls** to use `/competitors` endpoint instead of `/my-competitors`
2. **Update data transformation** for platform arrays:
   - Frontend sends: `platforms: ["youtube", "instagram"]`
   - Backend stores: `platforms: ["youtube", "instagram"]` (direct array mapping)
   - `social_media_handles` can store actual handle values like `{"youtube": "@username", "instagram": "@handle"}`
3. **Update response handling** to work with new column names

#### Step 5.2: Update Settings Wizard
**File**: `bos_solution/frontend/components/settings/settings-wizard.tsx`

**Changes needed**:
1. **Update API calls** to use the correct endpoint
2. **Update data transformation** for platform arrays
3. **Ensure proper error handling** for the new table structure

#### Step 5.3: Update Competitor Step Component
**File**: `bos_solution/frontend/components/onboarding/steps/competitor-step.tsx`

**Changes needed**:
1. **Update data structure** to match new table schema
2. **Update API calls** to use correct endpoint
3. **Handle platform array** to JSONB conversion

### Phase 6: Data Migration

#### Step 6.1: Create Migration Script
**File**: `bos_solution/backend/migrate_competitors.py`

**Purpose**: Migrate existing data from `my_competitors` to `competitors`

**Migration logic**:
```python
# For each record in my_competitors:
# 1. Map active_platforms array directly to platforms array (TEXT[])
# 2. Map competitor_name to name
# 3. Set default values for new columns (status='active', scan_frequency_minutes=60)
# 4. Initialize social_media_handles as empty JSONB {} (can be populated later)
# 5. Insert into competitors table
# 6. Update any foreign key references
```

#### Step 6.2: Execute Migration
**Steps**:
1. **Backup database** before migration
2. **Run migration script** to move data
3. **Verify data integrity** after migration
4. **Drop my_competitors table** after successful migration

### Phase 7: Testing & Validation

#### Step 7.1: Unit Tests
**Files to update**:
- All test files that reference `my_competitors`
- Update test data to use new table structure
- Verify all CRUD operations work correctly

#### Step 7.2: Integration Tests
**Test scenarios**:
1. **Create competitor** through onboarding
2. **Edit competitor** in settings
3. **Delete competitor** from settings
4. **Monitor competitor** activity
5. **Generate alerts** for competitor changes

#### Step 7.3: End-to-End Tests
**Test user flows**:
1. **Complete onboarding** with competitor setup
2. **Access settings** and modify competitors
3. **View competitor monitoring** dashboard
4. **Receive alerts** for competitor changes

## Implementation Order

### Priority 1 (Critical - Must be done first)
1. Update database schema
2. Update models
3. Update services
4. Update API endpoints

### Priority 2 (High - Must be done before testing)
1. Update frontend API client
2. Update frontend components
3. Create migration script

### Priority 3 (Medium - Can be done during testing)
1. Execute data migration
2. Drop old table
3. Update tests

### Priority 4 (Low - Can be done after deployment)
1. Clean up old code references
2. Update documentation
3. Performance optimization

## Risk Mitigation

### Data Loss Prevention
- **Always backup database** before schema changes
- **Test migration script** on copy of production data
- **Verify data integrity** after each migration step

### Rollback Plan
- **Keep old table** until migration is verified
- **Maintain backward compatibility** during transition
- **Have rollback scripts** ready if issues arise

### Testing Strategy
- **Unit test** all changes before integration
- **Integration test** with real database
- **User acceptance testing** with sample data

## Success Criteria

### Technical Success
- [ ] All competitor operations use `competitors` table (13 columns)
- [ ] No references to `my_competitors` table remain
- [ ] All CRUD operations work correctly with new column structure
- [ ] Data migration completed successfully
- [ ] Both `platforms` (TEXT[]) and `social_media_handles` (JSONB) columns work correctly

### Functional Success
- [ ] Onboarding competitor setup works
- [ ] Settings competitor management works
- [ ] Competitor monitoring works
- [ ] All existing functionality preserved

### Performance Success
- [ ] No performance degradation
- [ ] Database queries optimized
- [ ] Response times maintained or improved

## Post-Implementation Tasks

### Cleanup
1. **Remove old files** (my_competitor.py, my_competitors endpoint)
2. **Update documentation** to reflect new structure
3. **Remove unused imports** and dependencies

### Monitoring
1. **Watch for errors** in competitor operations
2. **Monitor performance** of new table structure
3. **Verify data integrity** over time

### Documentation
1. **Update API documentation** with new endpoints
2. **Update database schema documentation**
3. **Create migration guide** for future reference

## Timeline Estimate

- **Phase 1-2 (Schema & Models)**: 2-3 hours
- **Phase 3-4 (Services & API)**: 4-6 hours
- **Phase 5 (Frontend)**: 3-4 hours
- **Phase 6 (Migration)**: 2-3 hours
- **Phase 7 (Testing)**: 4-6 hours
- **Total estimated time**: 15-22 hours

## Notes

- **Always test** changes in development environment first
- **Use feature flags** if possible to gradually roll out changes
- **Monitor logs** closely during and after implementation
- **Have rollback plan** ready for any critical issues
- **Communicate changes** to team members and stakeholders
