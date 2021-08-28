import mwparserfromhell as mw
import util

def convert_league_row_to_task(row, sectionName: str):
	skills = []
	if 's' in row and row["s"] is not None:
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

	return task