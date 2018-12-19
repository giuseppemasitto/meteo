SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

CREATE TABLE `record` (
  `id` int(11) NOT NULL,
  `data` datetime NOT NULL,
  `pioggia` int(11) NOT NULL,
  `temperatura` float NOT NULL,
  `umidita` float NOT NULL,
  `pressione` int(11) NOT NULL,
  `vento` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE `record`
  ADD PRIMARY KEY (`id`);
