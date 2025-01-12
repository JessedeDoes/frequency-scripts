set schema 'data';
create temporary table xx as select regexp_replace(lemma_gigpos, '[^A-Za-z-].*','') , sum(1) as aantal from lemmata where keurmerk and online group by regexp_replace(lemma_gigpos, '[^A-Za-z-].*','') ;
create temporary table x as select sum(aantal) + 0.0 as totaal from xx;
alter table xx add column percentage real;
update xx set percentage = 100 * aantal / totaal from x;
select * from xx order by aantal desc;

