<html>
<head>
<title>aleph</title>
<link rel="stylesheet" type="text/css" href="style.css">
</head>
<body>
<?php include 'die.php'; include 'topbar.php'; ?>
<center>
<div>
<font style="font-size: 60px; letter-spacing: 6px;">aleph</font><br />
<font style="font-size: 10px; ">malware sourcing and analysis system</font>
</div>
<br /><br />

<div class=adminbox>
<?php

function isup($svc) {
	$ret = 1;
	passthru("pgrep $svc >/dev/null", $ret);

	if ($ret)
		return '<strong>NOT</strong>';
}

function create_svc_line($name, $svc, $cmd=NULL) {
	if (!isset($cmd))
		$cmd = $svc;

	echo "$name service: $svc is " . isup($cmd)  . ' running<br />';
}

function create_line($name, $cmd=NULL) {
	if (!isset($cmd))
		$cmd = $name;

	echo "$name: "; system($cmd); echo '<br />';
}

create_line('system', 'uname -a');
create_line('uptime');
create_line('memory', "free -th | grep  Mem: | awk '{ print $2, \"- used:\", $3, \"- free:\", $4 }'");
create_svc_line('aleph', 'alephd', 'alephd.sh');
create_svc_line('email', 'exim4');
create_svc_line('ftp', 'vsftpd');
create_svc_line('ssh', 'sshd');
create_line('users', 'getent group aleph-users | cut -d: -f4');

?>

</div>

<div style="clear: both; font-size: 12px;">
<br /><br /><br />
aleph (c) <?php echo date('Y'); ?>
</center>

</body>
</head>
</html>
