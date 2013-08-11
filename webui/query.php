<?php

function invalid() {
	die('please, inform a valid SHA1 hash');
}

if (!isset($_GET['sha']))
	invalid();

if (empty($_GET['sha']))
	invalid();

$sha=strtolower($_GET['sha']);
$tam=strlen($sha);

if ($tam != 40)
	invalid();

for ($i=0; $i<$tam; $i++) {
	if (!ctype_alnum($sha[$i]))
		invalid();
}

$dir="/home/aleph/reports";
$file="$dir/$sha.txt";

echo '<pre>';

if (file_exists($file))
	echo htmlspecialchars(file_get_contents($file));
else
	echo 'report not found. be patient...';

echo '</pre>';

?>
