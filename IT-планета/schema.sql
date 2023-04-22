CREATE ROLE postgres LOGIN PASSWORD '123';

CREATE TABLE IF NOT EXISTS public."Account"(
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    "firstName" character varying(255) COLLATE pg_catalog."default" NOT NULL,
    "lastName" character varying(255) COLLATE pg_catalog."default" NOT NULL,
    email character varying(255) COLLATE pg_catalog."default" NOT NULL,
    password character varying(255) COLLATE pg_catalog."default" NOT NULL,
    role character varying(255) COLLATE pg_catalog."default" NOT NULL
);

INSERT INTO "Account" ("firstName", "lastName", email, password, role) VALUES ('adminFirstName', 'adminLastName', 'admin@simbirsoft.com', 'qwerty123', 'ADMIN');
INSERT INTO "Account" ("firstName", "lastName", email, password, role) VALUES('chipperFirstName', 'chipperLastName', 'chipper@simbirsoft.com', 'qwerty123', 'CHIPPER');
INSERT INTO "Account" ("firstName", "lastName", email, password, role) VALUES('userFirstName', 'userLastName', 'user@simbirsoft.com', 'qwerty123', 'USER');

CREATE TABLE IF NOT EXISTS public."Location"(
    id SERIAL PRIMARY KEY,
    latitude double precision NOT NULL,
    longitude double precision NOT NULL
);


CREATE TABLE IF NOT EXISTS public."Area"(
    id SERIAL PRIMARY KEY,
    name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    "areaPoints" text COLLATE pg_catalog."default" NOT NULL
);


CREATE TABLE IF NOT EXISTS public."Location"(
    id integer PRIMARY KEY,
    latitude double precision NOT NULL,
    longitude double precision NOT NULL
);

CREATE TABLE IF NOT EXISTS public."AnimalType"(
    id SERIAL PRIMARY KEY,
    type character varying(255) COLLATE pg_catalog."default" NOT NULL
);

CREATE TABLE IF NOT EXISTS public."Animal"
(
    id SERIAL PRIMARY KEY,
    "animalTypes" text COLLATE pg_catalog."default" NOT NULL,
    weight real NOT NULL,
    length real NOT NULL,
    height real NOT NULL,
    gender character varying(255) COLLATE pg_catalog."default" NOT NULL,
    "lifeStatus" character varying(255) COLLATE pg_catalog."default" NOT NULL,
    "chippingDateTime" text COLLATE pg_catalog."default" NOT NULL,
    "chipperId_id" integer NOT NULL,
    "chippingLocationId_id" integer NOT NULL,
    "visitedLocations" text COLLATE pg_catalog."default",
    "deathDateTime" text COLLATE pg_catalog."default",
    CONSTRAINT "Animal_chipperId_id_fkey" FOREIGN KEY ("chipperId_id")
        REFERENCES public."Account" (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT "Animal_chippingLocationId_id_fkey" FOREIGN KEY ("chippingLocationId_id")
        REFERENCES public."Location" (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);


CREATE TABLE IF NOT EXISTS public."VisitedLocation"(
    id SERIAL NOT NULL,
    "dateTimeOfVisitLocationPoint" text COLLATE pg_catalog."default" NOT NULL,
    "locationPointId" integer NOT NULL
);