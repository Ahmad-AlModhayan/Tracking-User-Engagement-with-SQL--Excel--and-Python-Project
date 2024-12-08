-- Step 1: Set up the database environment
USE data_scientist_project;

-- Step 2: Calculate Total Minutes Watched in Q2 2021
DROP TABLE IF EXISTS minutes_watched_2021;
CREATE TEMPORARY TABLE minutes_watched_2021 AS
SELECT 
    svw.student_id,
    SUM(svw.seconds_watched) / 60 AS minutes_watched  -- Convert seconds to minutes
FROM 
    student_video_watched svw
WHERE 
    svw.date_watched BETWEEN '2021-04-01' AND '2021-06-30'
GROUP BY 
    svw.student_id;

-- Sanity Check: Verify row count for Q2 2021
SELECT COUNT(*) AS total_rows_2021 FROM minutes_watched_2021;  -- Expected: 7,639 rows

-- Step 3: Calculate Total Minutes Watched in Q2 2022
DROP TABLE IF EXISTS minutes_watched_2022;
CREATE TEMPORARY TABLE minutes_watched_2022 AS
SELECT 
    svw.student_id,
    SUM(svw.seconds_watched) / 60 AS minutes_watched  -- Convert seconds to minutes
FROM 
    student_video_watched svw
WHERE 
    svw.date_watched BETWEEN '2022-04-01' AND '2022-06-30'
GROUP BY 
    svw.student_id;

-- Sanity Check: Verify row count for Q2 2022
SELECT COUNT(*) AS total_rows_2022 FROM minutes_watched_2022;  -- Expected: 8,841 rows

-- Step 4: Create Result Sets with Paid Column for Q2 2021
DROP TABLE IF EXISTS minutes_watched_2021_paid;
CREATE TEMPORARY TABLE minutes_watched_2021_paid AS
SELECT 
    mw.student_id,
    mw.minutes_watched,
    pi.paid_q2_2021 AS paid_in_q2
FROM 
    minutes_watched_2021 mw
INNER JOIN 
    purchases_info pi ON mw.student_id = pi.student_id;

-- Export Data for Q2 2021 (Free)
SELECT * FROM minutes_watched_2021_paid WHERE paid_in_q2 = 0 
INTO OUTFILE 'C:/ProgramData/MySQL/MySQL Server 8.4/Uploads/minutes_watched_2021_paid_0.csv'
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n';

-- Export Data for Q2 2021 (Paid)
SELECT * FROM minutes_watched_2021_paid WHERE paid_in_q2 = 1 
INTO OUTFILE 'C:/ProgramData/MySQL/MySQL Server 8.4/Uploads/minutes_watched_2021_paid_1.csv'
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n';

-- Step 5: Create Result Sets with Paid Column for Q2 2022
DROP TABLE IF EXISTS minutes_watched_2022_paid;
CREATE TEMPORARY TABLE minutes_watched_2022_paid AS
SELECT 
    mw.student_id,
    mw.minutes_watched,
    pi.paid_q2_2022 AS paid_in_q2
FROM 
    minutes_watched_2022 mw
INNER JOIN 
    purchases_info pi ON mw.student_id = pi.student_id;

-- Export Data for Q2 2022 (Free)
SELECT * FROM minutes_watched_2022_paid WHERE paid_in_q2 = 0 
INTO OUTFILE 'C:/ProgramData/MySQL/MySQL Server 8.4/Uploads/minutes_watched_2022_paid_0.csv'
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n';

-- Export Data for Q2 2022 (Paid)
SELECT * FROM minutes_watched_2022_paid WHERE paid_in_q2 = 1 
INTO OUTFILE 'C:/ProgramData/MySQL/MySQL Server 8.4/Uploads/minutes_watched_2022_paid_1.csv'
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n';

-- Step 6: Correlate Minutes Watched with Certificates Issued
DROP TABLE IF EXISTS minutes_and_certificates;
CREATE TEMPORARY TABLE minutes_and_certificates AS
SELECT 
    svw.student_id,
    SUM(svw.seconds_watched) / 60 AS total_minutes,
    COUNT(sc.certificate_id) AS certificates_issued
FROM 
    student_video_watched svw
LEFT JOIN 
    student_certificates sc ON svw.student_id = sc.student_id
GROUP BY 
    svw.student_id;

-- Export Data for Correlation Analysis
SELECT * FROM minutes_and_certificates
INTO OUTFILE 'C:/ProgramData/MySQL/MySQL Server 8.4/Uploads/minutes_and_certificates.csv'
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n';

-- Sanity Check: Verify row count for certificates issued
SELECT COUNT(*) AS total_rows_certificates FROM minutes_and_certificates;  -- Expected: 658 rows
