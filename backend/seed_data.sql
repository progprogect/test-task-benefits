-- Seed data for Benefit Reimbursement System
-- Run this script after migrations to populate initial data

-- Insert benefit categories (only if they don't exist)
INSERT INTO benefit_categories (id, name, max_transaction_amount, annual_limit, monthly_limit, created_at, updated_at)
SELECT gen_random_uuid(), 'Wellness & Fitness', 500.00, 5000.00, 500.00, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM benefit_categories WHERE name = 'Wellness & Fitness');

INSERT INTO benefit_categories (id, name, max_transaction_amount, annual_limit, monthly_limit, created_at, updated_at)
SELECT gen_random_uuid(), 'Professional Development', 1000.00, 3000.00, 500.00, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM benefit_categories WHERE name = 'Professional Development');

INSERT INTO benefit_categories (id, name, max_transaction_amount, annual_limit, monthly_limit, created_at, updated_at)
SELECT gen_random_uuid(), 'Home Office Equipment', 2000.00, 5000.00, 1000.00, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM benefit_categories WHERE name = 'Home Office Equipment');

INSERT INTO benefit_categories (id, name, max_transaction_amount, annual_limit, monthly_limit, created_at, updated_at)
SELECT gen_random_uuid(), 'Transportation', 200.00, 2000.00, 300.00, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM benefit_categories WHERE name = 'Transportation');

INSERT INTO benefit_categories (id, name, max_transaction_amount, annual_limit, monthly_limit, created_at, updated_at)
SELECT gen_random_uuid(), 'Health & Medical', 500.00, 3000.00, 500.00, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM benefit_categories WHERE name = 'Health & Medical');

-- Insert keywords for Wellness & Fitness
INSERT INTO category_keywords (id, category_id, keyword, created_at)
SELECT gen_random_uuid(), bc.id, kw.keyword, NOW()
FROM benefit_categories bc,
     (VALUES ('gym'), ('fitness'), ('yoga'), ('workout'), ('exercise'), ('sports'), ('personal trainer'), ('fitness center')) AS kw(keyword)
WHERE bc.name = 'Wellness & Fitness'
AND NOT EXISTS (SELECT 1 FROM category_keywords ck WHERE ck.category_id = bc.id AND ck.keyword = kw.keyword);

-- Insert keywords for Professional Development
INSERT INTO category_keywords (id, category_id, keyword, created_at)
SELECT gen_random_uuid(), bc.id, kw.keyword, NOW()
FROM benefit_categories bc,
     (VALUES ('course'), ('training'), ('certification'), ('conference'), ('workshop'), ('book'), ('education'), ('learning')) AS kw(keyword)
WHERE bc.name = 'Professional Development'
AND NOT EXISTS (SELECT 1 FROM category_keywords ck WHERE ck.category_id = bc.id AND ck.keyword = kw.keyword);

-- Insert keywords for Home Office Equipment
INSERT INTO category_keywords (id, category_id, keyword, created_at)
SELECT gen_random_uuid(), bc.id, kw.keyword, NOW()
FROM benefit_categories bc,
     (VALUES ('monitor'), ('keyboard'), ('mouse'), ('desk'), ('chair'), ('laptop stand'), ('headphones'), ('webcam')) AS kw(keyword)
WHERE bc.name = 'Home Office Equipment'
AND NOT EXISTS (SELECT 1 FROM category_keywords ck WHERE ck.category_id = bc.id AND ck.keyword = kw.keyword);

-- Insert keywords for Transportation
INSERT INTO category_keywords (id, category_id, keyword, created_at)
SELECT gen_random_uuid(), bc.id, kw.keyword, NOW()
FROM benefit_categories bc,
     (VALUES ('taxi'), ('uber'), ('fuel'), ('parking'), ('public transport'), ('metro'), ('bus'), ('train')) AS kw(keyword)
WHERE bc.name = 'Transportation'
AND NOT EXISTS (SELECT 1 FROM category_keywords ck WHERE ck.category_id = bc.id AND ck.keyword = kw.keyword);

-- Insert keywords for Health & Medical
INSERT INTO category_keywords (id, category_id, keyword, created_at)
SELECT gen_random_uuid(), bc.id, kw.keyword, NOW()
FROM benefit_categories bc,
     (VALUES ('doctor'), ('medical'), ('pharmacy'), ('prescription'), ('health check'), ('clinic'), ('hospital')) AS kw(keyword)
WHERE bc.name = 'Health & Medical'
AND NOT EXISTS (SELECT 1 FROM category_keywords ck WHERE ck.category_id = bc.id AND ck.keyword = kw.keyword);

-- Insert employees
INSERT INTO employees (id, name, employee_id, created_at, updated_at)
SELECT gen_random_uuid(), 'John Smith', 'EMP001', NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM employees WHERE employee_id = 'EMP001');

INSERT INTO employees (id, name, employee_id, created_at, updated_at)
SELECT gen_random_uuid(), 'Sarah Johnson', 'EMP002', NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM employees WHERE employee_id = 'EMP002');

INSERT INTO employees (id, name, employee_id, created_at, updated_at)
SELECT gen_random_uuid(), 'Michael Brown', 'EMP003', NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM employees WHERE employee_id = 'EMP003');

INSERT INTO employees (id, name, employee_id, created_at, updated_at)
SELECT gen_random_uuid(), 'Emily Davis', 'EMP004', NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM employees WHERE employee_id = 'EMP004');

INSERT INTO employees (id, name, employee_id, created_at, updated_at)
SELECT gen_random_uuid(), 'David Wilson', 'EMP005', NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM employees WHERE employee_id = 'EMP005');
