-- Step 1: Set up the database environment
USE data_scientist_project;

-- Step 2: Create a result set to calculate subscription end dates
DROP TABLE IF EXISTS subscription_end_dates;
CREATE TABLE subscription_end_dates AS
SELECT 
    sp.purchase_id,
    sp.student_id,
    sp.plan_id,
    sp.date_purchased AS date_start,
    CASE 
        WHEN sp.plan_id = 0 THEN DATE_ADD(sp.date_purchased, INTERVAL 1 MONTH)  -- Monthly Plan
        WHEN sp.plan_id = 1 THEN DATE_ADD(sp.date_purchased, INTERVAL 3 MONTH)  -- Quarterly Plan
        WHEN sp.plan_id = 2 THEN DATE_ADD(sp.date_purchased, INTERVAL 12 MONTH) -- Annual Plan
        WHEN sp.plan_id = 3 THEN NULL                                          -- Lifetime Plan
    END AS date_end
FROM 
    student_purchases sp;

-- Sanity Check: Ensure the number of rows matches expectations
SELECT COUNT(*) AS total_rows FROM subscription_end_dates;

-- Step 3: Update date_end to terminate at the refund date for refunded orders
DROP TABLE IF EXISTS adjusted_subscription_end_dates;
CREATE TABLE adjusted_subscription_end_dates AS
SELECT 
    sed.purchase_id,
    sed.student_id,
    sed.plan_id,
    sed.date_start,
    CASE 
        WHEN sp.date_refunded IS NOT NULL THEN sp.date_refunded  -- Use refund date if available
        ELSE sed.date_end  -- Otherwise, keep the original end date
    END AS date_end
FROM 
    subscription_end_dates sed
LEFT JOIN 
    student_purchases sp ON sed.purchase_id = sp.purchase_id;

-- Sanity Check: Ensure the number of rows matches expectations
SELECT COUNT(*) AS total_rows FROM adjusted_subscription_end_dates;

-- Step 4: Create the purchases_info view with paid columns
DROP VIEW IF EXISTS purchases_info;
CREATE VIEW purchases_info AS
SELECT 
    ase.purchase_id,
    ase.student_id,
    ase.plan_id,
    ase.date_start,
    ase.date_end,
    CASE 
        WHEN ase.date_start <= '2021-06-30' AND (ase.date_end IS NULL OR ase.date_end >= '2021-04-01') THEN 1
        ELSE 0
    END AS paid_q2_2021,
    CASE 
        WHEN ase.date_start <= '2022-06-30' AND (ase.date_end IS NULL OR ase.date_end >= '2022-04-01') THEN 1
        ELSE 0
    END AS paid_q2_2022
FROM 
    adjusted_subscription_end_dates ase;

-- Sanity Check: Verify the data in the purchases_info view
SELECT * FROM purchases_info LIMIT 10;

-- Verify active subscriptions in Q2 2021
SELECT COUNT(*) AS paid_q2_2021_count FROM purchases_info WHERE paid_q2_2021 = 1;

-- Verify active subscriptions in Q2 2022
SELECT COUNT(*) AS paid_q2_2022_count FROM purchases_info WHERE paid_q2_2022 = 1;
