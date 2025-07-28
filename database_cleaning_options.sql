-- NOMADLY2 DATABASE CLEANING OPTIONS
-- Choose the appropriate option based on your needs

-- ============================================================================
-- OPTION 1: CLEAN TEST USERS ONLY (SAFE)
-- Removes obvious test users while keeping real users and main user
-- ============================================================================

-- Remove empty test user (NomadlySMS - no data)
DELETE FROM users WHERE telegram_id = '1531772316';

-- Remove duplicate test user (6789012345 - duplicate onarrival1)
DELETE FROM orders WHERE telegram_id = '6789012345';
DELETE FROM users WHERE telegram_id = '6789012345';

-- Remove obvious test user (1111111111 - fake ID pattern)
DELETE FROM registered_domains WHERE telegram_id = '1111111111';
DELETE FROM orders WHERE telegram_id = '1111111111';
DELETE FROM users WHERE telegram_id = '1111111111';

-- ============================================================================
-- OPTION 2: CLEAN UNMANAGEABLE DOMAINS (RECOMMENDED)
-- Removes domains that can't be managed (not in OpenProvider account)
-- ============================================================================

-- Show unmanageable domains first
SELECT 
    domain_name, 
    telegram_id, 
    openprovider_domain_id,
    created_at
FROM registered_domains 
WHERE openprovider_domain_id = 'not_manageable_account_mismatch'
   OR openprovider_domain_id ~ '^[^0-9]+$'
ORDER BY created_at;

-- Remove unmanageable domains (UNCOMMENT to execute)
-- DELETE FROM registered_domains 
-- WHERE openprovider_domain_id = 'not_manageable_account_mismatch'
--    OR openprovider_domain_id ~ '^[^0-9]+$';

-- ============================================================================
-- OPTION 3: KEEP ONLY PRODUCTION USERS (MODERATE)
-- Keeps main user (5590563715) and real customer (folly542)
-- ============================================================================

-- Remove all test users and their data
-- DELETE FROM registered_domains WHERE telegram_id NOT IN ('5590563715', '6896666427');
-- DELETE FROM orders WHERE telegram_id NOT IN ('5590563715', '6896666427');
-- DELETE FROM users WHERE telegram_id NOT IN ('5590563715', '6896666427');

-- ============================================================================
-- OPTION 4: FRESH START (NUCLEAR - KEEP ONLY MAIN USER)
-- Keeps only the main development user
-- ============================================================================

-- DELETE FROM registered_domains WHERE telegram_id != '5590563715';
-- DELETE FROM orders WHERE telegram_id != '5590563715';
-- DELETE FROM users WHERE telegram_id != '5590563715';

-- ============================================================================
-- OPTION 5: COMPLETE RESET (DANGEROUS)
-- Removes ALL user data - use for fresh production deployment
-- ============================================================================

-- TRUNCATE registered_domains CASCADE;
-- TRUNCATE orders CASCADE;
-- TRUNCATE users CASCADE;

-- ============================================================================
-- VERIFICATION QUERIES
-- Run these after cleaning to verify results
-- ============================================================================

-- Check final counts
SELECT 
    'Users' as table_name, 
    COUNT(*) as count 
FROM users
UNION ALL
SELECT 
    'Domains' as table_name, 
    COUNT(*) as count 
FROM registered_domains
UNION ALL
SELECT 
    'Orders' as table_name, 
    COUNT(*) as count 
FROM orders;

-- Check remaining users
SELECT 
    telegram_id,
    username,
    created_at,
    (SELECT COUNT(*) FROM registered_domains WHERE telegram_id = u.telegram_id) as domains,
    (SELECT COUNT(*) FROM orders WHERE telegram_id = u.telegram_id) as orders
FROM users u
ORDER BY created_at;