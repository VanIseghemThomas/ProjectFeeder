-- MySQL dump 10.13  Distrib 5.7.17, for Win64 (x86_64)
--
-- Host: localhost    Database: feederdb
-- ------------------------------------------------------
-- Server version	5.5.5-10.3.17-MariaDB-0+deb10u1

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
-- Table structure for table `tblactuators`
--

DROP TABLE IF EXISTS `tblactuators`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tblactuators` (
  `actuatorid` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) DEFAULT NULL,
  `description` varchar(450) NOT NULL,
  PRIMARY KEY (`actuatorid`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tblactuators`
--

LOCK TABLES `tblactuators` WRITE;
/*!40000 ALTER TABLE `tblactuators` DISABLE KEYS */;
INSERT INTO `tblactuators` VALUES (1,'stepper','Used to dispence the food'),(2,'LED','Used for indication purposes');
/*!40000 ALTER TABLE `tblactuators` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbllogs`
--

DROP TABLE IF EXISTS `tbllogs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbllogs` (
  `logid` int(11) NOT NULL AUTO_INCREMENT,
  `timestamp` datetime NOT NULL,
  `value` float NOT NULL,
  `unit` varchar(45) NOT NULL,
  `presetid` int(11) DEFAULT NULL,
  `sensorid` int(11) DEFAULT NULL,
  `actuatorid` int(11) DEFAULT NULL,
  PRIMARY KEY (`logid`),
  KEY `fk_sensors_idx` (`sensorid`),
  KEY `fk_actuators_idx` (`actuatorid`),
  KEY `fk_preset_idx` (`presetid`),
  CONSTRAINT `fk_actuators` FOREIGN KEY (`actuatorid`) REFERENCES `tblactuators` (`actuatorid`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_preset` FOREIGN KEY (`presetid`) REFERENCES `tblpresets` (`presetid`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_sensors` FOREIGN KEY (`sensorid`) REFERENCES `tblsensors` (`sensorid`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=3208 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbllogs`
--

LOCK TABLES `tbllogs` WRITE;
/*!40000 ALTER TABLE `tbllogs` DISABLE KEYS */;
INSERT INTO `tbllogs` VALUES (3189,'2020-06-14 18:04:11',78,'mm',NULL,3,NULL),(3190,'2020-06-14 18:04:20',80,'mm',NULL,3,NULL),(3191,'2020-06-14 18:04:26',50,'Steps',NULL,NULL,1),(3192,'2020-06-14 18:04:26',80,'mm',NULL,3,NULL),(3193,'2020-06-14 18:05:27',81,'mm',NULL,3,NULL),(3194,'2020-06-14 18:05:36',85,'mm',NULL,3,NULL),(3195,'2020-06-14 18:06:18',84,'mm',NULL,3,NULL),(3196,'2020-06-14 18:06:20',87,'mm',NULL,3,NULL),(3197,'2020-06-14 18:06:36',1,'BIN',NULL,2,NULL),(3198,'2020-06-14 18:06:46',0,'BIN',NULL,2,NULL),(3199,'2020-06-14 18:06:47',1,'BIN',NULL,2,NULL),(3200,'2020-06-14 18:06:48',0,'BIN',NULL,2,NULL),(3201,'2020-06-14 18:06:49',1,'BIN',NULL,2,NULL),(3202,'2020-06-14 18:06:50',0,'BIN',NULL,2,NULL),(3203,'2020-06-14 18:06:51',1,'BIN',NULL,2,NULL),(3204,'2020-06-14 18:07:10',0,'BIN',NULL,2,NULL),(3205,'2020-06-14 18:07:10',1,'BIN',NULL,2,NULL),(3206,'2020-06-14 18:07:12',0,'BIN',NULL,2,NULL),(3207,'2020-06-14 18:07:22',78,'mm',NULL,3,NULL);
/*!40000 ALTER TABLE `tbllogs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tblpresets`
--

DROP TABLE IF EXISTS `tblpresets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tblpresets` (
  `presetid` int(11) NOT NULL AUTO_INCREMENT,
  `dayofweek` varchar(45) NOT NULL,
  `hour` int(11) NOT NULL,
  `minute` int(11) DEFAULT NULL,
  `amount` int(11) NOT NULL,
  PRIMARY KEY (`presetid`)
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tblpresets`
--

LOCK TABLES `tblpresets` WRITE;
/*!40000 ALTER TABLE `tblpresets` DISABLE KEYS */;
INSERT INTO `tblpresets` VALUES (51,'Wednesday',9,45,20),(55,'Thursday',13,49,80);
/*!40000 ALTER TABLE `tblpresets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tblsensors`
--

DROP TABLE IF EXISTS `tblsensors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tblsensors` (
  `sensorid` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `description` varchar(450) DEFAULT NULL,
  PRIMARY KEY (`sensorid`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tblsensors`
--

LOCK TABLES `tblsensors` WRITE;
/*!40000 ALTER TABLE `tblsensors` DISABLE KEYS */;
INSERT INTO `tblsensors` VALUES (1,'loadcell','Used to measure the weight of food available for the pet'),(2,'ir sensor','Used to detect pet eating'),(3,'tof sensor','Used to measure how much the container is filled up');
/*!40000 ALTER TABLE `tblsensors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `vw_measurements`
--

DROP TABLE IF EXISTS `vw_measurements`;
/*!50001 DROP VIEW IF EXISTS `vw_measurements`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `vw_measurements` AS SELECT 
 1 AS `logid`,
 1 AS `timestamp`,
 1 AS `value`,
 1 AS `unit`,
 1 AS `sensorid`,
 1 AS `name`*/;
SET character_set_client = @saved_cs_client;

--
-- Final view structure for view `vw_measurements`
--

/*!50001 DROP VIEW IF EXISTS `vw_measurements`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`mysql`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_measurements` AS select `l`.`logid` AS `logid`,`l`.`timestamp` AS `timestamp`,`l`.`value` AS `value`,`l`.`unit` AS `unit`,`s`.`sensorid` AS `sensorid`,`s`.`name` AS `name` from (`tblsensors` `s` left join `tbllogs` `l` on(`l`.`sensorid` = `s`.`sensorid`)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-06-14 18:18:27
