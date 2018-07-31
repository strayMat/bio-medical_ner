#!/opt/local/bin/perl

require "cgi-lib.perl";
require "db-lib.perl";

print &PrintHeader;

if (! &ReadParse(*input))
{
	# CgiDie('Error reading form');
	# exit(1);
}

$excerpt_id = $input{"excerpt_id"};
# $excerpt_id = "P07504457A03" if (! $excerpt_id);
$excerpt_num = $input{"excerpt_num"};

$corpus = $input{"corpus"};
$list_id = $input{"list_id"};
$annotation = $input{"annotation"};
$annotation_type_cd = $input{"annotation_type_cd"};
$annotation_id = $input{"annotation_id"};

$wh ="annotation_id=$annotation_id";

$sql = "insert into annotation_history select 'delete_phrase',now(),annotation.* from annotation where $wh";
$rows = db_do($sql);

if ($rows > 0)
{
	$sql ="delete from annotation where $wh";
	$rows = db_do($sql);
}

$status = "";
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

$ret = "edit_phrase.cgi?excerpt_id=$excerpt_id";
$ret .= "&excerpt_num=$excerpt_num" if ($excerpt_num);
$ret .= "&status=$status" if ($status);
$ret .= "&annotation=$annotation" if ($annotation);
$ret .= "&annotation_type_cd=$annotation_type_cd" if ($annotation_type_cd);
$ret .= "&corpus=$corpus" if ($corpus);
$ret .= "&list_id=$list_id" if ($list_id);
print "

<script language=\"JavaScript\">
window.location.replace(\"$ret\");
</script>
";
