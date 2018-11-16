<?php
  $conn = new mysqli($servername, $username, $password, $dbname);
	if ($conn->connect_error) {
		die("Connection failed: " . $conn->connect_error);
	} 

	$sql = "INSERT INTO record (time, location, temperature, humidity, rain) VALUES ('".htmlspecialchars($_GET['time'])."', '".htmlspecialchars($_GET['location'])."', '".htmlspecialchars($_GET['temperature'])."', '".htmlspecialchars($_GET['humidity'])."', '".htmlspecialchars($_GET['rain'])."')";

	if ($conn->query($sql) === TRUE) {
		echo "New record created successfully";
	} else {
		echo "Error: " . $sql . "<br>" . $conn->error;
	}

	$conn->close();
?>
