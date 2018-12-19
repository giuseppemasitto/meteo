<?php
	include('config.php');

	$conn = mysqli_connect($database['host'], $database['username'], $database['password'], $database['database']);
	if (mysqli_connect_errno()) {
		die("code:error_connect_database");
	} 
	
	if (htmlspecialchars($_GET['key']) == $client['key']) {
		switch($_GET['action']) {
			case "requestid":
				$result = mysqli_query($conn, "SELECT id FROM record ORDER BY id DESC LIMIT 1");
				if ($result) {
					// echo "code:success_requestid";
					$row = mysqli_fetch_array($result);
					echo $row[0];
				} else {
					echo "code:error_requestid";
				}
				break;
			case "sync":
				if (mysqli_multi_query($conn, $_GET['query']) === TRUE) {
					echo "code:success_sync";
				} else {
					echo "code:error_sync";
				}
				break;
			case "live":
				if (mysqli_query($conn, $_GET['query']) === TRUE) {
					echo "code:success_live";
				} else {
					echo "code:error_live";
				}
				break;
		}
	} else {
		echo "code:error_notauthorized";
	}
	
	mysqli_close($conn);
?>
