#!/usr/bin/perl -w

require "cgi-lib.perl";
require "db-lib.perl";

print &PrintHeader;

if (! &ReadParse(*input))
{
}

$status = $input{"status"};

print "<title>MedTag summary of lists</title>\n";

print "<h2>Current listing of lists:</h2>\n<p>\n";

if ($status)
{
	print "$status\n<p>\n";
}

if (db_val("select count(*) from excerpt_list") == 0)
{
	print "<h2>No lists found.\n";
	exit;
}

print "<table border>\n";
print "<tr><th></th><th>list</th><th>excerpts</th><th>comment</th><th>query</th><th>delete?</th></tr>\n";

$n = 0;
for (db_query("select list_id,query,comment from excerpt_list order by list_id"))
{
	@ary = @{$_};
	$n++;
	$list_id = $ary[0];
	$query = $ary[1];
	$comment = $ary[2];

	$field = ($query =~ /excerpt e/) ? "e.excerpt_id" : "excerpt_id";
	$sql = "select count(distinct $field) $query";

	# print "$sql\n";

	for (db_query("$sql"))
	{
		@ary = @{$_};
		$count = $ary[0];
		print "<tr><td>$n.</td><td><a href=\"list.cgi?list_id=$list_id\">$list_id</a></td>\n";
		print "<td align=center>$count</td>\n";
		print "<td>$comment</td>\n";
		print "<td>$query</td>\n";
		print "<td><a href=\"delete_list.cgi?list_id=$list_id\">delete</a></td>\n";
		print "</tr>\n";
	}
}

print "
<form method=post action=insert_list.cgi>
<tr>
<td align=center><input type=submit value=\"add\"></td>
<td align=center><input type=text name=list_id></td>
<td>&nbsp;</td>
<td align=center><input type=text name=comment></td>
<td align=center><input type=text name=query></td>
<td>&nbsp;</td>
</tr>
</form>
</table>
";

print "\n\n";
print `cat footer.html`;

