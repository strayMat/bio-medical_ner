#!/usr/bin/perl -w

require "cgi-lib.perl";
require "db-lib.perl";

print &PrintHeader;

if (! &ReadParse(*input))
{
}

$corpus = $input{"corpus"}; $corpus = "" if (! $corpus);
($corpus_cd, $subcorpus_cd) = split(/\//, $corpus);
$match = $input{"match"}; $match = "" if (! $match);
$match_before = $input{"match_before"};
$match_after = $input{"match_after"};
$match_case = $input{"match_case"};
$match_annotation = $input{"match_annotation"}; $match_annotation = "" if (! $match_annotation);
$list_id = $input{"list_id"};
$comment = $input{"comment"};

my $sth;

$match_str = "$match";
$match_str = "$match_before\%$match_str" if ($match_before);
$match_str = "$match_str\%$match_after" if ($match_after);
$match_str = "\%$match_str\%" if ($match_str);

$cond = "";
$list = "";

if ($corpus_cd)
{
	$cond .= " and " if ($cond);
	$cond .= " e.corpus_cd like '$corpus_cd' ";

	$list .= "corpus $corpus_cd";
}

if ($subcorpus_cd)
{
	$cond .= " and " if ($cond);
	$cond .= " e.subcorpus_cd like '$subcorpus_cd' ";

	$list .= ", " if ($list);
	$list .= "subcorpus $subcorpus_cd";
}

($w, $t) = split(/\_/, $match_annotation);

if ($w || $t)
{
	$cond .= " and " if ($cond);
	$cond .= " binary " if ($w && $match_case);
	$cond .= " a.text rlike '$w'" if ($w);
	$cond .= " and " if ($w && $t);
	$cond .= " a.annotation like '$t' " if ($t);
	$cond .= " and e.excerpt_id = a.excerpt_id and e.corpus_cd = a.corpus_cd ";

	$list .= ", " if ($list);
	$list .= "annotation $match_annotation";
}

if ($match_str)
{
	$cond .= " and " if ($cond);
	$cond .= " binary " if ($match_case);
	$cond .= " e.text like '$match_str' ";

	$list .= ", " if ($list);
	$list .= "$match_before before" if ($match_before);
	$list .= ", " if ($list);
	$list .= "matching $match" if ($match);
	$list .= ", " if ($list);
	$list .= "$match after" if ($match_after);
}

if ($cond)
{

	$list_query = "from excerpt e";
	$list_query .= ", annotation a" if ($match_annotation);
	$list_query .= " where $cond";

	$query = "select distinct e.excerpt_id, e.corpus_cd, e.subcorpus_cd $list_query order by 1";
} else
{
	print "Please enter a search condition.\n";
	exit;
}

if ($list_query && $list_id)
{
	$q_list_id = $list_id;
	$q_list_id =~ s/\'/\'\'/g;
	$q_list_id = "'$q_list_id'";

	$cmd = "delete from excerpt_list where list_id = $q_list_id";
	db_do($cmd);

	$q_list_query = $list_query;
	$q_list_query =~ s/\'/\'\'/g;
	$q_list_query = "'$q_list_query'";

	$q_comment = "null";
	if ($comment)
	{
		$q_comment = $comment;
		$q_comment =~ s/\'/\'\'/g;
		$q_comment = "'$q_comment'";
	}

	$cmd = "insert into excerpt_list (list_id, query, comment)";
	$cmd .= " values ($q_list_id, $q_list_query, $q_comment)";
	db_do($cmd);
}

# print "\n$query\n\n";

print "<title>MedTag listing of $list</title>\n";
print "<h2>Current listing of $list:</h2>\n<p>\n";

print "<table>\n";
$num = 0;
for (db_query($query))
{
	@ary = @{$_};

	$excerpt_id = $ary[0];
	$corpus_cd = "$ary[1]";
	$corpus_cd .= "/$ary[2]" if ($ary[2]);
	$num++;

	$args = "?excerpt_id=$excerpt_id";
	$args .= "&excerpt_num=$num" if ($num);
	$args .= "&corpus=$corpus" if ($corpus);
	$args .= "&list_id=$list_id" if ($list_id);

	print "<tr><td>$num.</td>\n";
	print "<td>$corpus_cd&nbsp;&nbsp;</td>\n";
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

