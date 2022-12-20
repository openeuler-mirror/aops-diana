CREATE TABLE IF NOT EXISTS `alert_host` (
    `alert_id`  CHAR(32) NOT NULL, 
    `host_id`   CHAR(32) NOT NULL, 
    `host_ip`   CHAR(32) NULL, 
    `host_name` CHAR(50) NULL, 
    PRIMARY KEY (`host_id`,`alert_id`), 
    KEY `FK__alert_id_auto_index` (`alert_id`), 
    KEY `FK_alert_with_host_host_id_auto_index` (`host_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci ROW_FORMAT=DYNAMIC ;

CREATE TABLE IF NOT EXISTS `algorithm` (
    `algo_id`     INT(11)   NOT NULL, 
    `path`        CHAR(150) NULL, 
    `username`    CHAR(10)  NULL, 
    `algo_name`   CHAR(20)  NOT NULL, 
    `field`       CHAR(20)  NOT NULL, 
    `description` LONGTEXT  NULL, 
    PRIMARY KEY (`algo_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci ROW_FORMAT=DYNAMIC ;

CREATE TABLE IF NOT EXISTS `domain_check_result` (
    `alert_id`      CHAR(32)   NOT NULL, 
    `domain`        CHAR(20)   NOT NULL, 
    `alert_name`    CHAR(50)   NULL, 
    `time`          INT(11)    NULL, 
    `workflow_name` CHAR(50)   NULL, 
    `workflow_id`   CHAR(32)   NULL, 
    `username`      CHAR(20)   NULL, 
    `level`         CHAR(20)   NULL, 
    `confirmed`     TINYINT(1) NULL, 
    PRIMARY KEY (`alert_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci ROW_FORMAT=DYNAMIC ;

CREATE TABLE IF NOT EXISTS `host_check_result` (
    `id`           INT(11)    NOT NULL, 
    `time`         INT(11)    NOT NULL, 
    `is_root`      TINYINT(1) NULL, 
    `host_id`      CHAR(32)   NOT NULL, 
    `metric_name`  CHAR(50)   NULL, 
    `alert_id`     CHAR(32)   NOT NULL, 
    `metric_label` CHAR(255)  NULL, 
    PRIMARY KEY (`id`), 
    KEY `host_id_auto_index` (`host_id`), 
    KEY `alert_id_auto_index` (`alert_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci ROW_FORMAT=DYNAMIC ;

CREATE TABLE IF NOT EXISTS `model` (
    `model_id`    INT(11)   NOT NULL, 
    `username`    CHAR(40)  NULL, 
    `model_name`  CHAR(10)  NULL, 
    `tag`         CHAR(255) NULL, 
    `algo_id`     INT(11)   NULL, 
    `create_time` INT(11)   NULL, 
    `file_path`   CHAR(64)  NULL, 
    `precision`   DOUBLE    NULL, 
    PRIMARY KEY (`model_id`), 
    KEY `algo_id_auto_index` (`algo_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci ROW_FORMAT=DYNAMIC ;

CREATE TABLE IF NOT EXISTS `workflow` (
    `workflow_id`   CHAR(20) NOT NULL, 
    `workflow_name` CHAR(10) NOT NULL, 
    `status`        CHAR(12) NOT NULL, 
    `description`   CHAR(50) NULL, 
    `app_name`      CHAR(10) NOT NULL, 
    `app_id`        CHAR(10) NOT NULL, 
    `step`          INT(11)  NOT NULL, 
    `period`        INT(11)  NOT NULL, 
    `domain`        CHAR(20) NOT NULL, 
    `username`      CHAR(40) NOT NULL, 
    PRIMARY KEY (`workflow_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci ROW_FORMAT=DYNAMIC ;

CREATE TABLE IF NOT EXISTS `workflow_host` (
    `host_id`     CHAR(32) NOT NULL, 
    `workflow_id` CHAR(10) NULL, 
    `host_name`   CHAR(20) NULL, 
    `host_ip`     CHAR(16) NULL, 
    PRIMARY KEY (`host_id`), 
    KEY `workflow_id_auto_index` (`workflow_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci ROW_FORMAT=DYNAMIC ;

ALTER TABLE alert_host
ADD CONSTRAINT `FK_alert_with_host_alert_id` FOREIGN KEY (`alert_id`) REFERENCES `domain_check_result` (`alert_id`) ON DELETE RESTRICT ON UPDATE RESTRICT ;

ALTER TABLE host_check_result
ADD CONSTRAINT `host_id` FOREIGN KEY (`host_id`) REFERENCES `alert_host` (`host_id`) ON DELETE RESTRICT ON UPDATE RESTRICT , 
ADD CONSTRAINT `alert_id` FOREIGN KEY (`alert_id`) REFERENCES `domain_check_result` (`alert_id`) ON DELETE RESTRICT ON UPDATE RESTRICT ;

ALTER TABLE model
ADD CONSTRAINT `algo_id` FOREIGN KEY (`algo_id`) REFERENCES `algorithm` (`algo_id`) ON DELETE RESTRICT ON UPDATE RESTRICT ;

ALTER TABLE workflow_host
ADD CONSTRAINT `workflow_id` FOREIGN KEY (`workflow_id`) REFERENCES `workflow` (`workflow_id`) ON DELETE RESTRICT ON UPDATE RESTRICT ;