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

$corpus = $input{"corpus"};
($corpus_cd, $subcorpus_cd) = split(/\//, $corpus);
$list_id = $input{"list_id"};
$first_offs = $input{"first_offs"};
$last_offs = $input{"last_offs"};
$text = $input{"text"};
$annotation = $input{"annotation"};
$annotation_type_cd = $input{"annotation_type_cd"};
$comment = $input{"comment"};

$text =~ s/\s+$//; $text =~ s/^\s+//;
$annotation =~ s/\s+$//; $annotation =~ s/^\s+//;
$annotation_type_cd =~ s/\s+$//; $annotation_type_cd =~ s/^\s+//;
$comment =~ s/\s+$//; $comment =~ s/^\s+//;

$corpus_cd =~ s/\'/\'\'/g;
$text =~ s/\'/\'\'/g;
$annotation =~ s/\'/\'\'/g;
$annotation_type_cd =~ s/\'/\'\'/g;
$comment =~ s/\'/\'\'/g;

$p_corpus_cd = $corpus_cd ? "'$corpus_cd'" : "null";
$p_text = $text ? "'$text'" : "null";
$p_annotation = $annotation ? "'$annotation'" : "null";
$p_annotation_type_cd = $annotation_type_cd ? "'$annotation_type_cd'" : "null";
$p_comment = $comment ? "'$comment'" : "null";

$status = "";

if ($excerpt_id && $corpus_cd && length($first_offs) && length($last_offs) && $text && $annotation && $annotation_type_cd)
{

	$ins ="insert into annotation (excerpt_id, corpus_cd, text_type, first_offs, last_offs, text, annotation, annotation_type_cd, comment, status_cd, status_date) values ('$excerpt_id', $p_corpus_cd, 'phrase', $first_offs, $last_offs, $p_text, $p_annotation, $p_annotation_type_cd, $p_comment, 'open', now())";
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
	$status .= "Must enter text (with first and last character offsets), annotation, annotation type, and corpus.";
}

# Redirect the output

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

