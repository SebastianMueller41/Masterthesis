CREATE TABLE DATA_SETS (id int AUTO_INCREMENT, filename varchar(2000),  PRIMARY KEY (id));
CREATE TABLE DATA_ENTRY (id int auto_increment, randomValue int, iconsistencyValue int, datasetid int, PRIMARY KEY (id));

