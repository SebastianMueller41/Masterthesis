-- Set the variable
SET @pattern = '%ARG/%';

-- Use the variable in the query
WITH AllCombinations AS (
    SELECT dc.div_conq, sw.sw_size, sp.strategy_param
    FROM (SELECT 0 AS div_conq UNION ALL SELECT 1) AS dc
    CROSS JOIN (SELECT 1 AS sw_size UNION ALL SELECT 5 UNION ALL SELECT 10) AS sw
    CROSS JOIN (SELECT 0 AS strategy_param UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3) AS sp
),

ExistingResults AS (
    SELECT 
        file_name,
        SUBSTRING(file_name, LENGTH(file_name)) AS dataset,
        div_conq, sw_size, strategy_param
    FROM EXE_RESULTS.RESULTS_OLD
    WHERE file_name LIKE @pattern
),

DatasetCombinations AS (
    SELECT DISTINCT er.file_name, er.dataset, ac.div_conq, ac.sw_size, ac.strategy_param
    FROM ExistingResults er
    CROSS JOIN AllCombinations ac
),

DatasetLengths AS (
    SELECT 
        SUBSTRING(filename, LENGTH(filename)) AS dataset,
        COUNT(id) AS dataset_length
    FROM EXE_RESULTS.DATA_ENTRY
    WHERE filename LIKE @pattern
    GROUP BY SUBSTRING(filename, LENGTH(filename))
)

SELECT 
    dc.file_name,
    dc.div_conq, 
    dc.sw_size, 
    dc.strategy_param,
    dl.dataset_length
FROM DatasetCombinations dc
LEFT JOIN ExistingResults er
ON dc.dataset = er.dataset
AND dc.div_conq = er.div_conq
AND dc.sw_size = er.sw_size
AND dc.strategy_param = er.strategy_param
LEFT JOIN DatasetLengths dl
ON dc.dataset = dl.dataset
WHERE er.dataset IS NULL
AND dl.dataset_length > dc.sw_size
ORDER BY dc.dataset, dc.div_conq, dc.sw_size, dc.strategy_param;
