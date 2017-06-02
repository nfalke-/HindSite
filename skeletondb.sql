/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `run_step`
--

DROP TABLE IF EXISTS `run_step`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `run_step` (
  `run_step_id` int(11) NOT NULL AUTO_INCREMENT,
  `runid` int(11) NOT NULL,
  `action` varchar(400) NOT NULL DEFAULT '',
  `args` varchar(400) NOT NULL DEFAULT '',
  `passed` tinyint(1) DEFAULT NULL,
  `take_screenshot` tinyint(1) NOT NULL DEFAULT '0',
  `screenshot_percentage` decimal(6,5) DEFAULT NULL,
  `screenshot_passed` tinyint(1) NOT NULL DEFAULT '0',
  `screenshot_name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`run_step_id`),
  KEY `runid` (`runid`),
  CONSTRAINT `run_step_ibfk_1` FOREIGN KEY (`runid`) REFERENCES `runs` (`runid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1902 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `runs`
--

DROP TABLE IF EXISTS `runs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `runs` (
  `runid` int(11) NOT NULL AUTO_INCREMENT,
  `testid` int(11) NOT NULL,
  `start` datetime NOT NULL,
  `end` datetime DEFAULT NULL,
  `passed` tinyint(1) DEFAULT NULL,
  `screenshot_passed` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`runid`),
  KEY `testid` (`testid`),
  CONSTRAINT `runs_ibfk_1` FOREIGN KEY (`testid`) REFERENCES `tests` (`testid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=549 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `scheduled`
--

DROP TABLE IF EXISTS `scheduled`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `scheduled` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `suiteid` int(11) NOT NULL,
  `testid` int(11) DEFAULT NULL,
  `period` int(32) NOT NULL,
  `nextrun` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `suiteid` (`suiteid`),
  KEY `testid` (`testid`),
  CONSTRAINT `scheduled_ibfk_1` FOREIGN KEY (`suiteid`) REFERENCES `suites` (`suiteid`) ON DELETE CASCADE,
  CONSTRAINT `scheduled_ibfk_2` FOREIGN KEY (`testid`) REFERENCES `tests` (`testid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `scheduledSuite`
--

DROP TABLE IF EXISTS `scheduledSuite`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `scheduledSuite` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `suiteid` int(11) NOT NULL,
  `period` int(32) NOT NULL,
  `active` tinyint(1) NOT NULL DEFAULT '0',
  `nextrun` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `suiteid` (`suiteid`),
  CONSTRAINT `scheduledSuite_ibfk_1` FOREIGN KEY (`suiteid`) REFERENCES `suites` (`suiteid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `scheduledTest`
--

DROP TABLE IF EXISTS `scheduledTest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `scheduledTest` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `suiteid` int(11) NOT NULL,
  `testid` int(11) NOT NULL,
  `period` int(32) NOT NULL,
  `active` tinyint(1) NOT NULL DEFAULT '0',
  `nextrun` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `suiteid` (`suiteid`),
  KEY `testid` (`testid`),
  CONSTRAINT `scheduledTest_ibfk_1` FOREIGN KEY (`suiteid`) REFERENCES `suites` (`suiteid`) ON DELETE CASCADE,
  CONSTRAINT `scheduledTest_ibfk_2` FOREIGN KEY (`testid`) REFERENCES `tests` (`testid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `steps`
--

DROP TABLE IF EXISTS `steps`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `steps` (
  `stepid` int(11) NOT NULL AUTO_INCREMENT,
  `testid` int(11) NOT NULL,
  `stepnumber` int(11) NOT NULL,
  `action` varchar(10) DEFAULT NULL,
  `optional` tinyint(1) NOT NULL DEFAULT '0',
  `args` varchar(400) DEFAULT NULL,
  `screenshot` tinyint(1) NOT NULL DEFAULT '0',
  `screenshot_name` varchar(60) NOT NULL DEFAULT '',
  `threshold` decimal(6,5) NOT NULL DEFAULT '0.10000',
  PRIMARY KEY (`stepid`),
  KEY `testid` (`testid`),
  CONSTRAINT `steps_ibfk_1` FOREIGN KEY (`testid`) REFERENCES `tests` (`testid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=139 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `suite_config`
--

DROP TABLE IF EXISTS `suite_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `suite_config` (
  `configid` int(11) NOT NULL AUTO_INCREMENT,
  `suiteid` int(11) NOT NULL,
  `browser` varchar(32) NOT NULL DEFAULT 'chrome',
  `width` int(8) NOT NULL DEFAULT '1920',
  `height` int(8) NOT NULL DEFAULT '1080',
  PRIMARY KEY (`configid`),
  KEY `suiteid` (`suiteid`),
  CONSTRAINT `suite_config_ibfk_1` FOREIGN KEY (`suiteid`) REFERENCES `suites` (`suiteid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `suites`
--

DROP TABLE IF EXISTS `suites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `suites` (
  `suiteid` int(11) NOT NULL AUTO_INCREMENT,
  `suitename` varchar(40) DEFAULT NULL,
  `description` varchar(500) NOT NULL DEFAULT '',
  PRIMARY KEY (`suiteid`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tests`
--

DROP TABLE IF EXISTS `tests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tests` (
  `testid` int(11) NOT NULL AUTO_INCREMENT,
  `suiteid` int(11) NOT NULL,
  `testname` varchar(40) DEFAULT NULL,
  PRIMARY KEY (`testid`),
  KEY `suiteid` (`suiteid`),
  CONSTRAINT `tests_ibfk_1` FOREIGN KEY (`suiteid`) REFERENCES `suites` (`suiteid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
