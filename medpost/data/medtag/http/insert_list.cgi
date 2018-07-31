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
$comment = $input{"comment"};
$query = $input{"query"};

$q_list_id = $list_id;
$q_list_id =~ s/\'/\'\'/g;
$q_list_id = "'$q_list_id'";

$q_comment = $comment;
$q_comment =~ s/\'/\'\'/g;
$q_comment = "'$q_comment'";

$q_query = $query;
$q_query =~ s/\'/\'\'/g;
$q_query = "'$q_query'";

$status = "";

if ($list_id && $query)
{

	$ins ="insert into excerpt_list (list_id, query, comment) values ($q_list_id, $q_query, $q_comment)";
	$rows = db_do($ins);

	if (! defined($rows))
	{
		$status .= "An error occurred (undefined).";
		$status .= "<br>$ins\n";
	} elsif (! $rows)
	{
		$status .= "An error occurred (no rows added).";
		$status .= "<br>$ins\n";
	} else
	{
		$status .= "$rows rows added.";
	}
} else
{
	$status .= "Must enter list name and a query.";
}

# Redirect the output

$ret = "sum_lists.cgi?status=$status";

print "
<script language=\"JavaScript\">
window.location.replace(\"$ret\");
</script>
";

