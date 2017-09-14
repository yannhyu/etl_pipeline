#!/usr/bin/python
# -*- coding: utf-8 -*-
import os.path
import sys
import fileinput
import time
import string
import csv
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table, Sequence
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.exc import DataError
from sqlalchemy.dialects.postgresql import \
    CHAR, VARCHAR, DATE, TIMESTAMP, INTEGER, BIGINT, NUMERIC
from rt_logger import make_a_logger
from transformer import db_truncate
# dir = os.path.dirname(__file__)
# lib_path = os.path.join(dir, '..', '..', 'lib/python/common')
# sys.path.append(lib_path)
# try:
    # from configs import CONN_STRING
#     from rt_logger import make_a_logger
# except ImportError:
#     sys.exit(1)    

CONN_STRING = 'postgresql://postgres:psql@localhost/etl_pipeline'
logger = make_a_logger('ins0_extractor')

def parse_command_line_args():
    """Parse args for our_run_date and cust_id."""
    if len(sys.argv) < 2:
        sys.stderr.write("Usage : python {} MMDDYY_HHMMSS_cust_id (for example 051317_000001_000015)\n"
            .format(sys.argv[0]))
        raise SystemExit(1)       
    mmddyy, hhmmss, raw_cust_id = sys.argv[1].split('_')
    our_run_date = datetime.strptime('{} {}'.format(mmddyy, hhmmss), '%m%d%y %H%M%S')
    param_cust_id = raw_cust_id.lstrip('0')
    return our_run_date, param_cust_id

def generate_headers(table_name):
    """Return the headers of any table by table name."""
    ex_table = metadata.tables[table_name]
    return [column.name for column in ex_table.columns]

def db_ready_data_lines(versioned_headers):
    """Produce db ready data rows."""
    for line in fileinput.input(sys.argv[2:]):
        line_cleaned = ''.join(s for s in line if s in string.printable)
        items = line_cleaned.strip().split('|')
        items_with_none = [i or None for i in items]    # Experimental
        items_with_none = [i.strip() if i else i for i in items_with_none]
        data_line = dict(zip(versioned_headers, items_with_none))
        acctnum = data_line.get('acctnum')
        hid = data_line.get('hid')
        cpi = data_line.get('cpi')
        fail_reason = None
        # When count of delimiters and data item count do not match right
        # delimiters_count + 1 is expected to equal to items_count
        if len(versioned_headers) != line.count('|') + 1:
            fail_reason = 'DL'
        elif acctnum is None or len(acctnum) > 20:
            fail_reason = 'AC'
        elif hid and len(hid) > 6:
            fail_reason = 'HD'
        elif cpi and len(cpi) > 15:
            fail_reason = 'CP'

        unstaged_headers = tuple(generate_headers('unstaged_t'))
        res = {k:data_line[k] for k in unstaged_headers if k in data_line}
        # fill missed attr
        res['dataload'] = data_line
        res['id_rec'] = None
        res['seqnum'] = fileinput.lineno()
        res['fail_reason'] = fail_reason

        yield res

def cust_id_match(expected_cust_id):
    """Signal if cust_id from data row is the same as expected."""
    while True:
        dl = (yield)
        yield dl['cust_id'].lstrip('0') == expected_cust_id

def get_mapping():
    """Retrieve cust_id to ins0 version mapping."""
    result = {}
    with open('cust_version_mapping.csv', 'r') as fh:
        result = {rows[0]:rows[1] for rows in csv.reader(fh)}
    return result

def version(cust_id):
    # TODO: replace it with reading from DB tbl
    mapping = get_mapping()
    default = 'v4_invoice'
    if cust_id > str('5000'):
        default = 'v6'
    return mapping.get(cust_id, default)


if __name__ == '__main__':
    overall_start_time = time.time()
    db_truncate('unstaged_t')
    our_run_date, param_cust_id = parse_command_line_args()
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
    Base = automap_base(metadata=metadata)
    Base.prepare(engine, reflect=False)
    Unstaged = Base.classes.unstaged_t

    desired_version = version(param_cust_id)
    desired_headers = tuple(generate_headers('read_insurance0_{}_t'.format(desired_version)))
    
    data_lines = db_ready_data_lines(desired_headers)

    session = Session(engine)
    irregulars_count = 0
    for count, dl in enumerate(data_lines, 1):
        # check param_cust_id with cust_id from input, 
        # if not match, raise ERROR
        check_cust_id_match = cust_id_match(param_cust_id)
        next(check_cust_id_match)
        if not check_cust_id_match.send(dl):
            session.rollback()
            logger.error('Error: cust_id mismatch found...')
            raise RuntimeError('Error: cust_id mismatch found...')

        dl['our_run_date'] = our_run_date
        session.add(Unstaged(**dl))

        if count % 1234 == 0:
            try:
                session.commit()
            except DataError as exc:
                session.rollback()
                reason = exc.message
                logger.error('Data Error: {}'.format(reason))
    else:
        try:
            session.commit()
        except DataError as exc:
            session.rollback()
            reason = exc.message
            logger.error('Data Error: {}'.format(reason))

    logger.info("Overall: --- {} seconds ---".format(time.time() - overall_start_time))