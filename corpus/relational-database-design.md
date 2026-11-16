# Relational database design for lab data

## Normalisation

Normalisation removes redundancy so that each fact is stored once. In first normal form every column holds a single value. In second normal form every non-key column depends on the whole primary key. In third normal form non-key columns depend only on the key, not on other non-key columns. For example, a TE family's classification belongs in the family table, not repeated on every genomic copy of that family.

## Keys and relations

A primary key identifies each row; a foreign key references a row in another table and the database rejects references to rows that do not exist. One-to-many relations (one sample, many sequencing runs) use a foreign key on the many side. Many-to-many relations (individuals and phenotypes) need a junction table with a composite primary key. CHECK constraints and triggers enforce rules such as coordinates lying within a chromosome.

## Querying

Joins combine tables; GROUP BY with aggregate functions summarises them; HAVING filters groups. Common table expressions (WITH) name intermediate results, and recursive CTEs walk hierarchies such as a classification tree stored as an adjacency list. Window functions (RANK, ROW_NUMBER, LAG, SUM OVER) compute rankings, running totals and comparisons with previous rows without collapsing the rows.

## Performance and safety

Indexes on the columns used in joins and range filters, such as (chromosome, start, end) for interval overlaps, avoid full table scans; EXPLAIN QUERY PLAN shows whether they are used. User input must be passed as query parameters, never pasted into the SQL string, to prevent SQL injection. Personal data in a biobank should be pseudonymised.
