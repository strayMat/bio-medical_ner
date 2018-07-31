<script language="JavaScript">

function getSelected()
{
	var range = document.selection.createRange();
	var e = window.event;
	e.cancelBubble = true;

	if (! range) return;

	var regexp = /[0-9]+(?=o-->)/g;

	var offs = range.htmlText.match(regexp);

	if (! offs) return;

	var mx = offs[0];
	var mn = offs[0];

	for (var i = 0; i < offs.length; i++)
	{
		mn = Math.min(offs[i], mn);
		mx = Math.max(offs[i], mx);
	}


	document.insert_phrase.first_offs.value = mn;
	document.insert_phrase.last_offs.value = mx;

	var text = range.htmlText;

	// remove all comments

	text = text.replace(/<!--[0-9]+o-->/g,"");

	// remove font directives

	text = text.replace(/<[/]?font[^>]*>/ig,"");

	// remove subscripted text

	text = text.replace(/[<]sub.*?sub[>]/ig,"");

	// Replace some escapes

	text = text.replace(/&lt;/g, "<");
	text = text.replace(/&gt;/g, ">");
	text = text.replace(/&amp;/g, "&");

	// Remove leading and trailing spaces

	text = text.replace(/\s+$/, "");
	text = text.replace(/^\s+/, "");

	document.insert_phrase.text.value = text;

	document.insert_phrase.annotation.select();
	return false;
}

</script>

