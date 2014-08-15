<?php
	if (!isset($_SESSION))
		session_start();

	if (isset($_SESSION['logged']))
	{
		echo "<div id=topbar>Welcome back, " . $_SESSION['logged'] .
			'! [ <a class=topbar href="/">home</a> | '.
			'<a class=topbar href="admin.php">admin</a> | '.
			'<a class=topbar href="logout.php">logout</a>'.
			' ]</div>';
	}
?>
