#!/opt/local/bin/perl

require "cgi-lib.perl";
require "db-lib.perl";

print &PrintHeader;

if (! &ReadParse(*input))
{
	# CgiDie('Error reading form');
	# exit(1);
}

$list_id = $input{"list_id"};

$status = "";
if ($list_id eq "")
{
	$status = "no lists specified.";
} else
{

	$q_list_id = $list_id;
	$q_list_id =~ s/\'/\'\'/g;
	$q_list_id = "'$q_list_id'";

	$sql = "delete from excerpt_list where list_id = $q_list_id";
        $rows = db_do($sql);

	if (! defined($rows))
	{
		$status .= "An error occurred (undefined).";
		$status .= "<br>$sql";
	} elsif ($rows > 0)
	{
		$status .= "$rows rows deleted.";
	} else
	{
		$status .= "An error occurred (no rows deleted).";
		$status .= "<br>$sql";
	}
}


$ret = "sum_lists.cgi?status=$status";
print "

<script language=\"JavaScript\">
window.location.replace(\"$ret\");
</script>
";
