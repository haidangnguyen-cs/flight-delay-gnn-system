CREATE KEYSPACE IF NOT EXISTS flight_ks 
WITH REPLICATION = { 
   'class' : 'SimpleStrategy', 
   'replication_factor' : 1 
};

USE flight_ks;

CREATE TABLE IF NOT EXISTS training_data (
    id UUID PRIMARY KEY,
    
    OP_UNIQUE_CARRIER text,
    ORIGIN text,
    DEST text,
    
    DAY_OF_MONTH int,
    DAY_OF_WEEK int,
    CRS_MINUTES int,
    
    DISTANCE float,
    
    temp float,
    rhum float,
    prcp float,
    wspd float,
    coco float,
    
    DEP_DEL15 float,
    
    created_at timestamp
);