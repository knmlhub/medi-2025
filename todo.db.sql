START TRANSACTION;

CREATE TABLE IF NOT EXISTS `diary` (
	`dia_id` INT NOT NULL AUTO_INCREMENT,
	`text` TEXT NOT NULL,
	`date` VARCHAR(20) NOT NULL,
	`user_id` INT NOT NULL,
	`title` TEXT NOT NULL,
	PRIMARY KEY(`dia_id`)
);

CREATE TABLE IF NOT EXISTS `users` (
	`user_id` INT NOT NULL AUTO_INCREMENT,
	`name` TEXT NOT NULL,
	`password_hash` TEXT NOT NULL,
	PRIMARY KEY(`user_id`)
);

INSERT INTO `diary` VALUES (1,'帰って寝る','5-17',1,'すること');
INSERT INTO `diary` VALUES (2,'家に帰る','5-18',2,'すること');
INSERT INTO `diary` VALUES (3,'皿洗う','5-18',3,'すること');
INSERT INTO `diary` VALUES (4,'s','2025-06-02',1,'s');
INSERT INTO `diary` VALUES (5,'aaa','2025-06-18',1,'aa');
INSERT INTO `diary` VALUES (6,'aaa','2025-06-11',5,'aa');
INSERT INTO `diary` VALUES (7,'qqq','2025-06-19',4,'おおかみ');
INSERT INTO `diary` VALUES (8,'ああああ','2025-06-11',6,'てすと');
INSERT INTO `diary` VALUES (9,'aaaa','2025-06-12',7,'aaa');

INSERT INTO `users` VALUES (1,'ねこ','aaa');
INSERT INTO `users` VALUES (2,'いぬ','aaa');
INSERT INTO `users` VALUES (3,'さる','aaa');
INSERT INTO `users` VALUES (4,'おおかみ','pbkdf2_sha256$310000$c1826131e3213f3f7af539361a87c2ee$SU8ofFETdQ4ofmEZPdb5AzkNEj4eJ+rgWAu9PuUbuKk=');
INSERT INTO `users` VALUES (5,'とり','pbkdf2_sha256$310000$20b1a6611ea62a3d777293d658dc0cc2$QDgf1p82Qd4sxT8kS7m7/9ELrD9Y0mYJLoBAv5E1+AU=');
INSERT INTO `users` VALUES (6,'ほし','pbkdf2_sha256$310000$6cb1bbb504e876b7b1670530f8e2148e$DTrJz+9I61lKe5ipI8+OYAa+d7nO+ytxbOPBEuGsySc=');
INSERT INTO `users` VALUES (7,'あああ','pbkdf2_sha256$310000$458d260ca79856449428f5c8127b6d55$3RPgOvsERiQPTA0A2spoSdNz2ciOCk0uQ9Q8SWxpeXg=');

COMMIT;
