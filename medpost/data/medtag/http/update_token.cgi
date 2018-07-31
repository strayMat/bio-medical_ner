#!/usr/bin/perl -w

require "cgi-lib.perl";
require "db-lib.perl";

print &PrintHeader;

if (! &ReadParse(*input))
{
	# CgiDie('Error reading form');
	# exit(1);
}

$num_words = $input{"num_words"};
$num_words = 0 if (! $num_words);

$corpus = $input{"corpus"};
$excerpt_id = $input{"excerpt_id"};
$excerpt_num = $input{"excerpt_num"};
$list_id = $input{"list_id"};
$after_next = $input{"after_next"};
$comment = $input{"comment"};

if ($after_next == 0)
{
	$next_id = $excerpt_id;
	$excerpt_num = $excerpt_num - 1;
	$excerpt_num = 0 if ($excerpt_num <= 0);
} else
{
	$next_id = $input{"next_id"};		# If successful, go to next
						# Otherwise, return and display a status
}

# Update the excerpt comment, this should only update if there was a change

$q_corpus_cd = $corpus;
$q_corpus_cd =~ s/\/.*//g;
$q_corpus_cd =~ s/\'/\'\'/g;
$q_corpus_cd = "'$q_corpus_cd'" if ($q_corpus_cd);

$q_comment = $comment;
$q_comment =~ s/\'/\'\'/g;
$q_comment = "'$q_comment'" if ($q_comment);

$upd_comment = 0;
if ($q_corpus_cd)
{
	$q_comment = "null" if (! $q_comment);
	$sql = "update excerpt set comment = $q_comment where excerpt_id = '$excerpt_id' and corpus_cd = $q_corpus_cd";
	$rows = db_do($sql);

	if (! defined($rows))
	{
		$status .= "An error occurred:" . db_err() . "<br>$sql";
		$dbh->rollback();
		$next_id = $excerpt_id;

		$excerpt_num-- if ($after_next);
		$excerpt_num = 0 if ($excerpt_num <= 0);

		goto RET;
	} elsif ($rows == 1)
	{
		$upd_comment = 1;
	}
}

# Correct the tags of idioms first

$last_t = "";
for (my $i = $num_words - 1; $i >= 0; $i--)
{
	$t = $input{"tag_${i}"};
	if ($t =~ /\+/ && $last_t)
	{
		$t = "${last_t}\+";
		$input{"tag_${i}"} = $t;
	}
	$last_t = $t if ($t !~ /\+/);
}

$num_tokens = 0;
for ($i = 0; $i < $num_words; $i++)
{
	# $w = $input{"word_${i}"};
	$t = $input{"tag_${i}"};
	$ot = $input{"old_tag_${i}"};
	next if ($t eq $ot);
	$fo = $input{"first_offs_${i}"};
	$id = $input{"annotation_id_${i}"};

	$t =~ s/\'/\'\'/g;
	$wh = "annotation_id = $id";
	# $wh = "excerpt_id = '$excerpt_id' and first_offs = '$fo' and text_type = 'token'";

	$sql = "insert into annotation_history select 'update_token',now(),annotation.* from annotation where $wh";
	$rows = db_do($sql);

	if (defined($rows) && $rows == 1)
	{
		$sql = "update annotation set annotation = '$t', status_date = now(), status_cd = 'open' where $wh";
		$rows = db_do($sql);
	}

        if (! defined($rows) || $rows != 1)
        {
                $status .= "An error occurred:" . db_err() . "<br>$sql";
		$dbh->rollback();
		$next_id = $excerpt_id;
		last;
        }

	$num_tokens++;
}
$dbh->commit();

if (! $status)
{
	if ($num_tokens > 0)
	{
		$status = "$num_tokens annotation(s) updated."
	} else
	{
		$status = "no annotations changes.";
	}
}

RET:

# Forward to the editor, or to the previous if there was an error

if ($next_id eq "")
{
	$next_id = next_excerpt($excerpt_id, $corpus, $list_id);
}

if ($next_id eq "")
{
	$next_id = $excerpt_id;
}

$ret = "edit_token.cgi?excerpt_id=$next_id";
$ret .= "&excerpt_num=$excerpt_num" if ($excerpt_num);
$ret .= "&corpus=$corpus" if ($corpus);
$ret .= "&list_id=$list_id" if ($list_id);
$status =~ s/\;//g if ($status);
$status = "updated comment, $status" if ($upd_comment && $status);
$status = "updated comment." if ($upd_comment && ! $status);
$ret .= "&status=$status" if ($status);

# print $ret;

print "<script language=\"JavaScript\">
window.location.replace(\"$ret\");
</script>
";

