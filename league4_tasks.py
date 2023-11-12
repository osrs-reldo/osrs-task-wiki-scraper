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

	achievement_pages = api.query_category("Trailblazer_Reloaded_League")
	for name, page in achievement_pages.items():
		if not name.startswith("Trailblazer Reloaded League/Tasks/"):
			continue

		area = regionNameMapping.get(name.replace("Trailblazer Reloaded League/Tasks/", ""))
		if not area:
			continue

		try:
			code = mw.parse(page, skip_style_tags=True)
			sections = code.get_sections(levels=[1,2,3])
			for section in sections:
				sectionName = section.get(0)
				for row in util.each_row("LeagueTaskRow", section):
					task = league_utils.convert_league_row_to_task(row, sectionName)
					task["area"] = area
					tasks.append(task)

		except (KeyboardInterrupt, SystemExit):
			raise
		except:
			traceback.print_exc()

	skipSort = True
	util.write_list_json("league4_tasks.json", "league4_tasks.min.json", tasks, skipSort)