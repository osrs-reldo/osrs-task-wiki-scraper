import os
import json
from datetime import datetime
import urllib.request
import urllib.parse
from typing import *

use_cache: bool = True
user_agent: Dict[str, str] = {"User-Agent": "Runelite Task Scraper/1.0"}

def prep_cache_name(name):
	return name.replace("/", ".") + datetime.now().strftime("%Y%m%d")

def get_wiki_api(args: Dict[str, str], continueKey: str) -> Iterator[Any]:
	args["format"] = "json"
	while True:
		url = "https://oldschool.runescape.wiki/api.php?" + urllib.parse.urlencode(args)
		print("Grabbing " + url)
		with urllib.request.urlopen(urllib.request.Request(url, headers=user_agent)) as raw:
			js = json.load(raw)

		yield js
		if "continue" in js:
			args[continueKey] = js["continue"][continueKey]
		else:
			return

def query_page(page_name: str) -> Dict[str, str]:
	cache_file_name = prep_cache_name(page_name) + ".cache.json"
	if use_cache and os.path.isfile(cache_file_name):
		with open(cache_file_name, "r") as fi:
			print("opening %s from cache" % page_name)
			return json.load(fi)

	for res in get_wiki_api(
		{
		"action": "query",
		"prop": "pageprops",
		"titles": page_name
		}, "ppcontinue"):
		for id, page in res["query"]["pages"].items():
			pageid = page["pageid"]
			if pageid is not None:
				break
		if pageid is not None:
			break

	for res in get_wiki_api(
		{
		"action": "query",
		"prop": "revisions",
		"rvprop": "content",
		"pageids": pageid,
		}, "rvcontinue"):
		for id, page in res["query"]["pages"].items():
			with open(cache_file_name, "w+") as fi:
				json.dump(page["revisions"][0]["*"], fi)
			return page["revisions"][0]["*"]


def query_category(category_name: str) -> Dict[str, str]:
	"""
	query_category returns a dict of page title to page wikitext
	you can then use mwparserfromhell to parse the wikitext into
	an ast
	"""
	cache_file_name = prep_cache_name(category_name) + ".cache.json"
	if use_cache and os.path.isfile(cache_file_name):
		with open(cache_file_name, "r") as fi:
			return json.load(fi)

	pageids = []
	for res in get_wiki_api(
		{
		"action": "query",
		"list": "categorymembers",
		"cmlimit": "500",
		"cmtitle": "Category:" + category_name,
		}, "cmcontinue"):

		for page in res["query"]["categorymembers"]:
			pageids.append(str(page["pageid"]))

	pages = {}
	for i in range(0, len(pageids), 50):
		for res in get_wiki_api(
			{
			"action": "query",
			"prop": "revisions",
			"rvprop": "content",
			"pageids": "|".join(pageids[i:i + 50]),
			}, "rvcontinue"):
			for id, page in res["query"]["pages"].items():
				pages[page["title"]] = page["revisions"][0]["*"]

	with open(cache_file_name, "w+") as fi:
		json.dump(pages, fi)

	return pages
