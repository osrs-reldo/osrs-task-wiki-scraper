import traceback
import mwparserfromhell as mw
import api
import util
import league_utils
from typing import *


def run():
	tasks = []
	task_not_found_id = 90000
	duplicate_store = {}
	duplicates = []

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

	for category in categories:
		pageName = "Shattered Relics League/Tasks/" + category
		page = api.query_page(pageName)
		print("Scraping from '" + pageName + "'")
		try:
			code = mw.parse(page, skip_style_tags=True)
			sections = code.get_sections(levels=[1,2,3])
			for section in sections:
				sectionName = section.get(0)
				for row in util.each_row("SRLTaskRow", section):
					task = {}
					if "id" in row and row["id"] != "":
						task["id"] = int(row["id"])
					else:
						task["id"] = task_not_found_id
						task_not_found_id += 1
					task.update(league_utils.convert_league_row_to_task(row, sectionName))
					task["category"] = category
					tasks.append(task)
			tasks = sorted(tasks, key = lambda t: t["id"])

		except (KeyboardInterrupt, SystemExit):
			raise
		except:
			traceback.print_exc()
	
	# Quality checks
	if len(duplicates) > 0:
		raise "Duplicates exist"
	if len(tasks) != 1260:
		raise "Tasks length does not match expected task count: " + len(tasks) + "/1260"

	skipSort = True
	util.write_list_json("out/league3_tasks.json", "out/min/league3_tasks.min.json", tasks, skipSort)