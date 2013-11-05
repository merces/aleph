<?php
session_start();
include 'die.php';
require_once "HTTP/Upload.php";

$upload = new HTTP_Upload("en");
$file = $upload->getFiles("f");

if ($file->isValid()) {
	$moved = $file->moveTo('/home/incoming/' . $_SESSION['logged'] . '/incoming/');
	$pear = new PEAR();
	if (!$pear->isError($moved)) {
		$msg = 'Success.';
	}
	else
		$msg = $moved->getMessage();
} elseif ($file->isMissing()) {
	$msg = "No file was provided.";
} elseif ($file->isError()) {
	$msg = $file->errorMsg();
}

echo '<html>
<head>
<meta http-equiv="refresh" content="2; url=/">
</head>
<body>'.$msg.'</body>
</html>';

?>
