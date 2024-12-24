# Jmvs_tool_box

'''
import importlib
from Jmvs_tool_box import main

importlib.reload(main)
main.run_tool_box()
'''

Got the json's to work,
made json's data feed into database's
>> if the database gets :
    `cr_database("bipedArm", "_R", u_s_dict)` unique_id == 1 NOT == 1
    `cr_database("bipedArm", "_L", u_s_dict)` unique_id == 1 NOT == 2
    `cr_database("bipedArm", "_R", u_s_dict)` unique_id == 2 NOT == 3
    `cr_database("bipedArm", "_L", u_s_dict)` unique_id == 2 NOT == 4
> need to make the unique_id from database_schema work: #NameError: name 'unique_id' is not defined
