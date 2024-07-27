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
            WHERE inner_hs.file
