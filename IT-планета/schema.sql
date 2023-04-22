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

after VisitedLocation

CREATE OR REPLACE FUNCTION public.set_datetimeofvisitlocationpoint()

RETURNS trigger

LANGUAGE 'plpgsql'

COST 100

VOLATILE NOT LEAKPROOF

AS $BODY$

BEGIN

NEW."dateTimeOfVisitLocationPoint" = to_char(NOW(), 'YYYY-MM-DD"T"HH24:MI:SS"Z"');

RETURN NEW;

END;

$BODY$;

CREATE TRIGGER insert_datetime_of_visitlocationpoint

BEFORE INSERT

ON public."VisitedLocation"

FOR EACH ROW

EXECUTE FUNCTION public.set_datetimeofvisitlocationpoint();

after Animal

CREATE OR REPLACE FUNCTION public.set_chipping_date()

RETURNS trigger

LANGUAGE 'plpgsql'

COST 100

VOLATILE NOT LEAKPROOF

AS $BODY$

BEGIN

IF NEW.chippingDateTime IS NULL THEN

NEW.chippingDateTime = to_char(NOW(), 'YYYY-MM-DD"T"HH24:MI:SS"Z"');

END IF;

RETURN NEW;

END;

$BODY$;

--

CREATE OR REPLACE FUNCTION public.set_chippingdatetime()

RETURNS trigger

LANGUAGE 'plpgsql'

COST 100

VOLATILE NOT LEAKPROOF

AS $BODY$

BEGIN

NEW."chippingDateTime" = to_char(NOW(), 'YYYY-MM-DD"T"HH24:MI:SS"Z"');

RETURN NEW;

END;

$BODY$;

CREATE OR REPLACE FUNCTION public.update_death_date()

RETURNS trigger

LANGUAGE 'plpgsql'

COST 100

VOLATILE NOT LEAKPROOF

AS $BODY$

BEGIN

IF (NEW."lifeStatus" = 'DEAD' AND NEW."deathDateTime" IS NULL)

OR (OLD."lifeStatus" <> 'DEAD' AND NEW."lifeStatus" = 'DEAD' AND NEW."deathDateTime" IS NULL) THEN

NEW."deathDateTime" = to_char(NOW(), 'YYYY-MM-DD"T"HH24:MI:SS"Z"');

END IF;

RETURN NEW;

END;

$BODY$;

--

--

CREATE TRIGGER insert_chippingdatetime

BEFORE INSERT

ON public."Animal"

FOR EACH ROW

EXECUTE FUNCTION public.set_chippingdatetime();

CREATE TRIGGER insert_datetimeofvisitlocationpoint

BEFORE INSERT

ON public."Animal"

FOR EACH ROW

EXECUTE FUNCTION public.set_datetimeofvisitlocationpoint();



CREATE TRIGGER update_death_date_trigger

BEFORE UPDATE

ON public."Animal"

FOR EACH ROW

EXECUTE FUNCTION public.update_death_date();
