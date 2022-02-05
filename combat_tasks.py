import traceback
import mwparserfromhell as mw
import api
import csv
import util
from typing import *

def parse_client_data():
	tasks = {}
	csv.register_dialect("piper", delimiter="|", quoting=csv.QUOTE_NONE)
	with open("client-data/combat_tasks_data.txt", "rt", encoding="utf8") as csvfile:
		for task in csv.DictReader(csvfile, dialect="piper"):
			id = int(task["id"])
			tasks[id] = task
	return tasks

def get_tier_from_icon(icon):
	icon = int(icon)
	if icon == 3399:
		return "Easy"
	if icon == 3400:
		return "Medium"
	if icon == 3401:
		return "Hard"
	if icon == 3402:
		return "Elite"
	if icon == 3403:
		return "Master"
	if icon == 3404:
		return "Grandmaster"

def run():
	task_data = parse_client_data()

	tasks = []
	for id in task_data:
		task_datum = task_data[id]
		task = {}
		task["id"] = task_datum["id"]
		task["monster"] = task_datum["monster"]
		task["name"] = task_datum["name"].replace("\xa0", " ")
		task["description"] = task_datum["description"]
		task["category"] = task_datum["type"]
		task["tier"] = get_tier_from_icon(task_datum["tier_icon"])
		task["clientSortId"] = task_datum["client_sort_id"]
		tasks.append(task)

	skipSort = True
	util.write_list_json("out/combat_tasks.json", "out/min/combat_tasks.min.json", tasks, skipSort)

# Deprecated - relies solely on game data now, because there is no metadata in the wiki
def scrape_wiki():
	tiers = ["Easy", "Medium", "Hard", "Elite", "Master", "Grandmaster"]
	tasks = []

	for tier in tiers:
		page = api.query_page("Combat_Achievements/" + tier)

		try:
			code = mw.parse(page, skip_style_tags=True)
			for section in code.get_sections():
				sectionName = section.get(0).title
				if sectionName != "Tasks":
					continue

				for row in util.each_row("CATaskRow", section):
					task = convert_combat_task_row_to_task(row, tier)
					tasks.append(task)

		except (KeyboardInterrupt, SystemExit):
			raise
		except:
			print("Task {} failed:".format(tier))
			traceback.print_exc()
	return tasks

def convert_combat_task_row_to_task(row, sectionName: str):
	task = {
		"monster": util.strip(str(row['1'])),
		"name": util.strip(str(row['2'])),
		"description": util.strip(str(row['3'])),
		"category": util.strip(str(row["4"])),
		"tier": util.strip(sectionName)
	}

	return task
