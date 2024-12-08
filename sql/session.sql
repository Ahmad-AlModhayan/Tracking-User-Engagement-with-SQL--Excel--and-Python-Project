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

-- Sanity Check: Verify row count
SELECT COUNT(*) AS total_rows_2021 FROM minutes_watched_2021;  -- Expected: 7,639 rows
