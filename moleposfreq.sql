

drop function adjust_percentages;
drop table if exists adjusted;
start transaction;
set schema 'data';
create temporary table xx as select regexp_replace(lemma_gigpos, '[^A-Za-z-].*','') as pos , sum(1) as aantal from lemmata 
where keurmerk and online and not (lemma_gigpos ~ 'RES') group by regexp_replace(lemma_gigpos, '[^A-Za-z-].*','') ;
create temporary table x as select sum(aantal) + 0.0 as totaal from xx;
alter table xx add column percentage real;
update xx set percentage = 100 * aantal / totaal from x;



CREATE OR REPLACE FUNCTION adjust_percentages()
RETURNS TABLE (pos_new text, adjusted_percentage numeric) AS $$
DECLARE
    total numeric := 0;
    delta numeric;
    sorted_data RECORD;
BEGIN
    -- Create a temporary table to store intermediate results
    CREATE TEMP TABLE temp_percentages AS
    SELECT pos, ROUND(percentage::numeric, 2) AS rounded_percentage
    FROM xx;

    -- Calculate the total after rounding
    SELECT SUM(rounded_percentage) INTO total FROM temp_percentages;

    -- Compute the difference to adjust
    delta := 100 - total;

    -- Adjust values iteratively until delta is zero
    FOR sorted_data IN
        SELECT pos, rounded_percentage
        FROM temp_percentages
        ORDER BY (CASE WHEN delta > 0 THEN rounded_percentage - FLOOR(rounded_percentage)
                       ELSE CEIL(rounded_percentage) - rounded_percentage END) DESC
    LOOP
        IF delta = 0 THEN
            EXIT;
        END IF;

        -- Adjust one value by 0.01
        UPDATE temp_percentages
        SET rounded_percentage = rounded_percentage + (CASE WHEN delta > 0 THEN 0.01 ELSE -0.01 END)
        WHERE pos = sorted_data.pos;

        -- Update delta
        delta := delta - (CASE WHEN delta > 0 THEN 0.01 ELSE -0.01 END);
    END LOOP;

    -- Return the final adjusted percentages
    RETURN QUERY
    SELECT pos, rounded_percentage FROM temp_percentages;

    -- Clean up temporary table
    DROP TABLE temp_percentages;
END;
$$ LANGUAGE plpgsql;

drop table if exists adjusted;
alter table xx add column percentage_x real;
update xx set percentage_x=percentage;
create temporary table adjusted as select * from adjust_percentages();
select * from adjusted order by adjusted_percentage desc;
select sum(adjusted_percentage) from adjusted;
select * from xx order by percentage desc;

create table sonarfreq (pos text, freq real);
\copy sonarfreq from 'aapje.tsv';
select sum(freq) from sonarfreq;
select * from sonarfreq;
rollback;
