#!/usr/bin/perl -w

use DBI;

my $dsn = "DBI:mysql:LOCAL-DATABASE-NAME";
my $user_name = "LOCAL-USER-NAME";
my $password = "LOCAL-PASSWORD";
my %attr = ( PrintError => 0, RaiseError => 0 );

$dbh = DBI->connect($dsn, $user_name, $password, \%attr)
	or bail_out("Could not connect to server");
$dbh->{AutoCommit} = 0;

sub db_do($)
{
	return $dbh->do($_[0]);
}

sub db_query($)
{
	my $query = shift;

	my $sth = $dbh->prepare($query)
		or bail_out("Could not prepare query");

	$sth->execute()
		or bail_out("Could not execute query");

	my @ret;

	while (my @ary = $sth->fetchrow_array())
	{
		push @ret, [ @ary ];
	}

	$sth->finish();

	return @ret;
}

sub db_val($)
{
	my $query = shift;

	my $sth = $dbh->prepare($query)
		or bail_out("Could not prepare query");

	$sth->execute()
		or bail_out("Could not execute query");

	my $ret;

	while (my @ary = $sth->fetchrow_array())
	{
		$ret = $ary[0];
		last;
	}

	$sth->finish();

	return $ret;
}

sub db_err()
{
	return "$DBI::err ($DBI::errstr)";
}

sub bail_out
{
	my $message = shift;
	die "<br>$message\n<br>Error $DBI::err ($DBI::errstr)\n";
}


# This function gets the next excerpt
# the db environment is required and
# should aleady be running

# require "db-lib.perl";
# print next_excerpt("P08549784X05", "medpost/mb", "") . "\n";

sub next_excerpt($$$)
{
	my $excerpt_id = shift;
	my $corpus = shift;
	my $list_id = shift;
	my $query = "";

	if ($list_id)
	{
		my $l = $list_id;
		$l =~ s/\'/\'\'/g;
		for (db_query("select query from excerpt_list where list_id = '$l'"))
		{
			@ary = @{$_};
			$query = $ary[0];
			last;
		}
	}

	if ($query)
	{
		$field = ($query =~ /excerpt e/) ? "e.excerpt_id" : "excerpt_id";
		$query = "select min($field) $query and $field > '$excerpt_id'";
	} elsif ($corpus)
	{
		my ($corpus_cd, $subcorpus_cd) = split(/\//, $corpus);
		$query = "select min(excerpt_id) from excerpt where corpus_cd = '$corpus_cd' and excerpt_id > '$excerpt_id'";
		$query .= " and subcorpus_cd = '$subcorpus_cd'" if ($subcorpus_cd);
	} else
	{
		$query = "select min(excerpt_id) from excerpt where excerpt_id > '$excerpt_id'";
	}

	my $next_excerpt_id = "";
	for (db_query($query))
	{
		@ary = @{$_};
		$next_excerpt_id = $ary[0];
		last;
	}
	return $next_excerpt_id;
}

1;
