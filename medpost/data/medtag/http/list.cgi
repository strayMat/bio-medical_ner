#!/usr/bin/perl -w

require "cgi-lib.perl";
require "db-lib.perl";

print &PrintHeader;

if (! &ReadParse(*input))
{
}

$corpus = $input{"corpus"}; $corpus = "" if (! $corpus);
($corpus_cd, $subcorpus_cd) = split(/\//, $corpus);
$list_id = $input{"list_id"};

my $sth;

$query = "";
if ($list_id)
{
	$l = $list_id;
	$l =~ s/\'/\'\'/g;
	$query = db_val("select query from excerpt_list where list_id = '$l'");
	# print "<p>Querying list_id ($l): $query<p>\n";
	$list = $list_id;
}

if ($query eq "" && $corpus_cd)
{
	$query = "from excerpt where corpus_cd = '$corpus_cd'";
	$query .= " and subcorpus_cd = '$subcorpus_cd'" if ($subcorpus_cd);
	$list = "corpus $corpus";
} elsif ($query eq "")
{
	$query = "from excerpt";
	$list = "all excerpts";
}

$pre = ($query =~ /excerpt e/) ? "e." : "";
$fields = "${pre}excerpt_id";

if ($query =~ /from excerpt/)
{
	$fields .= ", concat(${pre}corpus_cd,if(isnull(${pre}subcorpus_cd), '', concat('/',${pre}subcorpus_cd)))";
} else
{
	$fields .= ", ${pre}corpus_cd";
}

$query = "select distinct $fields $query order by 1";

print "<title>MedTag listing of $list</title>\n";
print "<h2>Current listing of $list:</h2>\n<p>\n";

# print "$query\n";

print "<table>\n";
$num = 0;
for (db_query($query))
{
	@ary = @{$_};

	$excerpt_id = $ary[0];
	$corpus = $ary[1];
	$num++;

	$args = "?excerpt_id=$excerpt_id";
	$args .= "&excerpt_num=$num" if ($num);
	$args .= "&corpus=$corpus" if ($corpus);
	$args .= "&list_id=$list_id" if ($list_id);

	print "<tr><td>$num.</td>\n";
	print "<td>$corpus&nbsp;&nbsp;</td>\n";
	print "<td>$excerpt_id&nbsp;&nbsp;</td>\n";
	print "<td>";
	print "<a href=\"print_token.cgi$args\">View tokens</a>\n";
	print "&nbsp;&nbsp;<a href=\"edit_token.cgi$args\">Edit tokens</a>\n";
	print "&nbsp;&nbsp;<a href=\"edit_phrase.cgi$args\">Edit phrases</a>\n";
	print "</td>\n";
	print "</tr>\n";
}
print "</table>\n";

print "\n\n";
print `cat footer.html`;

