<html>
<head>
<title>aleph</title>
<link rel="stylesheet" type="text/css" href="style.css">
</head>
<body>
<?php include 'topbar.php'; ?>
<center>
<div>
<font style="font-size: 60px; letter-spacing: 6px;">aleph</font><br />
<font style="font-size: 10px; ">malware sourcing and analysis system</font>
</div>
<br />
<img src="aleph.jpg" title="A tribute to Alberto Fabiano (1975 - 2013)">
<br />
<br />
<br />
<?php
	if (isset($_SESSION['logged']))
		include 'main.php';
	else {
?>
	<form action=login.php method=post>
	<input type="text" name="un" autofocus required pattern="[a-z]+" title="Username"><br />
	<input type="password" name="pw" required title="Password"></br >
	<input type="submit" value="login">
	</form>
<? } ?>

<div style="clear: both; font-size: 12px;">
<br /><br /><br />
aleph (c) <?php echo date('Y'); ?>
</center>

</body>
</head>
</html>
