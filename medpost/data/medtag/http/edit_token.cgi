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
$list_id = $input{"list_id"};
$corpus = $input{"corpus"};
$status = $input{"status"};

@tags = (XX,"XX+",CC,CS,CSN,CST,DB,DD,EX,"GE",II,JJ,JJR,JJT,MC,NN,NNP,NNS,PN,PND,PNG,PNR,
RR,RRR,RRT,SYM,TO,VM,VBB,VBD,VBG,VBI,VBN,VBZ,VDB,VDD,VDG,VDI,VDN,VDZ,VHB,VHD,
VHG,VHI,VHN,VHZ,VVB,VVD,VVG,VVI,VVN,VVZ,VVNJ,VVGJ,VVGN,"(",")",",",".",":","``","''");

$add_xx = 1;

%likely_tags = (
	JJ	=> [VVNJ],
	RR	=> [II],
	NN	=> [VVGN],
	VVGN	=> [NN],
	VVG	=> [VVGN]);

%likely_tags = (
	"CC+"	=> [CC],
	"RR+"	=> [RR],
	"II+"	=> [II],
	"CS+"	=> [CS],
	CC	=> [DD,NN,NNS,PNR],
	PNR	=> [CS,DD,PNG,PND,PN],
	PNG	=> [PN,PND,PNR],
	CR	=> [CS,DD,PNR],
	CS	=> [II,RR,PNR,CST,CC,CSN],
	CST	=> [PNR,CS,DD,PND],
	CSN	=> [II],
	DB	=> [CC,CS,DD,II,RR],
	DD	=> [DB,CC,NN,RR,PND,RRT,JJ],
	II	=> [CC,PNR,CS,JJ,RR,TO,CST,JJ,CSN],
	JJ	=> [JJR,JJT,NN,RR,VVB,VVD,VVG,VVGJ,VVN,VVNJ,MC,II,DD],
	JJR	=> [JJ,JJT,NN,RR,RRR],
	JJT	=> [RRT,DD,PND],
	MC	=> [JJ, PN],
	NN	=> [JJ,MC,NNP,NNS,PN,RR,VVB,VVG,VVNJ,VVGJ,VVGN,VVI,VVN,RRR,RRT,SYM],
	NNP	=> [NN],
	NNS	=> [II,JJ,NN,NNP,VVD,VVZ,VVN],
	PN	=> [NN,MC,PNR],
	PND	=> [PN,NN,MC,DD,RR,JJ,II],
	RR	=> [CC,DD,II,JJ,JJR,NN,RRT,VVB,VVN,CS,PND],
	RRR	=> [JJR,NN,RR],
	RRT	=> [JJT,NN,DD],
	SYM	=> [CC],
	TO	=> [II],
	VBI	=> [VBB],
	VHI	=> [VHB],
	VVB	=> [CS,JJ,JJR,NN,VVI,VVZ],
	VVD	=> [NN,VVN,VVNJ],
	VVG	=> [NN,VVGJ,VVGN],
	VVGJ	=> [NN,VVG,VVN,JJ,VVGN],
	VVI	=> [JJ,NN,VVB],
	VVN	=> [NN,VVD,VVG,VVNJ,JJ,RR,VVI,VVB],
	VVNJ	=> [JJ,VVD,VVN,NN],
	VVGN	=> [VVGJ,VVG,NN],
	VVZ	=> [NNS,VVB],
	VBGN	=> [VVGN]);

$alltags = $input{alltags};

@word = ();
@tag = ();
@comments = ();
$num_words = 0;
$num_comments = 0;

for (db_query("select text,annotation,corpus_cd,first_offs,annotation_id,comment from annotation where excerpt_id = '$excerpt_id' and text_type = 'token' order by corpus_cd,first_offs"))
{
	@ary = @{$_};

	$word[$num_words] = $ary[0];
	$tag[$num_words] = $ary[1];
	$corpus = $ary[2] if (! $corpus);
	$first_offs[$num_words] = $ary[3];
	$annotation_id[$num_words] = $ary[4];
	$comments[$num_words] = $ary[5];
	$num_comments++ if ($comments[$num_words]);
	$num_words++;
}

print "<title>Edit tokens for $excerpt_id</title>\n";

if ($num_words == 0)
{
	print "<h2>Token annotations not found for $excerpt_id.\n";
	exit(0);
}

# Get the next excerpt_id

$next_id = next_excerpt($excerpt_id, $corpus, $list_id);

print "<table width=100%><tr>\n";
print "<td><font size=6>Excerpt";
print " $excerpt_num" if ($excerpt_num);
print ": $excerpt_id</font></td>\n";
print "<td align=right><font size=6>Corpus: $corpus</font></td>\n" if ($corpus);
print "</tr></table>\n";
# print " <br>List: $list_id\n" if ($list_id);

if ($status)
{
        print "<table><tr><td width=20>&nbsp;</td><td>Status of last operation:</td><td>$status</td></tr></table>\n";
        print "<p>\n";
}

print "<table border width=100%>\n";

$exargs = "excerpt_id=$excerpt_id&excerpt_num=$excerpt_num";

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
print "<td align=center width=50%><a href=\"print_token.cgi?$exargs$args\">View tokens</a>\n";
print " &nbsp; &nbsp; <a href=\"edit_phrase.cgi?$exargs$args\">Edit phrases</a></td>\n";
if ($next_id)
{
	$n = $excerpt_num + 1;
	print "<td align=center><a href=\"edit_token.cgi?excerpt_id=$next_id&excerpt_num=$n$args\">Next $nxt: $next_id</a></td>\n"
} else
{
	print "<td align=center>No more excerpts $nxt</td>\n"
}
print "</tr>\n";

print "<tr><td colspan=2>\n";
for (db_query("SELECT text,comment from excerpt where excerpt_id = '$excerpt_id'"))
{
	@ary = @{$_};
	print "$ary[0]\n";
	$comment = $ary[1];
}
print "</td></tr>\n";

print "<form method=post action=\"update_token.cgi\" name=sentence>\n";
print "<tr><td colspan=2>\n";

print "<input type=hidden name=num_words value=$num_words>\n";
print "<input type=hidden name=excerpt_id value=\"$excerpt_id\">\n";
$n = $excerpt_num + 1;
print "<input type=hidden name=excerpt_num value=\"$n\">\n";
print "<input type=hidden name=list_id value=\"$list_id\">\n" if ($list_id);
print "<input type=hidden name=corpus value=\"$corpus\">\n" if ($corpus);
print "<input type=hidden name=next_id value=\"$next_id\">\n" if ($next_id);

for ($i = 0; $i < $num_words; $i++)
{
	print "<input type=hidden name=word_$i value=\"$word[$i]\">\n";
	print "<input type=hidden name=annotation_id_$i value=\"$annotation_id[$i]\">\n";
	print "<input type=hidden name=first_offs_$i value=\"$first_offs[$i]\">\n";
	print "<input type=hidden name=old_tag_$i value=\"$tag[$i]\">\n";
	print "<font size=6>$word[$i]</font>";

	@options = ();
	if ($alltags)
	{
		@options = @tags;
	} elsif ($likely_tags{$tag[$i]})
	{
		@options = @{$likely_tags{$tag[$i]}};
		unshift @options, $tag[$i];
		push @options, "." if ($word[$i] =~ /\./);
		push @options, "XX" if ($add_xx);
		push @options, "XX+" if ($add_xx);
	} elsif ($tag[$i] eq "XX")
	{
		@options = @tags;
	}

	if (@options)
	{
		$found = 0;
		for $t (@options)
		{
			$found = 1 if ($tag[$i] eq $t);
		}

		if (! $found)
		{
			unshift @options, $tag[$i];
		}

		print "&nbsp;<select name=tag_$i size=1>\n";
		for $t (@options)
		{
			print "<option";
			print " selected" if ($tag[$i] eq $t);
			print ">$t</option>\n";
		}
		print "</select>\n";
	} else
	{
		print "<sub>$tag[$i]</sub>\n" if ($tag[$i] =~ /[A-Z]/);
		print "<input type=hidden name=tag_$i value=\"$tag[$i]\">\n";
	}
}

print "<p>\n";
print "<center>\n";
print "<input type=submit value=Save>\n";
print "<br>(after save, display <input type=radio name=after_next value=1 checked> the next excerpt, or\n";
print "<input type=radio name=after_next value=0> this excerpt)\n";
print "</center>\n";
print "</td></tr>\n";

print "<tr><td colspan=2>Comment:&nbsp;<textarea rows=3 cols=80 name=comment>$comment</textarea></td></tr>\n";
print "</form>\n";

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



if (! $alltags)
{
	print "<p><a href=\"edit_token.cgi?$exargs&alltags=1$args\">";
	print "<center>Only the likely tag options are displayed, to show all tag options, click here.</center>";
	print "</a>\n";
} else
{
	print "<p><a href=\"edit_token.cgi?$exargs$args\">";
	print "<center>All tag options are displayed, to display only likely tag options, click here.</center>";
	print "</a>\n";
}

print `cat footer.html`;

