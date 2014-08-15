<?php

function check_group($username) {
	$output = array();

	exec("groups $username", $output);

	if (!isset($output[0]))
		return false;

	$v = explode(' ', $output[0]);

	foreach ($v as $i)
		if ($i == 'aleph-users')
			return true;

	return false;
}

function check_password($username, $password) {
	$stream = expect_popen("su $username");
	$cases = array(
	    // array(pattern, value to return if pattern matched)
	    array('Password:', 'pw'),
	);

	ini_set("expect.timeout", 5);

	while (1) {
		switch (expect_expectl($stream, $cases)) {
			case 'pw':
				fwrite($stream, "$password\n");
				break 2;
			case EXP_TIMEOUT:
			case EXP_EOF:
				break 2; // break both the switch statement and the while loop
			default:
				die('error on executaion!');
		}
	}

	$line = fgets($stream);
	$line = fgets($stream, 19);
	fclose($stream);
	return !($line == 'su: Authentication');
}

function login_page() {
	echo '<form method=post>
<input type=text name=un required><br />
<input type=password name=pw required></br >
<input type=submit value=login>
</form>';
}

function auth() {
	$un = escapeshellcmd(strip_tags($_POST['un']));
	$pw = escapeshellcmd(strip_tags($_POST['pw']));

	if (strlen($un) < 3 || strlen($un) > 16 || strlen($pw) < 6)
		return false;

	if (!ctype_lower($un))
		return false;

	if (!preg_match('/^[a-zA-z0-9 ]+$/', $pw))
		return false;

	if (!check_group($un) || !check_password($un, $pw))
		return false;

	return true;
}

function process_auth() {
	if (auth()) {
      //session_set_cookie_params(3600, '/', '', true, true);
      session_start();
		$_SESSION['logged'] = $_POST['un'];
		header('Location: /index.php');
	}
	else {
		echo '<html><head><meta http-equiv="refresh" content="2; url=/"></head><body>Access denied.</body></html>';
	}
}

if (isset($_POST['un']) && isset($_POST['pw']))
	process_auth();
else
	header('Location: /');
?>
