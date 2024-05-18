CREATE TABLE DATA_SETS (filename varchar(307),  PRIMARY KEY (filename));
CREATE TABLE DATA_ENTRY (id int auto_increment, randomValue int, inconsistencyValue int, filename varchar(1024), PRIMARY KEY (id));
