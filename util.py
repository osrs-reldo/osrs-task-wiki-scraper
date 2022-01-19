import os
import json
import collections
import re
import mwparserfromhell as mw
from typing import *

VERSION_EXTRACTOR = re.compile(r"(.*?)([0-9]+)?$")

def each_row(rowName: str, code):
	rows = code.filter_templates(matches=lambda t: t.name.matches(rowName))
	if len(rows) < 1:
		return

	for row in rows:
		result = {}
		for param in row.params:
			key = str(param.name)
			value = str(param.value)
			result[key] = value

		yield result



def each_version(template_name: str, code, include_base: bool = False,
	mergable_keys: List[str] = None) -> Iterator[Tuple[int, Dict[str, Any]]]:
	"""
	each_version is a generator that yields each version of an infobox
	with variants, such as {{Infobox Item}} on [[Ring of charos]]
	"""
	if mergable_keys is None:
		mergable_keys = ["version", "image", "caption"]
	infoboxes = code.filter_templates(matches=lambda t: t.name.matches(template_name))
	if len(infoboxes) < 1:
		return
	for infobox in infoboxes:
		base: Dict[str, str] = {}
		versions: Dict[int, Dict[str, str]] = {}
		for param in infobox.params:
			matcher = VERSION_EXTRACTOR.match(str(param.name).strip())
			if matcher is None:
				raise AssertionError()
			primary = matcher.group(1)
			dic = base
			if matcher.group(2) != None:
				version = int(matcher.group(2))
				if not version in versions:
					versions[version] = {}
				dic = versions[version]
			dic[primary] = param.value
		if len(versions) == 0:
			yield (-1, base)
		else:
			all_mergable = True
			for versionID, versionDict in versions.items():
				for key in versionDict:
					if not key in mergable_keys:
						all_mergable = False
			if all_mergable:
				yield (-1, base)
			else:
				if include_base:
					yield (-1, base)
				for versionID, versionDict in versions.items():
					yield (versionID, {**base, **versionDict})


def write_json(name: str, minName: str, docs: Dict[Any, Dict[str, Any]]):
	items = []
	for (id, doc) in docs.items():
		named = {k: v for (k, v) in doc.items() if not k.startswith("__")}
		nameless = named.copy()
		if "name" in nameless:
			del nameless["name"]
		if nameless != {}:
			items.append((id, named, nameless))

	withNames = collections.OrderedDict([(k, v) for (k, v, _) in items])
	with open(name, "w+") as fi:
		json.dump(withNames, fi, indent=2)

	withoutNames = collections.OrderedDict([(k, v) for (k, _, v) in items])
	with open(minName, "w+") as fi:
		json.dump(withoutNames, fi, separators=(",", ":"))

def write_list_json(name: str, minName: str, docs: List[Dict[str, Any]], skipSort: bool = False):
	with open(name, "w+") as fi:
		json.dump(docs, fi, indent=2)

	with open(minName, "w+") as fi:
		json.dump(docs, fi, separators=(",", ":"))

def create_dir_if_not_exists(path):
	exists = os.path.exists(path)

	if not exists:
		# Create a new directory because it does not exist 
		os.makedirs(path)

def get_doc_for_id_string(source: str, version: Dict[str, str], docs: Dict[str, Dict],
	allow_duplicates: bool = False) -> Optional[Dict]:
	if not "id" in version:
		print("page {} is missing an id".format(source))
		return None

	ids = [id for id in map(lambda id: id.strip(), str(version["id"]).split(",")) if id != "" and id.isdigit()]

	if len(ids) == 0:
		print("page {} is has an empty id".format(source))
		return None

	doc = {}
	doc["__source__"] = source
	invalid = False
	for id in ids:
		if not allow_duplicates and id in docs:
			print("page {} is has the same id as {}".format(source, docs[id]["__source__"]))
			invalid = True
		docs[id] = doc

	if invalid:
		return None
	return doc


def copy(name: Union[str, Tuple[str, str]],
	doc: Dict,
	version: Dict[str, Any],
	convert: Callable[[Any], Any] = lambda x: x) -> bool:
	src_name = name if isinstance(name, str) else name[0]
	dst_name = name if isinstance(name, str) else name[1]
	if not src_name in version:
		return False
	strval = str(version[src_name]).strip()
	if strval == "":
		return False
	newval = convert(strval)
	if not newval:
		return False
	doc[dst_name] = newval
	return True


def has_template(name: str, code) -> bool:
	return len(code.filter_templates(matches=lambda t: t.name.matches(name))) != 0

def strip(input: str) -> str:
	stripped = input.strip()
	stripped = stripped.replace("===", "")
	stripped = stripped.replace("==", "")
	stripped = stripped.replace("{{sic}}", "")

	stripped = parse_scps(stripped)
	stripped = parse_named_links(stripped)
	stripped = parse_links(stripped)
	stripped = parse_twitter_links(stripped)
	
	return stripped

def parse_links(input: str) -> str:
	ONLY_LINK_PATTERN = re.compile(r"[\[\{][\[\{]([^\]}\|]+?)[\]\}][\]\}]")
	matcher = ONLY_LINK_PATTERN.search(input)
	if matcher is None:
		return input
	return ONLY_LINK_PATTERN.sub("\\1", input)

def parse_named_links(input: str) -> str:
	NAMED_LINK_PATTERN = re.compile(r"[\[\{][\[\{]([^\]}\|]+?)\|([^\]}\|]+?)[\]\}][\]\}]")
	matcher = NAMED_LINK_PATTERN.search(input)
	if matcher is None:
		return input
	return NAMED_LINK_PATTERN.sub("\\2", input)


def parse_scps(input: str) -> str:
	SCP_PATTERN = re.compile(r"{{SCP\|(.+?)}}")
	matcher = SCP_PATTERN.search(input)
	if matcher is None:
		return input
	scp_content = matcher.group(1)
	scp_elements = scp_content.split("|")
	if (len(scp_elements) == 1):
		return scp_elements[0]
	return SCP_PATTERN.sub(scp_elements[0] + " " + scp_elements[1], input)

def parse_twitter_links(input: str) -> str:
	TWITTER_PATTERN = re.compile(r"[{\[][{\[]CiteTwitter.+?[}\]][}\]]")
	return TWITTER_PATTERN.sub("", input)
