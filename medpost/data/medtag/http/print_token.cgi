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
$excerpt_num = $input{"excerpt_num"};
$excerpt_nuk = 1 if (! $excerpt_num);
$list_id = $input{"list_id"};
$corpus = $input{"corpus"};
($corpus_cd, $subcorpus_cd) = split(/\//, $corpus);

# Debugging
if (! $excerpt_id)
{
	$excerpt_id = "P07504457A03";
	$corpus = "medpost/mb";
}

@word = ();
@tag = ();
@comments = ();
$num_words = 0;
$num_comments = 0;


$query =  "select text,annotation,corpus_cd,comment from annotation " .
	"where excerpt_id = '$excerpt_id' and text_type = 'token' ";
$query .= "and corpus_cd = '$corpus_cd' " if ($corpus_cd);
$query .= "order by first_offs";

# print "$query\n";

for (db_query($query))
{
	@ary = @{$_};
	$w = $ary[0];
	$t = $ary[1];
	$corpus = $ary[2] if (! $corpus);
	$comment = $ary[3];

	$word[$num_words] = $w;
	$tag[$num_words] = $t;
	$comments[$num_words] = $comment;
	$num_comments++ if ($comment);
	$num_words++;
}

print "<title>View tokens for $excerpt_id</title>\n";

if ($num_words == 0)
{
	print "<h2>Token annotations not found for $excerpt_id.\n";
	exit(0);
}

$next_id = next_excerpt($excerpt_id, $corpus, $list_id);

print "<table width=100%><tr>\n";
print "<td><font size=6>Excerpt";
print " $excerpt_num" if ($excerpt_num);
print ": $excerpt_id</font></td>\n";
print "<td align=right><font size=6>Corpus: $corpus</font></td>\n" if ($corpus);
print "</tr></table>\n";
# print " <br>List: $list_id\n" if ($list_id);

print "<table border width=100%>\n";

if ($list_id)
{
	$args = "&list_id=$list_id"
} elsif ($corpus)
{
	$args .= "&corpus=$corpus";
} else
{
	$args = "";
}

$nxt = $list_id ? "from list $list_id" : "from corpus $corpus";

print "<tr>\n";
print "<td align=center width=50%><a href=\"edit_token.cgi?excerpt_id=$excerpt_id$args&excerpt_num=$excerpt_num\">Edit tokens</a>\n";
print " &nbsp; &nbsp; <a href=\"edit_phrase.cgi?excerpt_id=$excerpt_id$args&excerpt_num=$excerpt_num\">Edit phrases</a></td>\n";

if ($next_id)
{
	$n = $excerpt_num + 1;
	print "<td align=center><a href=\"print_token.cgi?excerpt_id=$next_id$args&excerpt_num=$n\">Next $nxt: $next_id</a></td>\n"
} else
{
	print "<td align=center>No more excerpts $nxt</td>\n"
}
print "</tr>\n";

$comment = "";
print "<tr><td colspan=2>\n";
for (db_query("select text,comment from excerpt where excerpt_id = '$excerpt_id'"))
{
	@ary = @{$_};
	print "$ary[0]\n";
	$comment = $ary[1];
}
print "</td></tr>\n";

print "<tr><td colspan=2>\n";
for ($i = 0; $i < $num_words; $i++)
{
	# print "<table><tr><td>\n";
	print "<font size=6>$word[$i]</font>";
	if ($compare_errs && $tag[$i] ne $orig_tag[$i])
	{
		print "<sub>$tag[$i]<font color=red>/$orig_tag[$i]</font></sub>";
	} elsif ($tag[$i] =~ /[A-Z]/)
	{
		print "<sub>$tag[$i]</sub>";
	}
	# print "</td></tr><tr><td>\n";
	# print "$i\n";
	# print "</td></tr></table>\n";
	print "\n";
}
print "</td></tr>\n";

print "<tr><td colspan=2>Comment: $comment</td></tr>\n" if ($comment);

print "</table>\n";

if ($num_comments > 0)
{
	print "\n<p><b>Token comments</b><br>\n";
	print "<table border width=100%><tr><th>tok#</th><th>token</th><th>annotation</th><th>comment</th></tr>\n";
	for $i (0 .. $#comments)
	{
		next if (! $comments[$i]);
		$j = $i + 1;
		print "<tr><td align=center>$j</td><td align=center>$word[$i]</td><td align=center>$tag[$i]</td>\n";
		print "<td>$comments[$i]</td></tr>\n";
	}
	print"</table>\n";
}

print `cat footer.html`;

