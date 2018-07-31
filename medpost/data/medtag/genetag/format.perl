
# Read a tagged file and get the GENE tagged phrases
# and write them in the same format as Gold.format

$tagsep = "_";
$option_id = "line";

$last_tag = "";
while (<>)
{
	chomp;

	if ($option_id eq "line" && (!/$tagsep/))
	{
		$id = $_;
		next;
	}

	$tok = 0;
	$offs = 0;
	$gene = "";
	for (split(/\s+/, $_))
	{
		$tok++;
		if ($option_id eq "token" && $tok == 0)
		{
			$id = $_;
			next;
		}

		$w = $_;
		$t = "";
		if ($w =~ /(.*)${tagsep}(.*)/)
		{
			$w = $1;
			$t = $2;
		}

		if ($gene && $t ne $last_tag)
		{
			$last_offs = $offs - 1;
			print "$id|$first_offs $last_offs|$gene\n";
			$gene = "";
		}

		if ($t =~ /GENE/)
		{
			$first_offs = $offs if ($gene eq "");
			$gene .= " " if ($gene);
			$gene .= $w;
		}

		$offs += length($w);
		$last_tag = $t;
	}

	# If the line ends with a gene, print it

	if ($gene)
	{
		$last_offs = $offs - 1;
		print "$id|$first_offs $last_offs|$gene\n";
		$gene = "";
	}
}
