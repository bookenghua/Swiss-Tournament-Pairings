-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP DATABASE tournament;

CREATE DATABASE tournament;

\c tournament

CREATE TABLE players ( 
 	p_id serial PRIMARY KEY,
	p_name varchar(255)
 
);


CREATE TABLE tournaments ( 
	t_id serial PRIMARY KEY,
	t_name varchar(255) 
);

CREATE TABLE matches ( 
	m_id serial,
	t_id integer REFERENCES tournaments ON DELETE CASCADE,
	winner_id integer REFERENCES players(p_id) ON DELETE CASCADE,
	loser_id integer REFERENCES players(p_id) ON DELETE CASCADE,
	draw boolean
);

CREATE TABLE scoreboard ( 
	t_id integer REFERENCES tournaments ON DELETE CASCADE,
	p_id integer REFERENCES players ON DELETE CASCADE,
	score integer,
	matches integer,
	bye integer 
);

