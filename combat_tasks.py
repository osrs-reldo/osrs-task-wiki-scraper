import traceback
import mwparserfromhell as mw
import api
import util
from typing import *


def run():
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

	skipSort = True
	util.write_list_json("out/combat_tasks.json", "out/combat_tasks.min.json", tasks, skipSort)

def convert_combat_task_row_to_task(row, sectionName: str):
	task = {
		"monster": util.strip(str(row['1'])),
		"name": util.strip(str(row['2'])),
		"description": util.strip(str(row['3'])),
		"category": util.strip(str(row["4"])),
		"tier": util.strip(sectionName)
	}

	return task
