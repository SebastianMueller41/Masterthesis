SET SQL_SAFE_UPDATES = 0;


CREATE TABLE EXE_RESULTS.OPTIMAL_BU SELECT * FROM EXE_RESULTS.OPTIMAL

/*
UPDATE EXE_RESULTS.OPTIMAL o
JOIN (
    SELECT 
        hs.filename,
        MAX(hs.cardinality) AS max_cardinality,
        MAX(hs.random_sum) AS max_random_value,
        MAX(hs.inconsistency_sum) AS max_incon_value,
        MIN(hs.random_sum) AS min_random_value,
        MIN(hs.inconsistency_sum) AS min_incon_value,
        MIN(hs.cardinality) AS min_cardinality,
        COUNT(*) AS num_leafs,
        (
            SELECT MIN(inner_hs.cardinality)
            FROM EXE_RESULTS.HITTING_SETS inner_hs
            WHERE inner_hs.filename = hs.filename
              AND inner_hs.random_sum = (
                  SELECT MAX(max_hs.random_sum)
                  FROM EXE_RESULTS.HITTING_SETS max_hs
                  WHERE max_hs.filename = hs.filename
              )
        ) AS card_max_random,
        (
            SELECT MIN(inner_hs.cardinality)
            FROM EXE_RESULTS.HITTING_SETS inner_hs
            WHERE inner_hs.filename = hs.filename
              AND inner_hs.inconsistency_sum = (
                  SELECT MAX(max_hs.inconsistency_sum)
                  FROM EXE_RESULTS.HITTING_SETS max_hs
                  WHERE max_hs.filename = hs.filename
              )
        ) AS card_max_incon,
        (
            SELECT MIN(inner_hs.cardinality)
            FROM EXE_RESULTS.HITTING_SETS inner_hs
            WHERE inner_hs.filename = hs.filename
              AND inner_hs.random_sum = (
                  SELECT MIN(min_hs.random_sum)
                  FROM EXE_RESULTS.HITTING_SETS min_hs
                  WHERE min_hs.filename = hs.filename
              )
        ) AS card_min_random,
        (
            SELECT MIN(inner_hs.cardinality)
            FROM EXE_RESULTS.HITTING_SETS inner_hs
            WHERE inner_hs.filename = hs.filename
              AND inner_hs.inconsistency_sum = (
                  SELECT MIN(min_hs.inconsistency_sum)
                  FROM EXE_RESULTS.HITTING_SETS min_hs
                  WHERE min_hs.filename = hs.filename
              )
        ) AS card_min_incon,
        (
            SELECT MIN(inner_hs.cardinality)
            FROM EXE_RESULTS.HITTING_SETS inner_hs
            WHERE inner_hs.filename = hs.filename
              AND inner_hs.random_sum = (
                  SELECT MAX(max_hs.random_sum)
                  FROM EXE_RESULTS.HITTING_SETS max_hs
                  WHERE max_hs.filename = hs.filename
              )
        ) AS min_card_max_value_random,
        (
            SELECT MIN(inner_hs.cardinality)
            FROM EXE_RESULTS.HITTING_SETS inner_hs
            WHERE inner_hs.filename = hs.filename
              AND inner_hs.inconsistency_sum = (
                  SELECT MAX(max_hs.inconsistency_sum)
                  FROM EXE_RESULTS.HITTING_SETS max_hs
                  WHERE max_hs.filename = hs.filename
              )
        ) AS min_card_max_value_incon
    FROM EXE_RESULTS.HITTING_SETS hs
    GROUP BY hs.filename
) sub ON o.filename = sub.filename
SET 
    o.max_cardinality = sub.max_cardinality,
    o.max_random_value = sub.max_random_value,
    o.max_incon_value = sub.max_incon_value,
    o.min_random_value = sub.min_random_value,
    o.min_incon_value = sub.min_incon_value,
    o.min_cardinality = sub.min_cardinality,
    o.num_leafs = sub.num_leafs,
    o.card_max_random = sub.card_max_random,
    o.card_max_incon = sub.card_max_incon,
    o.card_min_random = sub.card_min_random,
    o.card_min_incon = sub.card_min_incon,
    o.min_card_max_value_random = sub.min_card_max_value_random,
    o.min_card_max_value_incon = sub.min_card_max_value_incon
WHERE o.execution_time IS NOT NULL;
*/

#DELETE FROM EXE_RESULTS.HITTING_SETS where filename like '%sig10_15_25/srs_%'

#DELETE FROM EXE_RESULTS.HITTING_SETS WHERE ID = 22744

#USE EXE_RESULTS;

#DELETE FROM EXE_RESULTS.RESULTS WHERE filename like '%sig5_15%';

#DELETE FROM EXE_RESULTS.RESULTS WHERE pruner = 'LOWER';

#ALTER TABLE EXE_RESULTS.RESULTS RENAME COLUMN optimal_value_incon TO max_incon_value;

#UPDATE EXE_RESULTS.RESULTS SET optimal_cardinality = JSON_LENGTH(optimal_solution);

#DELETE FROM EXE_RESULTS.RESULTS where filename like '%10_15_25%';


