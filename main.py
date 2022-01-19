import util
import api

import combat_tasks
import league1_tasks
import league2_tasks
import league3_tasks

util.create_dir_if_not_exists('out')
util.create_dir_if_not_exists('out/min')

# combat_tasks.run()
# league1_tasks.run()
# league2_tasks.run()
league3_tasks.run()
