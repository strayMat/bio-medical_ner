#!/usr/bin/perl -w

require "cgi-lib.perl";
require "db-lib.perl";

print &PrintHeader;
print "<title>MedTag summary of corpora</title>\n";

print "<h2>Current listing of corpora:</h2>\n<p>\n";

$n = 0;
$tot = 0;

# $exp_status = ",max(case a.status_cd when 'closed' then null when null then null else a.status_cd end)";

$query = "select c.corpus_cd, c.subcorpus_cd, count(distinct c.excerpt_id), max(d.comment) " .
	"from excerpt c left join corpus d on ifnull(c.subcorpus_cd,c.corpus_cd) = d.corpus_cd " .
	"group by c.corpus_cd, c.subcorpus_cd";

print "<table border>\n";
print "<tr><th></th><th>corpus</th><th>excerpts</th><th>comment</th></tr>\n";
for (db_query($query))
{
	@ary = @{$_};
	$n++;
	# print "<br>" . join ("\t", @ary), "\n";
	$corpus = $ary[0];
	$corpus .= "/$ary[1]" if ($ary[1]);
	$count = $ary[2];
	$comment = $ary[3];
	# $open = $ary[3];
	print "<tr><td>$n.</td><td><a href=\"list.cgi?corpus=$corpus\">$corpus</a></td>\n";
	print "<td align=center>$count</td>\n";
	print "<td>$comment</td>\n";
	print "</tr>\n";
	$tot += $count;
}
print "</table>\n";

print "\n\n";
print `cat footer.html`;

