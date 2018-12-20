<?php
	// importa il file di configurazione
	include('config.php');

	# inizializza la variabile per la gestione della connessione
	$conn = mysqli_connect($database['host'], $database['username'], $database['password'], $database['database']);
	if (mysqli_connect_errno()) {
		# gestisce l'errore della connessione
		die("code:error_connect_database");
	} 
	
	// se la chiave di sicurezza del client è uguale a quella del server remoto, allora continua
	if (htmlspecialchars($_GET['key']) == $client['key']) {
		switch($_GET['action']) {
			// Azione: 	requestid
			// Descrizione:	Ritorna l'ultimo ID cronologicamente
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
			// Azione:	sync
			// Descrizione: Esegue la query per la sincronizzazione dei server
			case "sync":
				if (mysqli_multi_query($conn, $_GET['query']) === TRUE) {
					echo "code:success_sync";
				} else {
					echo "code:error_sync";
				}
				break;
			// Azione:	live
			// Descrizione:	Esegue la query per il salvataggio
			case "live":
				if (mysqli_query($conn, $_GET['query']) === TRUE) {
					echo "code:success_live";
				} else {
					echo "code:error_live";
				}
				break;
		}
	} else {
		// genera un errore per la chiave di sicurezza
		echo "code:error_notauthorized";
	}
	
	// chiuse la connessione al database
	mysqli_close($conn);
?>
