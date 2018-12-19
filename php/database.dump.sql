SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

CREATE TABLE `record` (
  `id` int(11) NOT NULL,
  `data` datetime NOT NULL,
  `pioggia` int(11) NOT NULL,
  `temperatura` float NOT NULL,
  `umidita` float NOT NULL,
  `pressione` int(11) NOT NULL,
  `vento` text CHARACTER SET utf8mb4 NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `record_live` (
  `id` int(11) NOT NULL,
  `data` datetime NOT NULL,
  `pioggia` int(11) NOT NULL,
  `temperatura` float NOT NULL,
  `umidita` float NOT NULL,
  `pressione` int(11) NOT NULL,
  `vento` text CHARACTER SET utf8mb4 NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

ALTER TABLE `record`
  ADD PRIMARY KEY (`id`);
  
ALTER TABLE `record_live`
  ADD PRIMARY KEY (`id`);
