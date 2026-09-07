CREATE TABLE IF NOT EXISTS votes_par_candidat (
    candidat VARCHAR(100) PRIMARY KEY,
    nombre_votes INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS votes_par_region (
    region VARCHAR(100) PRIMARY KEY,
    nombre_votes INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS votes_par_parti (
    parti VARCHAR(100) PRIMARY KEY,
    nombre_votes INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS participation_diaspora (
    type_vote VARCHAR(30) PRIMARY KEY,
    nombre_votes INTEGER NOT NULL
);