#!/usr/bin/python
import random
import fileinput
from sqlalchemy import create_engine
from sqlalchemy import MetaData
'''
type .\input_data\042617_190042_005064_insacct_wins.txt | python .\input_data\step_00_read_inputfile.py
'''
CONN_STRING = 'postgresql://postgres:psql@localhost/etl_pipeline'

def generate_headers(table_name):
    """Return the headers of any table by table name."""
    ex_table = metadata.tables[table_name]
    return [column.name for column in ex_table.columns]

def clean(data_dict):
    my_ssn = random.randint(100000000, 999999999)
    my_g_ssn = random.randint(100000000, 999999999)
    data_dict['ssn'] = str(my_ssn)
    data_dict['g_ssn'] = str(my_g_ssn)
    return data_dict

if __name__ == '__main__':
    engine = create_engine(CONN_STRING)
    metadata = MetaData(engine)
    metadata.reflect(engine,
                     only=[
                         'unstaged_t',
                         'read_insurance0_v1_t',
                         'read_insurance0_v2_invoice_t',
                         'read_insurance0_v2_t',
                         'read_insurance0_v3_invoice_t',
                         'read_insurance0_v3_t',
                         'read_insurance0_v4_invoice_t',
                         'read_insurance0_v4_t',
                         'read_insurance0_v5_t',
                         'read_insurance0_v6_t',
                    ])
    headers = generate_headers('read_insurance0_v1_t')

    for line in fileinput.input():
        line = line.strip('\n').strip('\r').split('|')
        dict_line = dict(zip(headers, line))
        # print(dict_line)
        dict_line = clean(dict_line)
        print('|'.join([dict_line.get(k) for k in headers]))

