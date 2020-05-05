-- MySQL Script generated by MySQL Workbench
-- Mon May  4 21:59:05 2020
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema inquestsca
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `inquestsca` ;

-- -----------------------------------------------------
-- Schema inquestsca
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `inquestsca` DEFAULT CHARACTER SET utf8 ;
SHOW WARNINGS;
USE `inquestsca` ;

-- -----------------------------------------------------
-- Table `inquestsca`.`jurisdictionCategory`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `inquestsca`.`jurisdictionCategory` (
  `jurisdictionCategoryId` CHAR(100) NOT NULL COMMENT 'For a country, its ISO code.',
  `name` VARCHAR(255) NOT NULL COMMENT 'Generally, but not always, a country',
  PRIMARY KEY (`jurisdictionCategoryId`),
  UNIQUE INDEX `jurisdictionID_UNIQUE` (`jurisdictionCategoryId` ASC))
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `inquestsca`.`jurisdiction`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `inquestsca`.`jurisdiction` (
  `jurisdictionId` CHAR(100) NOT NULL COMMENT 'Generally concatenation of sovereignty code and division code (e.g., CAD_ON).',
  `jurisdictionCategoryId` CHAR(100) NOT NULL COMMENT 'Generally, but not always, a country',
  `name` VARCHAR(255) NOT NULL,
  `code` VARCHAR(255) NOT NULL,
  `isFederal` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`jurisdictionId`, `jurisdictionCategoryId`),
  UNIQUE INDEX `jurisdictionID_UNIQUE` (`jurisdictionId` ASC),
  INDEX `fk_jurisdictionCategoryId_jurisdiction1_idx` (`jurisdictionCategoryId` ASC),
  CONSTRAINT `fk_jurisdictionCategoryId_jurisdiction1`
    FOREIGN KEY (`jurisdictionCategoryId`)
    REFERENCES `inquestsca`.`jurisdictionCategory` (`jurisdictionCategoryId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `inquestsca`.`inquest`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `inquestsca`.`inquest` (
  `inquestId` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `jurisdictionId` CHAR(100) NOT NULL,
  `isPrimary` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `name` VARCHAR(255) NOT NULL,
  `overview` VARCHAR(255) NULL,
  `synopsis` VARCHAR(5000) NOT NULL,
  `notes` VARCHAR(1000) NULL,
  `presidingOfficer` VARCHAR(255) NOT NULL,
  `start` DATE NOT NULL,
  `end` DATE NULL,
  `sittingDays` INT NULL,
  `exhibits` INT NULL,
  `remarks` VARCHAR(1000) NULL,
  PRIMARY KEY (`inquestId`),
  UNIQUE INDEX `inquestId_UNIQUE` (`inquestId` ASC),
  INDEX `fk_jurisdictionId_inquest1_idx` (`jurisdictionId` ASC),
  FULLTEXT INDEX `name_FULLTEXT` (`name` ASC),
  CONSTRAINT `fk_jurisdictionId_inquest1`
    FOREIGN KEY (`jurisdictionId`)
    REFERENCES `inquestsca`.`jurisdiction` (`jurisdictionId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `inquestsca`.`inquestCategory`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `inquestsca`.`inquestCategory` (
  `inquestCategoryId` CHAR(100) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `description` VARCHAR(255) NULL,
  PRIMARY KEY (`inquestCategoryId`),
  UNIQUE INDEX `keyword_id_UNIQUE` (`inquestCategoryId` ASC),
  UNIQUE INDEX `name_UNIQUE` (`name` ASC))
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `inquestsca`.`inquestKeyword`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `inquestsca`.`inquestKeyword` (
  `inquestKeywordId` CHAR(100) NOT NULL,
  `inquestCategoryId` CHAR(100) NULL,
  `name` VARCHAR(255) NOT NULL,
  `description` VARCHAR(255) NULL,
  PRIMARY KEY (`inquestKeywordId`),
  UNIQUE INDEX `keyword_id_UNIQUE` (`inquestKeywordId` ASC),
  UNIQUE INDEX `name_UNIQUE` (`name` ASC),
  INDEX `fk_inquestCategoryId_inquestKeyword1_idx` (`inquestCategoryId` ASC),
  CONSTRAINT `fk_inquestCategoryId_inquestKeyword1`
    FOREIGN KEY (`inquestCategoryId`)
    REFERENCES `inquestsca`.`inquestCategory` (`inquestCategoryId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `inquestsca`.`inquestKeywords`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `inquestsca`.`inquestKeywords` (
  `inquestId` INT UNSIGNED NOT NULL,
  `inquestKeywordId` CHAR(100) NOT NULL,
  PRIMARY KEY (`inquestId`, `inquestKeywordId`),
  INDEX `keyword_id_idx` (`inquestKeywordId` ASC),
  CONSTRAINT `fk_inquestId_inquestKeywords1`
    FOREIGN KEY (`inquestId`)
    REFERENCES `inquestsca`.`inquest` (`inquestId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_inquestKeywordId_inquestKeywords1`
    FOREIGN KEY (`inquestKeywordId`)
    REFERENCES `inquestsca`.`inquestKeyword` (`inquestKeywordId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `inquestsca`.`authority`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `inquestsca`.`authority` (
  `authorityId` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `isPrimary` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `name` VARCHAR(255) NOT NULL,
  `overview` VARCHAR(255) NOT NULL,
  `synopsis` VARCHAR(5000) NOT NULL,
  `quotes` VARCHAR(5000) NULL,
  `notes` VARCHAR(1000) NULL,
  `remarks` VARCHAR(1000) NULL COMMENT 'Not exposed through UI.',
  PRIMARY KEY (`authorityId`),
  UNIQUE INDEX `authorityId_UNIQUE` (`authorityId` ASC),
  FULLTEXT INDEX `name_FULLTEXT` (`name` ASC))
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `inquestsca`.`source`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `inquestsca`.`source` (
  `sourceId` CHAR(100) NOT NULL COMMENT 'Generally concatenation of sovereignty code and court code (e.g., CAD_ONCA).',
  `jurisdictionId` CHAR(100) NULL,
  `name` VARCHAR(255) NOT NULL,
  `code` VARCHAR(255) NULL,
  `rank` INT UNSIGNED NOT NULL COMMENT 'Rank which determines the importance of the source, and whether it is binding.',
  PRIMARY KEY (`sourceId`),
  INDEX `fk_jurisdictionID_source1_idx` (`jurisdictionId` ASC),
  CONSTRAINT `fk_jurisdictionId_source1`
    FOREIGN KEY (`jurisdictionId`)
    REFERENCES `inquestsca`.`jurisdiction` (`jurisdictionId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `inquestsca`.`authorityDocumentType`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `inquestsca`.`authorityDocumentType` (
  `authorityDocumentTypeId` CHAR(100) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `description` VARCHAR(255) NULL,
  PRIMARY KEY (`authorityDocumentTypeId`),
  UNIQUE INDEX `documentType_UNIQUE` (`authorityDocumentTypeId` ASC))
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `inquestsca`.`authorityDocument`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `inquestsca`.`authorityDocument` (
  `authorityDocumentId` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `authorityId` INT UNSIGNED NOT NULL,
  `authorityDocumentTypeId` CHAR(100) NULL,
  `sourceId` CHAR(100) NOT NULL,
  `isPrimary` TINYINT NOT NULL DEFAULT 0,
  `name` VARCHAR(255) NOT NULL,
  `citation` VARCHAR(255) NULL,
  `created` DATE NULL,
  INDEX `fk_sourceID_authorityDocuments1_idx` (`sourceId` ASC),
  INDEX `fk_authorityDocumentTypeId_authorityDocuments1_idx` (`authorityDocumentTypeId` ASC),
  PRIMARY KEY (`authorityDocumentId`),
  UNIQUE INDEX `authorityDocumentId_UNIQUE` (`authorityDocumentId` ASC),
  CONSTRAINT `fk_authorityId_authorityDocuments1`
    FOREIGN KEY (`authorityId`)
    REFERENCES `inquestsca`.`authority` (`authorityId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_sourceId_authorityDocuments1`
    FOREIGN KEY (`sourceId`)
    REFERENCES `inquestsca`.`source` (`sourceId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_authorityDocumentTypeId_authorityDocuments1`
    FOREIGN KEY (`authorityDocumentTypeId`)
    REFERENCES `inquestsca`.`authorityDocumentType` (`authorityDocumentTypeId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `inquestsca`.`inquestDocumentType`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `inquestsca`.`inquestDocumentType` (
  `inquestDocumentTypeId` CHAR(100) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `description` VARCHAR(255) NULL,
  PRIMARY KEY (`inquestDocumentTypeId`),
  UNIQUE INDEX `documentType_UNIQUE` (`inquestDocumentTypeId` ASC))
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `inquestsca`.`inquestDocument`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `inquestsca`.`inquestDocument` (
  `inquestDocumentId` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `inquestId` INT UNSIGNED NOT NULL,
  `inquestDocumentTypeId` CHAR(100) NULL COMMENT 'E.g., verdict, ruling, exhibit.\nCan be NULL if document falls into misc. category.',
  `name` VARCHAR(255) NOT NULL,
  `created` DATE NOT NULL,
  PRIMARY KEY (`inquestDocumentId`),
  INDEX `fk_inquestDocumentTypeId_inquestDocuments1_idx` (`inquestDocumentTypeId` ASC),
  UNIQUE INDEX `inquestDocumentId_UNIQUE` (`inquestDocumentId` ASC),
  CONSTRAINT `fk_inquestId_inquestDocuments1`
    FOREIGN KEY (`inquestId`)
    REFERENCES `inquestsca`.`inquest` (`inquestId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_inquestDocumentTypeId_inquestDocuments1`
    FOREIGN KEY (`inquestDocumentTypeId`)
    REFERENCES `inquestsca`.`inquestDocumentType` (`inquestDocumentTypeId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `inquestsca`.`authorityCategory`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `inquestsca`.`authorityCategory` (
  `authorityCategoryId` CHAR(100) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `description` VARCHAR(255) NULL,
  PRIMARY KEY (`authorityCategoryId`),
  UNIQUE INDEX `keyword_id_UNIQUE` (`authorityCategoryId` ASC),
  UNIQUE INDEX `name_UNIQUE` (`name` ASC))
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `inquestsca`.`authorityKeyword`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `inquestsca`.`authorityKeyword` (
  `authorityKeywordId` CHAR(100) NOT NULL,
  `authorityCategoryId` CHAR(100) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `description` VARCHAR(255) NULL,
  PRIMARY KEY (`authorityKeywordId`),
  UNIQUE INDEX `keyword_id_UNIQUE` (`authorityKeywordId` ASC),
  UNIQUE INDEX `name_UNIQUE` (`name` ASC),
  INDEX `fk_authorityCategoryId_authorityKeyword1_idx` (`authorityCategoryId` ASC),
  CONSTRAINT `fk_authorityCategoryId_authorityKeyword1`
    FOREIGN KEY (`authorityCategoryId`)
    REFERENCES `inquestsca`.`authorityCategory` (`authorityCategoryId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `inquestsca`.`authorityKeywords`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `inquestsca`.`authorityKeywords` (
  `authorityId` INT UNSIGNED NOT NULL,
  `authorityKeywordId` CHAR(100) NOT NULL,
  PRIMARY KEY (`authorityId`, `authorityKeywordId`),
  INDEX `fk_keywordId_authorityKeywords1_idx` (`authorityKeywordId` ASC),
  CONSTRAINT `fk_authorityId_authorityKeywords1`
    FOREIGN KEY (`authorityId`)
    REFERENCES `inquestsca`.`authority` (`authorityId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_keywordId_authorityKeywords1`
    FOREIGN KEY (`authorityKeywordId`)
    REFERENCES `inquestsca`.`authorityKeyword` (`authorityKeywordId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `inquestsca`.`deathManner`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `inquestsca`.`deathManner` (
  `deathMannerId` CHAR(100) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`deathMannerId`),
  UNIQUE INDEX `deathMannerId_UNIQUE` (`deathMannerId` ASC))
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `inquestsca`.`inquestType`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `inquestsca`.`inquestType` (
  `inquestTypeId` CHAR(100) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `isMandatory` TINYINT UNSIGNED NOT NULL,
  PRIMARY KEY (`inquestTypeId`),
  UNIQUE INDEX `deathMannerId_UNIQUE` (`inquestTypeId` ASC))
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `inquestsca`.`deceased`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `inquestsca`.`deceased` (
  `deceasedId` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `inquestId` INT UNSIGNED NOT NULL,
  `inquestTypeId` CHAR(100) NOT NULL,
  `deathMannerId` CHAR(100) NOT NULL,
  `deathCause` VARCHAR(255) NOT NULL,
  `deathDate` DATE NOT NULL,
  `lastName` VARCHAR(255) NULL COMMENT 'NULL if youth.',
  `givenNames` VARCHAR(255) NULL COMMENT 'NULL if youth.',
  `age` INT NULL,
  `sex` VARCHAR(255) NULL,
  PRIMARY KEY (`deceasedId`),
  UNIQUE INDEX `deceasedId_UNIQUE` (`deceasedId` ASC),
  INDEX `fk_inquestId_deceased_idx` (`inquestId` ASC),
  INDEX `fk_deathMannerId_deceased1_idx` (`deathMannerId` ASC),
  INDEX `fk_inquestTypeId_deceased1_idx` (`inquestTypeId` ASC),
  FULLTEXT INDEX `lastName_FULLTEXT` (`lastName` ASC, `givenNames` ASC),
  CONSTRAINT `fk_inquestId_deceased1`
    FOREIGN KEY (`inquestId`)
    REFERENCES `inquestsca`.`inquest` (`inquestId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_deathMannerId_deceased1`
    FOREIGN KEY (`deathMannerId`)
    REFERENCES `inquestsca`.`deathManner` (`deathMannerId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_inquestTypeId_deceased1`
    FOREIGN KEY (`inquestTypeId`)
    REFERENCES `inquestsca`.`inquestType` (`inquestTypeId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `inquestsca`.`authorityInquests`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `inquestsca`.`authorityInquests` (
  `authorityId` INT UNSIGNED NOT NULL,
  `inquestId` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`authorityId`, `inquestId`),
  INDEX `fk_inquestId_authorityInquest1_idx` (`inquestId` ASC),
  CONSTRAINT `fk_authorityId_authorityInquests1`
    FOREIGN KEY (`authorityId`)
    REFERENCES `inquestsca`.`authority` (`authorityId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_inquestId_authorityInquest1`
    FOREIGN KEY (`inquestId`)
    REFERENCES `inquestsca`.`inquest` (`inquestId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `inquestsca`.`authorityCitations`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `inquestsca`.`authorityCitations` (
  `authorityId` INT UNSIGNED NOT NULL,
  `citedAuthorityId` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`authorityId`, `citedAuthorityId`),
  INDEX `fk_authorityId_authorityCitations2_idx` (`citedAuthorityId` ASC),
  CONSTRAINT `fk_authorityId_authorityCitations1`
    FOREIGN KEY (`authorityId`)
    REFERENCES `inquestsca`.`authority` (`authorityId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_authorityId_authorityCitations2`
    FOREIGN KEY (`citedAuthorityId`)
    REFERENCES `inquestsca`.`authority` (`authorityId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `inquestsca`.`authorityRelated`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `inquestsca`.`authorityRelated` (
  `authorityId` INT UNSIGNED NOT NULL,
  `relatedAuthorityId` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`authorityId`, `relatedAuthorityId`),
  INDEX `fk_authorityId_authorityRelated2_idx` (`relatedAuthorityId` ASC),
  CONSTRAINT `fk_authorityId_authorityRelated1`
    FOREIGN KEY (`authorityId`)
    REFERENCES `inquestsca`.`authority` (`authorityId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_authorityId_authorityRelated2`
    FOREIGN KEY (`relatedAuthorityId`)
    REFERENCES `inquestsca`.`authority` (`authorityId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `inquestsca`.`authoritySuperceded`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `inquestsca`.`authoritySuperceded` (
  `authorityId` INT UNSIGNED NOT NULL,
  `supercededAuthorityId` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`authorityId`, `supercededAuthorityId`),
  INDEX `fk_authorityId_authorityCitations2_idx` (`supercededAuthorityId` ASC),
  CONSTRAINT `fk_authorityId_authoritySuperceded1`
    FOREIGN KEY (`authorityId`)
    REFERENCES `inquestsca`.`authority` (`authorityId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_authorityId_authoritySuperceded2`
    FOREIGN KEY (`supercededAuthorityId`)
    REFERENCES `inquestsca`.`authority` (`authorityId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `inquestsca`.`documentSource`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `inquestsca`.`documentSource` (
  `documentSourceId` CHAR(100) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `isFree` TINYINT UNSIGNED NOT NULL DEFAULT 1,
  PRIMARY KEY (`documentSourceId`))
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `inquestsca`.`authorityDocumentLinks`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `inquestsca`.`authorityDocumentLinks` (
  `authorityDocumentId` INT UNSIGNED NOT NULL,
  `documentSourceId` CHAR(100) NOT NULL,
  `link` VARCHAR(1000) NOT NULL,
  PRIMARY KEY (`authorityDocumentId`, `documentSourceId`),
  INDEX `fk_documentSourceId_documentLinks1_idx` (`documentSourceId` ASC),
  CONSTRAINT `fk_documentSourceId_authorityDocumentLinks1`
    FOREIGN KEY (`documentSourceId`)
    REFERENCES `inquestsca`.`documentSource` (`documentSourceId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_authorityDocumentId_authorityDocumentLinks1`
    FOREIGN KEY (`authorityDocumentId`)
    REFERENCES `inquestsca`.`authorityDocument` (`authorityDocumentId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `inquestsca`.`inquestDocumentLinks`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `inquestsca`.`inquestDocumentLinks` (
  `inquestDocumentId` INT UNSIGNED NOT NULL,
  `documentSourceId` CHAR(100) NOT NULL,
  `link` VARCHAR(1000) NOT NULL,
  PRIMARY KEY (`inquestDocumentId`, `documentSourceId`),
  INDEX `fk_documentSourceId_documentLinks1_idx` (`documentSourceId` ASC),
  CONSTRAINT `fk_documentSourceId_inquestDocumentLinks1`
    FOREIGN KEY (`documentSourceId`)
    REFERENCES `inquestsca`.`documentSource` (`documentSourceId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_inquestDocumentId_inquestDocumentLinks1`
    FOREIGN KEY (`inquestDocumentId`)
    REFERENCES `inquestsca`.`inquestDocument` (`inquestDocumentId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

SHOW WARNINGS;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

-- -----------------------------------------------------
-- Data for table `inquestsca`.`jurisdictionCategory`
-- -----------------------------------------------------
START TRANSACTION;
USE `inquestsca`;
INSERT INTO `inquestsca`.`jurisdictionCategory` (`jurisdictionCategoryId`, `name`) VALUES ('CAD', 'Canada');
INSERT INTO `inquestsca`.`jurisdictionCategory` (`jurisdictionCategoryId`, `name`) VALUES ('US', 'United States');
INSERT INTO `inquestsca`.`jurisdictionCategory` (`jurisdictionCategoryId`, `name`) VALUES ('UK', 'United Kingdom and Common Wealth');

COMMIT;


-- -----------------------------------------------------
-- Data for table `inquestsca`.`jurisdiction`
-- -----------------------------------------------------
START TRANSACTION;
USE `inquestsca`;
INSERT INTO `inquestsca`.`jurisdiction` (`jurisdictionId`, `jurisdictionCategoryId`, `name`, `code`, `isFederal`) VALUES ('CAD', 'CAD', 'Canada', 'CAD', 1);
INSERT INTO `inquestsca`.`jurisdiction` (`jurisdictionId`, `jurisdictionCategoryId`, `name`, `code`, `isFederal`) VALUES ('CAD_AB', 'CAD', 'Alberta', 'AB', 0);
INSERT INTO `inquestsca`.`jurisdiction` (`jurisdictionId`, `jurisdictionCategoryId`, `name`, `code`, `isFederal`) VALUES ('CAD_BC', 'CAD', 'British Columbia', 'BC', 0);
INSERT INTO `inquestsca`.`jurisdiction` (`jurisdictionId`, `jurisdictionCategoryId`, `name`, `code`, `isFederal`) VALUES ('CAD_MB', 'CAD', 'Manitoba', 'MB', 0);
INSERT INTO `inquestsca`.`jurisdiction` (`jurisdictionId`, `jurisdictionCategoryId`, `name`, `code`, `isFederal`) VALUES ('CAD_NB', 'CAD', 'New Brunswick', 'NB', 0);
INSERT INTO `inquestsca`.`jurisdiction` (`jurisdictionId`, `jurisdictionCategoryId`, `name`, `code`, `isFederal`) VALUES ('CAD_NL', 'CAD', 'Newfoundland & Labrador', 'NL', 0);
INSERT INTO `inquestsca`.`jurisdiction` (`jurisdictionId`, `jurisdictionCategoryId`, `name`, `code`, `isFederal`) VALUES ('CAD_NS', 'CAD', 'Nova Scotia', 'NS', 0);
INSERT INTO `inquestsca`.`jurisdiction` (`jurisdictionId`, `jurisdictionCategoryId`, `name`, `code`, `isFederal`) VALUES ('CAD_NT', 'CAD', 'Northwest Territories', 'NT', 0);
INSERT INTO `inquestsca`.`jurisdiction` (`jurisdictionId`, `jurisdictionCategoryId`, `name`, `code`, `isFederal`) VALUES ('CAD_NU', 'CAD', 'Nunavut', 'NU', 0);
INSERT INTO `inquestsca`.`jurisdiction` (`jurisdictionId`, `jurisdictionCategoryId`, `name`, `code`, `isFederal`) VALUES ('CAD_ON', 'CAD', 'Ontario', 'ON', 0);
INSERT INTO `inquestsca`.`jurisdiction` (`jurisdictionId`, `jurisdictionCategoryId`, `name`, `code`, `isFederal`) VALUES ('CAD_PE', 'CAD', 'Prince Edward Island', 'PE', 0);
INSERT INTO `inquestsca`.`jurisdiction` (`jurisdictionId`, `jurisdictionCategoryId`, `name`, `code`, `isFederal`) VALUES ('CAD_QC', 'CAD', 'Québec', 'QC', 0);
INSERT INTO `inquestsca`.`jurisdiction` (`jurisdictionId`, `jurisdictionCategoryId`, `name`, `code`, `isFederal`) VALUES ('CAD_SK', 'CAD', 'Saskatchewan', 'SK', 0);
INSERT INTO `inquestsca`.`jurisdiction` (`jurisdictionId`, `jurisdictionCategoryId`, `name`, `code`, `isFederal`) VALUES ('CAD_YK', 'CAD', 'Yukon', 'YK', 0);
INSERT INTO `inquestsca`.`jurisdiction` (`jurisdictionId`, `jurisdictionCategoryId`, `name`, `code`, `isFederal`) VALUES ('UK', 'UK', 'United Kingdom', 'UK', 1);
INSERT INTO `inquestsca`.`jurisdiction` (`jurisdictionId`, `jurisdictionCategoryId`, `name`, `code`, `isFederal`) VALUES ('US', 'US', 'United States', 'US', 1);

COMMIT;


-- -----------------------------------------------------
-- Data for table `inquestsca`.`source`
-- -----------------------------------------------------
START TRANSACTION;
USE `inquestsca`;
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('CAD_ABCA', 'CAD_AB', 'Alberta Court of Appeal', 'ABCA', 70);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('CAD_ABCQB', 'CAD_AB', 'Alberta Court of Queen\'s Bench', 'ABCQB', 0);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('CAD_ABINQ', 'CAD_AB', 'Alberta Fatality Inquiry', 'ABINQ', 50);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('CAD_ABLEG', 'CAD_AB', 'Alberta Legislature', 'ABLEG', 30);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('CAD_BCCA', 'CAD_BC', 'British Columbia Court of Appeal', 'BCCA', 70);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('CAD_BCINQ', 'CAD_BC', 'British Columbia Inquest', 'BCINQ', 50);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('CAD_BCLEG', 'CAD_BC', 'British Columbia Legislature', 'BCLEG', 30);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('CAD_BCSC', 'CAD_BC', 'British Columbia Supreme Court', 'BCSC', 60);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('CAD_FCC', 'CAD', 'Federal Court of Canada', 'FCC', 80);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('CAD_LEG', 'CAD', 'Parliament of Canada', NULL, 30);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('CAD_MBCA', 'CAD_MB', 'Manitoba Court of Appeal', 'MBCA', 70);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('CAD_MBCQB', 'CAD_MB', 'Manitoba Court of Queen\'s Bench', 'MBCQB', 60);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('CAD_NSCA', 'CAD_NS', 'Nova Scotia Court of Appeal', 'NSCA', 70);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('CAD_NUINQ', 'CAD_NU', 'Nunavut Inquest', 'NUINQ', 50);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('CAD_ONCA', 'CAD_ON', 'Ontario Court of Appeal', 'ONCA', 70);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('CAD_ONINQ', 'CAD_ON', 'Ontario Inquest', 'ONINQ', 50);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('CAD_ONJI', 'CAD_ON', 'Ontario Judicial Inquiry', 'ONJI', 20);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('CAD_ONLEG', 'CAD_ON', 'Ontario Legislature', 'ONLEG', 30);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('CAD_ONOCC', 'CAD_ON', 'Ontario Office of the Chief Coroner', 'ONOCC', 50);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('CAD_ONOLRC', 'CAD_ON', 'Ontario Law Reform Commission', 'ONOLRC', 20);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('CAD_ONPI', 'CAD_ON', 'Ontario Public Inquiry', 'ONPI', 60);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('CAD_ONSCJ', 'CAD_ON', 'Ontario Superior Court of Justice (incl DIvisional)', 'ONSCJ', 60);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('CAD_SCC', 'CAD', 'Supreme Court of Canada', 'SCC', 90);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('CAD_SKLEG', 'CAD_SK', 'Saskatchewan Legislature', 'SKLEG', 30);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('CAD_SKQB', 'CAD_SK', 'Saskatchewan Court of Queen\'s Bench', 'SKQB', 60);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('CAD_YKCA', 'CAD_YK', 'Yukon Court of Appeal', 'YKCA', 70);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('REF', NULL, 'Other Reference', NULL, 0);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('UK_SC', 'UK', 'UK Supreme Court (formerly House of Lords)', NULL, 0);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('UK_SENC', 'UK', 'UK Senior Court', NULL, 10);
INSERT INTO `inquestsca`.`source` (`sourceId`, `jurisdictionId`, `name`, `code`, `rank`) VALUES ('US_SC', 'US', 'United States Supreme Court', NULL, 10);

COMMIT;


-- -----------------------------------------------------
-- Data for table `inquestsca`.`authorityDocumentType`
-- -----------------------------------------------------
START TRANSACTION;
USE `inquestsca`;
INSERT INTO `inquestsca`.`authorityDocumentType` (`authorityDocumentTypeId`, `name`, `description`) VALUES ('RULING', 'Ruling', NULL);
INSERT INTO `inquestsca`.`authorityDocumentType` (`authorityDocumentTypeId`, `name`, `description`) VALUES ('STATUTE', 'Statute or Regulation', NULL);
INSERT INTO `inquestsca`.`authorityDocumentType` (`authorityDocumentTypeId`, `name`, `description`) VALUES ('REFERENCE', 'Reference', 'Other references such as research.');

COMMIT;


-- -----------------------------------------------------
-- Data for table `inquestsca`.`inquestDocumentType`
-- -----------------------------------------------------
START TRANSACTION;
USE `inquestsca`;
INSERT INTO `inquestsca`.`inquestDocumentType` (`inquestDocumentTypeId`, `name`, `description`) VALUES ('VERDICT', 'Verdict/Verdict Explanation', NULL);
INSERT INTO `inquestsca`.`inquestDocumentType` (`inquestDocumentTypeId`, `name`, `description`) VALUES ('RULING', 'Ruling', NULL);
INSERT INTO `inquestsca`.`inquestDocumentType` (`inquestDocumentTypeId`, `name`, `description`) VALUES ('EXHIBIT', 'Exhibit', NULL);
INSERT INTO `inquestsca`.`inquestDocumentType` (`inquestDocumentTypeId`, `name`, `description`) VALUES ('RESPONSES', 'Responses to Recommendations', NULL);
INSERT INTO `inquestsca`.`inquestDocumentType` (`inquestDocumentTypeId`, `name`, `description`) VALUES ('OTHER', 'Other', NULL);

COMMIT;


-- -----------------------------------------------------
-- Data for table `inquestsca`.`deathManner`
-- -----------------------------------------------------
START TRANSACTION;
USE `inquestsca`;
INSERT INTO `inquestsca`.`deathManner` (`deathMannerId`, `name`) VALUES ('ACCIDENT', 'Accident');
INSERT INTO `inquestsca`.`deathManner` (`deathMannerId`, `name`) VALUES ('HOMICIDE', 'Homicide');
INSERT INTO `inquestsca`.`deathManner` (`deathMannerId`, `name`) VALUES ('NATURAL', 'Natural');
INSERT INTO `inquestsca`.`deathManner` (`deathMannerId`, `name`) VALUES ('SUICIDE', 'Suicide');
INSERT INTO `inquestsca`.`deathManner` (`deathMannerId`, `name`) VALUES ('UNDETERMINED', 'Undetermined');
INSERT INTO `inquestsca`.`deathManner` (`deathMannerId`, `name`) VALUES ('OTHER', 'Other');

COMMIT;


-- -----------------------------------------------------
-- Data for table `inquestsca`.`inquestType`
-- -----------------------------------------------------
START TRANSACTION;
USE `inquestsca`;
INSERT INTO `inquestsca`.`inquestType` (`inquestTypeId`, `name`, `isMandatory`) VALUES ('CONSTRUCTION', 'Construction', 1);
INSERT INTO `inquestsca`.`inquestType` (`inquestTypeId`, `name`, `isMandatory`) VALUES ('CUSTODY_INMATE', 'Custody (Inmate)', 1);
INSERT INTO `inquestsca`.`inquestType` (`inquestTypeId`, `name`, `isMandatory`) VALUES ('CUSTODY_POLICE', 'Custody (Police)', 1);
INSERT INTO `inquestsca`.`inquestType` (`inquestTypeId`, `name`, `isMandatory`) VALUES ('DISCRETIONARY', 'Discretionary', 0);
INSERT INTO `inquestsca`.`inquestType` (`inquestTypeId`, `name`, `isMandatory`) VALUES ('MINING', 'Mining', 1);
INSERT INTO `inquestsca`.`inquestType` (`inquestTypeId`, `name`, `isMandatory`) VALUES ('OTHER', 'Other', 0);

COMMIT;

