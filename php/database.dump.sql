CREATE TABLE `record` (
  `id` int(11) NOT NULL,
  `time` text NOT NULL,
  `location` text NOT NULL,
  `temperature` text NOT NULL,
  `humidity` text NOT NULL,
  `rain` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

ALTER TABLE `record`
  ADD PRIMARY KEY (`id`);

ALTER TABLE `record`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;
COMMIT;
