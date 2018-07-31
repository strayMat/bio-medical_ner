# The corpus table contains a list of corpora by name and a comment for each

drop table corpus;
create table corpus (
	corpus_cd char(100) primary key,	# The code used for the corpus
	comment text				# Any comment can be entered describing the corpus
);

drop table annotation_type;
create table annotation_type (
	annotation_type_cd char(100) primary key,	# Any code used for annotation type
	comment text				# Any comment can be entered describing the annotation
);

# The excerpt table contains text that has annotations in one or more corpus.
# Our system requires that each excerpt has a unique identifier,
# regardless of the corpus it occurs in.
# The excerpt_cd tells how the excerpt was obtained, which will usually correspond
# to a method employed by some corpus for obtaining sentences from text.
# The excerpt_id itself should be interpretable by the same process.

drop table excerpt;
create table excerpt (
	excerpt_id char(100) not null,		# Unique identifier
	corpus_cd char(100) not null,		# The corpus to which the excerpt belongs
	subcorpus_cd char(100),			# An optional sub-corpus
	source text,				# Where this text came from
	text text,				# The actual full text
	comment text,				# Any comment may be entered
	primary key (excerpt_id, corpus_cd)	# This says how excerpts are defined (unique per corpus)
);

# The annotation table contains annotations for sections of text (tokens or phrases)
# by reference to the excerpt table.

# IMPORTANT!
#
# any changes to these fields need to be duplicated in
# the annotation_history table.

drop table annotation;
create table annotation (
	annotation_id int unsigned not null auto_increment primary key,
	excerpt_id char(100),			# Reference to the excerpt
	corpus_cd char(100),			# and corpus
	text_type char(100),			# The type of text, e.g. token, phrase
	first_offs int,				# First character offset in the excerpt, not counting white space
	last_offs int,				# Last character offset in the excerpt, not counting white space
	text text,				# The actual text, it saves time to have it here
	token_offs int,				# Optional token offset (useful for backward compatability)
	annotation text,			# The actual annotation
	annotation_type_cd char(100),		# The annotation type
	status_cd char(100),			# The status, e.g. open, closed, or advisory
	status_date date,			# The data that the status was updated
	reviewer char(100),			# The name of the person responsible for the annotation
	comment text				# Any comment may be entered
);

drop table excerpt_list;
create table excerpt_list (
	list_id	char(100) primary key,		# a unique identifier
	query text,				# a valid SQL from and where clause
	comment text				# any comment may be entered
);

drop table annotation_history;
create table annotation_history (
	operation char(100),			# The operation
	timestamp datetime,			# The time that it occurred
# from annotation table:
	annotation_id int unsigned,
	excerpt_id char(100),
	corpus_cd char(100),
	text_type char(100),
	first_offs int,
	last_offs int,
	text text,
	token_offs int,
	annotation text,
	annotation_type_cd char(100),		# The annotation type
	status_cd char(100),
	status_date date,
	reviewer char(100),
	comment text
);

