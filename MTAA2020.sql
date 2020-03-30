CREATE TABLE "book" (
  "id" SERIAL PRIMARY KEY,
  "author_id" int,
  "title" varchar NOT NULL,
  "published" date NOT NULL,
  "rating" float NOT NULL,
  "price" float NOT NULL,
  "genres" varchar[]
);

CREATE TABLE "pdf" (
  "book_id" int UNIQUE,
  "pdfname" varchar,
  "pdf" bytea
);

CREATE TABLE "jpg" (
  "book_id" int UNIQUE,
  "jpgname" varchar,
  "jpg" bytea
);

CREATE TABLE "author" (
  "id" SERIAL PRIMARY KEY,
  "name" varchar UNIQUE NOT NULL,
  "about" varchar
);

CREATE TABLE "user" (
  "id" SERIAL PRIMARY KEY,
  "username" varchar UNIQUE NOT NULL,
  "passwordhash" varchar NOT NULL,
  "email" varchar UNIQUE NOT NULL,
  "balance" float,
  "admin" boolean
);

CREATE TABLE "review" (
  "id" SERIAL PRIMARY KEY,
  "book_id" int,
  "user_id" int,
  "time" timestamp,
  "rating" float,
  "comment" text
);

CREATE TABLE "deposit" (
  "id" SERIAL PRIMARY KEY,
  "user_id" int,
  "amount" float,
  "d_datetime" timestamp
);

CREATE TABLE "purchase" (
  "id" SERIAL PRIMARY KEY,
  "user_id" int,
  "book_id" int,
  "p_datetime" timestamp
);

ALTER TABLE "book" ADD FOREIGN KEY ("author_id") REFERENCES "author" ("id");

ALTER TABLE "pdf" ADD FOREIGN KEY ("book_id") REFERENCES "book" ("id");

ALTER TABLE "jpg" ADD FOREIGN KEY ("book_id") REFERENCES "book" ("id");

ALTER TABLE "review" ADD FOREIGN KEY ("book_id") REFERENCES "book" ("id");

ALTER TABLE "review" ADD FOREIGN KEY ("user_id") REFERENCES "user" ("id");

ALTER TABLE "deposit" ADD FOREIGN KEY ("user_id") REFERENCES "user" ("id");

ALTER TABLE "purchase" ADD FOREIGN KEY ("user_id") REFERENCES "user" ("id");

ALTER TABLE "purchase" ADD FOREIGN KEY ("book_id") REFERENCES "book" ("id");
