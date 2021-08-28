import traceback
import re
import mwparserfromhell as mw
import api
import util
from typing import *


def run():
	tasks = []

	achievement_pages = api.query_category("Combat_Achievements")
	for name, page in achievement_pages.items():
		if name.startswith("Category:") or name.startswith("Combat Achievements"):
			continue

		try:
			code = mw.parse(page, skip_style_tags=True)

			for (vid, version) in util.each_version("Infobox Task", code):
				task = {
					"name": util.strip(str(version["name"])),
					"description": util.strip(str(version["task"])),
					"area": util.strip(str(version["area"])),
					"tier": util.strip(str(version["tier"])),
				}
				tasks.append(task)

		except (KeyboardInterrupt, SystemExit):
			raise
		except:
			print("Task {} failed:".format(name))
			traceback.print_exc()

	skipSort = True
	util.write_list_json("combat_tasks.json", "combat_tasks.min.json", tasks, skipSort)
