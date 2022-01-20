import traceback
import mwparserfromhell as mw
import api
import util
import league_utils
from typing import *


def run():
	tasks = []

	achievement_pages = api.query_category("Shattered_Relics_League")
	for name, page in achievement_pages.items():
		if not name.startswith("Shattered Relics League/Tasks/"):
			continue

		category = name.replace("Shattered Relics League/Tasks/", "")
		try:
			code = mw.parse(page, skip_style_tags=True)
			sections = code.get_sections(levels=[1,2,3])
			for section in sections:
				sectionName = section.get(0)
				for row in util.each_row("SRLTaskRow", section):
					task = league_utils.convert_league_row_to_task(row, sectionName)
					task["category"] = category
					task["id"] = int(row["id"]) if "id" in row and row["id"] != "" else -1
					tasks.append(task)

		except (KeyboardInterrupt, SystemExit):
			raise
		except:
			traceback.print_exc()

	skipSort = True
	util.write_list_json("out/league3_tasks.json", "out/min/league3_tasks.min.json", tasks, skipSort)