<?php
	// variabili per la connesione al server mysql
	$database = array(
		'host'=>'hostname',
		'username'=>'username',
		'password'=>'password',
		'database'=>'database_name'
	);
	
	// imposta la chiave di sicurezza
	$client = array(
		'key'=>'chiave_di_sicurezza'
	);
	
	// imposta l'intervallo di ore da controllare per le previsioni meteo
	// il valore di default è 3
	$impostazioni = array(
		'range'=>'-6'
	);
?>
