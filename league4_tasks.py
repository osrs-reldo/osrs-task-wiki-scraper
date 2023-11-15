import traceback
import mwparserfromhell as mw
import api
import util
import league_utils
from typing import *

regionNameMapping = {
	'Asgarnia': 'Asgarnia',
	'Fremennik Provinces': 'Fremennik',
	'General': 'Any',
	'Kandarin': 'Kandarin',
	'Karamja': 'Karamja',
	'Kharidian Desert': 'Desert',
	'Kourend': 'Kourend',
	'Misthalin': 'Misthalin',
	'Morytania': 'Morytania',
	'Tirannwn': 'Tirannwn',
	'Wilderness': 'Wilderness'
}

def run():
	tasks = []

	page = api.query_page("Trailblazer Reloaded League/Tasks")
	try:
		code = mw.parse(page, skip_style_tags=True)
		for row in util.each_row("TRLTaskRow", code):
			task = league_utils.convert_league_row_to_task_new(row)
			tasks.append(task)

	except (KeyboardInterrupt, SystemExit):
		raise
	except:
		traceback.print_exc()

	skipSort = True
	util.write_list_json("league4_tasks.json", "league4_tasks.min.json", tasks, skipSort)