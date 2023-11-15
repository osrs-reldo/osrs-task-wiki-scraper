import mwparserfromhell as mw
import util

def convert_league_row_to_task(row, sectionName: str):
	skills = []
	if 's' in row and row["s"] is not None:
		skillCode = mw.parse(row["s"], skip_style_tags=True)
		for skillPart in skillCode.filter_templates(matches=lambda t: t.name.matches("SCP")):
			if (len(skillPart.params) > 1):
				skills.append({
					"skill": util.strip(str(skillPart.params[0])),
					"level": util.strip(str(skillPart.params[1]))
				})
	task = {
		"name": util.strip(str(row['1'])),
		"description": util.strip(str(row.get('2'))),
		"skills": skills,
		"other": util.strip(str(row["other"])) if "other" in row else "",
		"tier": util.strip(sectionName)
	}

	return task

# use this one for leagues 4 and newer
def convert_league_row_to_task_new(row):
	skills = []
	if 's' in row and row["s"] is not None:
		skillCode = mw.parse(row["s"], skip_style_tags=True)
		for skillPart in skillCode.filter_templates(matches=lambda t: t.name.matches("SCP")):
			if (len(skillPart.params) > 1):
				skills.append({
					"skill": util.strip(str(skillPart.params[0])),
					"level": util.strip(str(skillPart.params[1]))
				})
	task = {
		"id": util.strip(str(row["id"])),
		"name": util.strip(str(row['1'])),
		"description": util.strip(str(row.get('2'))),
		"skills": skills,
		"other": util.strip(str(row["other"])) if "other" in row else "",
		"tier": util.strip(str(row["tier"])),
		"area": util.strip(str(row["region"]))
	}

	return task