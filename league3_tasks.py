import traceback
import mwparserfromhell as mw
import api
import util
import csv
import league_utils
from typing import *

categories = [
	"General",
	"Fishing",
	"Agility",
	"Attack",
	"Clues",
	"Combat",
	"Construction",
	"Cooking",
	"Crafting",
	"Defence",
	"Farming",
	"Firemaking",
	"Fletching",
	"Herblore",
	"Hitpoints",
	"Hunter",
	"Magic",
	"Mining",
	"Prayer",
	"Quests",
	"Ranged",
	"Runecraft",
	"Slayer",
	"Smithing",
	"Strength",
	"Thieving",
	"Woodcutting"
]

def scrape_wiki():
	tasks = {}
	task_not_found_id = 90000
	duplicates = []

	for category in categories:
		page_name = "Shattered Relics League/Tasks/" + category
		page = api.query_page(page_name)
		print("Scraping from '" + page_name + "'")
		try:
			code = mw.parse(page, skip_style_tags=True)
			sectionName = "" # tier was stripped out into a part we can't associate; fine because game is source now
			for row in util.each_row("SRLTaskRow", code):
				task = {}
				id = -1
				if "id" in row and row["id"] != "":
					id = int(row["id"])
				else:
					id = task_not_found_id
					task_not_found_id += 1
				task.update(league_utils.convert_league_row_to_task(row, sectionName))
				task["category"] = category
				tasks[id] = task

		except (KeyboardInterrupt, SystemExit):
			raise
		except:
			traceback.print_exc()
	
	# Quality checks
	if len(duplicates) > 0:
		raise Exception("Duplicates exist")
	if len(tasks) != 1260:
		raise Exception("Tasks length does not match expected task count: %s/1260" % len(tasks))
	return tasks

def parse_client_data():
	tasks = {}
	csv.register_dialect("piper", delimiter="|", quoting=csv.QUOTE_NONE)
	with open("client-data/league3_data.txt", "rt", encoding="utf8") as csvfile:
		for task in csv.DictReader(csvfile, dialect="piper"):
			id = int(task["id"])
			tasks[id] = task
	return tasks

def get_tier_from_icon(icon):
	icon = int(icon)
	if icon == 2316:
		return "Beginner"
	if icon == 2317:
		return "Easy"
	if icon == 2318:
		return "Medium"
	if icon == 2319:
		return "Hard"
	if icon == 2320:
		return "Elite"
	if icon == 3739:
		return "Master"

def run():
	task_data = parse_client_data()
	wiki_tasks = scrape_wiki()

	combined_tasks = []
	for id in task_data:
		if id not in wiki_tasks:
			print("Wiki task id not found when joining data with wiki: id=%s" % id)
			continue
		wiki_task = wiki_tasks[id]
		combined_task = task_data[id]
		combined_task["name"] = combined_task["name"].replace("\xa0", " ")
		combined_task["skills"] = wiki_task["skills"]
		combined_task["other"] = wiki_task["other"]
		combined_task["tier"] = get_tier_from_icon(combined_task["tier_icon"])
		combined_tasks.append(combined_task)

	skipSort = True
	util.write_list_json("out/league3_tasks.json", "out/min/league3_tasks.min.json", combined_tasks, skipSort)
