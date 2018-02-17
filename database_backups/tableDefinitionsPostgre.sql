CREATE TABLE "new_gammas" (
  "id" int NOT NULL,
  "old_gamma" int DEFAULT NULL,
  "new_gamma" int DEFAULT NULL,
  "time" timestamp DEFAULT NULL,
  "transcriber" varchar(30) DEFAULT NULL,
  PRIMARY KEY ("id")
);
CREATE TABLE "transcribers" (
  "name" varchar(30) NOT NULL,
  "discord_id" varchar(40) DEFAULT NULL,
  "official_gamma_count" int DEFAULT NULL,
  "reference_comment" varchar(40) DEFAULT NULL,
  "last_checked_comment" varchar(40) DEFAULT NULL,
  "valid" boolean DEFAULT NULL,
  "counted_comments" int DEFAULT 0,
  PRIMARY KEY ("name")
);
CREATE TABLE "transcriptions" (
  "comment_id" varchar(40) NOT NULL,
  "transcriber" varchar(30) DEFAULT NULL,
  "content" text DEFAULT NULL,
  "subreddit" varchar(20) DEFAULT NULL,
  "found" timestamp DEFAULT NULL,
  "comment_count" int DEFAULT NULL,
  "upvotes" int DEFAULT NULL,
  "last_checked" timestamp DEFAULT NULL,
  "good_bot" int DEFAULT NULL,
  "bad_bot" int DEFAULT NULL,
  "good_human" int DEFAULT NULL,
  "bad_human" int DEFAULT NULL,
  "error" boolean DEFAULT NULL,
  "from_archive" boolean DEFAULT false,
  PRIMARY KEY ("comment_id")
);
