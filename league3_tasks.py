import traceback
import mwparserfromhell as mw
import api
import util
import league_utils
from typing import *


def run():
	tasks = []

	page = api.query_page("Shattered_Relics_League/Tasks")
	try:
		code = mw.parse(page, skip_style_tags=True)
		for section in code.get_sections():
			typeName = section.get(0)
			if not hasattr(section.get(2), 'contents'):
				continue
			typePageName = util.strip(section.get(2).contents)
			typePage = api.query_page(typePageName)
			typePageCode = mw.parse(typePage, skip_style_tags=True)
			sectionName = typePageCode.get(0)
			for row in util.each_row("LeagueTaskRow", typePageCode):
				task = league_utils.convert_league_row_to_task(row, sectionName)
				tasks.append(task)

	except (KeyboardInterrupt, SystemExit):
		raise
	except:
		traceback.print_exc()

	skipSort = True
	util.write_list_json("out/league3_tasks.json", "out/min/league3_tasks.min.json", tasks, skipSort)