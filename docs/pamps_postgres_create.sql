CREATE TABLE "public.user" (
	"id" serial NOT NULL,
	"email" varchar(255) NOT NULL UNIQUE,
	"username" varchar(255) NOT NULL UNIQUE,
	"avatar" varchar(255),
	"bio" TEXT,
	"password" TEXT NOT NULL,
	CONSTRAINT "user_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.social" (
	"id" serial NOT NULL,
	"from" bigint NOT NULL,
	"to" bigint NOT NULL,
	"date" TIMESTAMP NOT NULL,
	CONSTRAINT "social_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.post" (
	"id" serial NOT NULL,
	"user" bigint NOT NULL,
	"text" varchar(255) NOT NULL,
	"date" TIMESTAMP NOT NULL,
	"parent" bigint,
	CONSTRAINT "post_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.like" (
	"id" serial NOT NULL,
	"user" bigint NOT NULL,
	"post" bigint NOT NULL,
	CONSTRAINT "like_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);




ALTER TABLE "social" ADD CONSTRAINT "social_fk0" FOREIGN KEY ("from") REFERENCES "user"("id");
ALTER TABLE "social" ADD CONSTRAINT "social_fk1" FOREIGN KEY ("to") REFERENCES "user"("id");

ALTER TABLE "post" ADD CONSTRAINT "post_fk0" FOREIGN KEY ("user") REFERENCES "user"("id");
ALTER TABLE "post" ADD CONSTRAINT "post_fk1" FOREIGN KEY ("parent") REFERENCES "post"("id");

ALTER TABLE "like" ADD CONSTRAINT "like_fk0" FOREIGN KEY ("user") REFERENCES "user"("id");
ALTER TABLE "like" ADD CONSTRAINT "like_fk1" FOREIGN KEY ("post") REFERENCES "post"("id");





