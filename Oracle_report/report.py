import os
import time
import openpyxl
import xlswriter
import cx_Oracle
import pandas as pd
import numpy as np
from sqlalchemy import engine


DIALECT = 'oracle'
SQL_DRIVER = 'cx_Oracle'
USERNAME = 'XYZ'
PASSWORD = 'ABC123@'
HOST_1 = 'whatever.database.andever.com'
HOST_2 = 'whatever.database.andever.com'
SERVICE_1 = 'something'
SERVICE_2 = 'somethingelse'
ENGINE_PATH_WITH_AUTH_PCO = DIALECT + '+' + SQL_DRIVER + '://' + USERNAME + ':' + \
        PASSWORD + '@' + HOST_1 + ':' + \
        str(PORT) + '/?service_name=' + SERVICE_1
engine_123 = 'adjkahsiahfahsoashfoahfasfpafs'

engine_db = create_engine(ENGINE_PATH_WITH_AUTH_1)


time = time.strftime("%Y%m%d")
file_name = ("PC_" + time + ".xlsx")

file_path = "./"+ file_name

sql_rep_1st = pd.read_sql(
    """ SELECT /* parallel*/
    *
    FROM
    ***
    WHERE
    *********
    """.format(), engine_db)

sql_rep_2nd = pd.read_sql(
    """ SELECT /* parallel*/
    *
    FROM
    ***
    WHERE
    *********
    """.format(), engine_db)

final_rep = sql_rep_1st.merge(sql_rep_2nd, how = 'left',
                              left_on = 'column_from_db1', right_on = 'column_from_db2')

final_rep['Column1name'] = final_rep['Column1name'].astype(np.float32) / final_rep['Column1name'].astype(np.float32) -1

final_rep.loc[:, 'columnx'] = final_rep['columnx'].map('{:,2%}'.format)

wb = openpyxl.Workbook()
wb.save(file_path)

with pd.ExcelWriter(file_path, mode = 'a', engine = 'openpyxl', if_sheet_exist = 'replace') as writer:
    final_rep.to_excel(writer, index = False, sheet_name ="Compare", startcol = 0)

wb.close()