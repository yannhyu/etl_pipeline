#!/usr/bin/python
import random
import fileinput
from sqlalchemy import create_engine
from sqlalchemy import MetaData
'''
type .\input_data\042617_190042_005064_insacct_wins.txt | python .\input_data\step_00_read_inputfile.py

type .\input_data\before\071417_075003_000152_insacct_wins.txt | python .\input_data\step_01_read_inputfile_scramble.py > .\input_data\071417_075003_000152_insacct_wins_clean.txt
'''
CONN_STRING = 'postgresql://postgres:psql@localhost/etl_pipeline'

def generate_headers(table_name):
    """Return the headers of any table by table name."""
    ex_table = metadata.tables[table_name]
    return [column.name for column in ex_table.columns]

def clean(data_dict):
    ssn = data_dict.get('ssn')
    g_ssn = data_dict.get('g_ssn')
    ssn = ssn.replace('-', '')
    g_ssn = g_ssn.replace('-', '')
    data_dict['ssn'] = ''.join(random.sample(ssn, len(ssn)))
    data_dict['g_ssn'] = ''.join(random.sample(g_ssn, len(g_ssn)))
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
    headers = generate_headers('read_insurance0_v4_t')

    for line in fileinput.input():
        line = line.strip('\n').strip('\r').split('|')
        dict_line = dict(zip(headers, line))
        # print(dict_line)
        dict_line = clean(dict_line)
        print('|'.join([dict_line.get(k, '') for k in headers]))

