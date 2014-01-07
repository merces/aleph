<?php
isset($_SESSION) or session_start();
if (!isset($_SESSION['logged']))
	header('Location: /');
?>
