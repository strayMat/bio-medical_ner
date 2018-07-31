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
$excerpt_id = "P07504457A03" if (! $excerpt_id);
$excerpt_num = $input{"excerpt_num"};
$excerpt_num = 1 if (! $excerpt_num);
$status = $input{"status"};
$annotation = $input{"annotation"};
$annotation_type_cd = $input{"annotation_type_cd"};
$corpus = $input{"corpus"};
($corpus_cd, $subcorpus_cd) = split(/\//, $corpus);
$list_id = $input{"list_id"};
$noedit = $input{"noedit"};


print "<title>Edit phrases for $excerpt_id</title>\n";

print `cat getSelected.js` if (! $noedit);

@word = ();
@tag = ();
$num_words = 0;

for (db_query("select text,annotation,comment,corpus_cd,first_offs,last_offs,annotation_type_cd,annotation_id from annotation " .
	"where excerpt_id = '$excerpt_id' and text_type = 'phrase' order by first_offs"))
{
	@ary = @{$_};

	if ($corpus_cd && $corpus_cd ne $ary[3])
	{
		next;
	}

	$text[$num_phrases] = $ary[0];
	$annotation[$num_phrases] = $ary[1];
	$comment[$num_phrases] = $ary[2];
	$corpus_cd = $ary[3] if (! $corpus_cd);
	$corpus = $corpus_cd if (! $corpus);
	$first_offs[$num_phrases] = $ary[4];
	$last_offs[$num_phrases] = $ary[5];
	$annotation_type_cd[$num_phrases] = $ary[6];
	$annotation_id[$num_phrases] = $ary[7];

	$num_phrases++;
}

# Get the next excerpt_id

$next_id = next_excerpt($excerpt_id, $corpus, $list_id);

print "<table width=100%><tr>\n";
print "<td><font size=6>Excerpt";
print " $excerpt_num" if ($excerpt_num);
print ": $excerpt_id";
print "</font></td>\n";
print "<td align=right><font size=6>Corpus: $corpus</font></td>\n" if ($corpus);
print "</tr></table>\n";
# print " <br>List: $list_id\n" if ($list_id);
print "<p>\n";

if ($status)
{
	print "<table><tr><td width=20>&nbsp;</td><td>Status of last operation:</td><td>$status</td></tr></table>\n";
	print "<p>\n";
}

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

$nxt = $list_id ? "from list $list_id" : ($corpus ? "from corpus $corpus" : "");

print "<tr>\n";
print "<td align=center width=50%><a href=\"print_token.cgi?excerpt_id=$excerpt_id&excerpt_num=$excerpt_num$args\">View tokens</a>\n";
print "&nbsp; &nbsp; <a href=\"edit_token.cgi?excerpt_id=$excerpt_id&excerpt_num=$excerpt_num$args\">Edit tokens</a>";
print "</td>\n";
if ($next_id)
{
	$n = $excerpt_num + 1;
	$args .= "&excerpt_num=$n" if ($excerpt_num);
	print "<td align=center><a href=\"edit_phrase.cgi?excerpt_id=$next_id$args\">Next $nxt: $next_id</a></td>\n"
} else
{
	print "<td align=center>No more excerpts $nxt</td>\n"
}
print "</tr>\n";

$k = 0;
print "<tr><td colspan=2 onkeydown=\"return getSelected()\">\n";
for (db_query("SELECT text,corpus_cd,subcorpus_cd from excerpt where excerpt_id = '$excerpt_id'"))
{
	@ary = @{$_};
	$text = $ary[0];

	$corpus_cd = $ary[1] if (! $corpus_cd);
	$subcorpus_cd = $ary[2] if (! $subcorpus_cd);

	print "<font size=6>";
	for ($j = 0; $j < length($text); $j++)
	{
		$c = substr($text, $j, 1);
		if ($c =~ /\s/)
		{
			print "$c";
			next;
		}
		$one_sub = 0;
		for ($i = 1; $i <= $num_phrases; $i++)
		{
			if ($k == $first_offs[$i-1])
			{
				print "<sub><font size=3>";
				print "," if ($one_sub);
				print "$i</font></sub>";
				$one_sub = 1;
			}
		}
		for ($i = 1; $i <= $num_phrases; $i++)
		{
			if ($k == $first_offs[$i-1])
			{
				print "<font color=red>";
			}
		}
		print "<!--${k}o-->" if (! $noedit);
		print "$c";
		print "<!--${k}o-->" if (! $noedit);
		for ($i = 1; $i <= $num_phrases; $i++)
		{
			if ($k == $last_offs[$i-1])
			{
				print "</font>";
			}
		}
		$k++;
	}
	print "</font>\n";
	last;
}
print "\n";
print "</td></tr>\n";
print "</table>\n";

$corpus = "$corpus_cd/$subcorpus_cd" if (! $corpus);

print "<form name=insert_phrase action=insert_phrase.cgi>\n";
print "\n<table border width=100%>\n";
print "<tr><th>#</th><th>text</th><th>annotation</th><th>type</th><th>comment</th>\n";
print "<th>delete?</th>\n" if (! $noedit);
print "</tr>\n";

for ($i = 0; $i < $num_phrases; $i++)
{
	$j = $i + 1;
	print "<tr><td>$j.</td>\n";
	print "<td>$text[$i]</td>\n";
	print "<td>$annotation[$i]</td>\n";
	print "<td>$annotation_type_cd[$i]</td>\n";
	print "<td>$comment[$i]&nbsp;</td>\n";

	$args = "annotation_id=$annotation_id[$i]";
	$args .= "&excerpt_id=$excerpt_id";
	$args .= "&excerpt_num=$excerpt_num" if ($excerpt_num);
	if ($list_id)
	{
		$args .= "&list_id=$list_id" if ($list_id);
	} elsif ($corpus)
	{
		$args .= "&corpus=$corpus" if ($corpus);
	}
	$args .= "&annotation=$annotation[$i]";
	$args .= "&annotation_type_cd=$annotation_type_cd[$i]";

	print "<td><a href=\"delete_phrase.cgi?$args\">delete</a></td>\n" if (! $noedit);
	print "</td></tr>\n";
}

$annotation_type_cd = "genetag" if ($annotation_type_cd eq "" && $corpus_cd =~ /genetag/);
$annotation = "GENE" if ($annotation eq "" && $corpus_cd =~ /genetag/);

if (! $noedit)
{
	print "
	<tr>
	<td align=center valign=top><input type=submit value=add></td>
	<td align=center><input type=text name=text valign=top>
	<table><tr><td><input type=text size=4 name=first_offs></td>
		   <td><input type=text size=4 name=last_offs></td>
		   <td><input type=button value=\"(get)\" onclick=\"getSelected()\"></td></tr>
	       <tr><td align=center>first</td><td align=center>last</td></tr>
	</table>
	</td>

	<td align=center valign=top><input type=text name=annotation value=\"$annotation\" size=10></td>
	<td align=center valign=top><input type=text name=annotation_type_cd value=\"$annotation_type_cd\" size=10></td>
	<td align=center valign=top><input type=text name=comment></td>
	<td>&nbsp;</td>
	</tr>
	";
}

print "
</table>

<input type=hidden name=corpus value=\"$corpus\">
<input type=hidden name=excerpt_id value=\"$excerpt_id\">
<input type=hidden name=excerpt_num value=\"$excerpt_num\">\n";
# <tr><td colspan=5 align=center></tr>

print "<input type=hidden name=list_id value=\"$list_id\">\n" if ($list_id);

print "</form>\n";

print `cat footer.html`;

