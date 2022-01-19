import traceback
import mwparserfromhell as mw
import api
import util
import league_utils
from typing import *


def run():
	tasks = []

	page = api.query_page("Twisted_League/Tasks")
	try:
		code = mw.parse(page, skip_style_tags=True)
		for section in code.get_sections():
			sectionName = section.get(0)
			for row in util.each_row("LeagueTaskRow", section):
				task = league_utils.convert_league_row_to_task(row, sectionName)
				tasks.append(task)

	except (KeyboardInterrupt, SystemExit):
		raise
	except:
		traceback.print_exc()

	skipSort = True
	util.write_list_json("out/league1_tasks.json", "out/league1_tasks.min.json", tasks, skipSort)