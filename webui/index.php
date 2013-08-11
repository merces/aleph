<html>
<head>
<title>aleph</title>
<link rel="stylesheet" type="text/css" href="style.css">
</head>
<body>
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
<form action="query.php" method="get">
<input type="text" name="sha" size="40" autofocus required pattern="[a-fA-F0-9]{40}"
value="enter valid sha1..." required>
<br />
<br />
<input type="submit" value="Search">
<input type="submit" disabled value="Upload">
</form>
</center>

<div class="latest">
<p><strong>Latest analysis</strong></p>
<?php

exec('tail ../db.csv | tac', $out);

foreach($out as $v) {
	$temp = explode(',', $v);
	echo "$temp[0] - <a href=\"query.php?sha=$temp[1]\">$temp[2]</a><br />";
}

?>
</div>

<div class="stats">
<p><strong>Statistics</strong></p>
<?php
unset($out);
exec('date | cut -c-10', $out);
exec('grep \'^' . $out[0] . '\' ../db.csv | wc -l', $out);
echo "$out[1] files analyzed today<br />";
unset($out);
exec('wc -l ../db.csv | cut -d\' \' -f1; du -h ../store | cut -f1', $out);
echo "$out[0] total<br />$out[1] of data";
?>
</div>

<div class="topext">
<p><strong>Top 5 extensions</strong></p>
<?php
unset($out);
echo '<pre>';
system('../stats.sh | head -5');
echo '</pre>';
?>
</div>

<center>
<div style="clear: both; font-size: 12px;">
<br /><br /><br />
aleph (c) 2013
</div>
</center>


</body>
</head>
</html>
