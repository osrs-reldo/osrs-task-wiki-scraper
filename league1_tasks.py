import traceback
import re
import mwparserfromhell as mw
import api
import util
from typing import *


def run():
	tasks = []

	page = api.query_page("Twisted_League/Tasks")
	try:
		code = mw.parse(page, skip_style_tags=True)
		for section in code.get_sections():
			sectionName = section.get(0)
			for row in util.each_row("LeagueTaskRow", section):
				skills = []
				if row["s"] is not None:
					skillCode = mw.parse(row["s"], skip_style_tags=True)
					for skillPart in skillCode.filter_templates(matches=lambda t: t.name.matches("SCP")):
						skills.append({
							"skill": util.strip(str(skillPart.params[0])),
							"level": util.strip(str(skillPart.params[1]))
						})
				task = {
					"name": util.strip(str(row['1'])),
					"description": util.strip(str(row['2'])),
					"skills": skills,
					"other": util.strip(str(row["other"])) if "other" in row else "",
					"tier": util.strip(sectionName)
				}
				tasks.append(task)

	except (KeyboardInterrupt, SystemExit):
		raise
	except:
		traceback.print_exc()

	skipSort = True
	util.write_list_json("league1_tasks.json", "league1_tasks.min.json", tasks, skipSort)