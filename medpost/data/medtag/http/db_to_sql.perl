
# Generate SQL to load data from a native source formatted file.

while (<>)
{
	chomp;

	if (/^>>(.*)/)
	{
		print_sql() if ($table);

		$table = lc($1);
		%fields = ();
	}
	if (/^([A-Z\_]+):\s+(.*)/)
	{
		$fields{$1} = $2;
	}
}
print_sql() if ($table);

sub print_sql()
{
	for (keys %fields)
	{
		$fields{$_} =~ s/\'/\'\'/g;
	}

	print "insert into $table (";
	$first_col = 1;
	for $column (sort keys %fields)
	{
		print ", " if ($first_col == 0);
		print lc($column);
		$first_col = 0;
	}
	print ")\nvalues (";

	$first_col = 1;
	for $column (sort keys %fields)
	{
		print ", " if ($first_col == 0);
		print "'$fields{$column}'";
		$first_col = 0;
	}
	print ");\n";
}

