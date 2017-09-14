import time
import contextlib
import json
import psycopg2.extras
from re import sub
from decimal import Decimal
from datetime import datetime
from functools import partial
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.exc import DataError
from sqlalchemy.dialects.postgresql import \
    CHAR, VARCHAR, DATE, TIMESTAMP, INTEGER, BIGINT, NUMERIC
from coroutine import coroutine
from dateutil.parser import parse

# TODO: The following tools will be moved into
# generalized lib module framework later
def normalize(money):
    result = money
    if money:
        result = Decimal(sub(r'[^\d.]', '', money))
        if '(' in money and ')' in money:
            result = -result
    return result

def is_invalid_date(string):
    try: 
        parse(string)
        return False
    except ValueError:
        return True

def ssn_cleanup(ssn):
    if ssn and '-' in ssn:
        ssn = ssn.replace('-', '')
    return ssn


# import psycopg2.extras
# psycopg2.extras.register_json(oid=3802, array_oid=3807, globally=True)

# DB_URI = 'postgresql://dev_payorintel_u:u782nmt5@devmaindb/dev_ml_db'
DB_URI = 'postgresql://postgres:psql@localhost/etl_pipeline'
# engine = create_engine(DB_URI, echo=True)
engine = create_engine(DB_URI, echo=False)
TARGET_TBL_NAME = 'temp_batch_insurance0_unstaged_t'
metadata = MetaData(engine)
metadata.reflect(engine, only=[TARGET_TBL_NAME,
                               'read_insurance0_v1_t',
                               'read_insurance0_v2_t',
                               'read_insurance0_v2_invoice_t',
                               'read_insurance0_v3_t',
                               'read_insurance0_v3_invoice_t',
                               'read_insurance0_v4_t',
                               'read_insurance0_v4_invoice_t',
                               'read_insurance0_v5_t',
                               'read_insurance0_v6_t',    
                               'unstaged_t',])
target_tbl = metadata.tables[TARGET_TBL_NAME]
TRUNCATION_WHITELIST = ['acctnum', 'hid', 'cpi']

def db_truncate(tbl_name):
    with contextlib.closing(engine.connect()) as con:
        trans = con.begin()
        con.execute('TRUNCATE {} RESTART IDENTITY;'.format(tbl_name))
        trans.commit()

def db_schema_sanity_check():
    result = []
    target_tbl = metadata.tables['temp_batch_insurance0_unstaged_t']
    target_tbl_cols_names = [column.name for column in target_tbl.columns]
    bigger = set(target_tbl_cols_names)
    version_tbls = ('read_insurance0_v1_t',
                    'read_insurance0_v2_t',
                    'read_insurance0_v2_invoice_t',
                    'read_insurance0_v3_t',
                    'read_insurance0_v3_invoice_t',
                    'read_insurance0_v4_t',
                    'read_insurance0_v4_invoice_t',
                    'read_insurance0_v5_t',
                    'read_insurance0_v6_t',)
    for version_tbl in version_tbls:
        v_tbl = metadata.tables[version_tbl]
        v_tbl_cols = [column.name for column in v_tbl.columns]
        result.extend(set(v_tbl_cols) - bigger)

    return list(set(result))

def transform(rows, target):
    for row in rows:
        # print('id_rec:{} -- cust_id:{} -- our_run_date:{} -- fail_reason:{}'
        #     .format(row.id_rec, row.cust_id, row.our_run_date, row.fail_reason))
        dl = row['dataload']
        # Only apply to DBAPI (psycopg2 version is < 2.5.4)
        if isinstance(dl, str):
            dl = json.loads(dl)
        dl['cust_id'] = row['cust_id']
        dl['our_run_date'] = row['our_run_date']
        dl['seqnum'] = row['seqnum']
        # TODO: ask about the following fields
        dl['acctnum_seq'] = row['seqnum']
        # when ssn is hyphenated '429-27-0800', truncation works
        # yet it cuts off last two digits: work around is to 
        # remove any hyphens
        dl['ssn'] = ssn_cleanup(dl.get('ssn'))
        # the same goes with g_ssn
        dl['g_ssn'] = ssn_cleanup(dl.get('g_ssn'))

        target.send(dl)

# to fix DataError regarding date with PostgreSQL
# invalid input syntax for type numeric: "";
# invalid input syntax for type date: "";
# date/time field value out of range: "00/00/0000";
# TypeError: u'tot_pat_pmt' is an invalid
# keyword argument for temp_batch_insurance0_unstaged
# invalid input syntax for type numeric: "2,475.41"
def curate(dl):
    for column in target_tbl.columns:
        if isinstance(column.type, NUMERIC):
            numeric_str = dl.get(column.name)
            if not numeric_str:
                dl[column.name] = None
            # Currency fld
            if column.type.precision == 20 and column.type.scale == 2:
                dl[column.name] = normalize(numeric_str)
        if isinstance(column.type, DATE):
            date_str = dl.get(column.name)
            if not date_str:
                dl[column.name] = None
            elif is_invalid_date(date_str):
                    dl[column.name] = None


    # work around the invalid keyword argument problem with db
    db_schema_blacklist = db_schema_sanity_check()
    if db_schema_blacklist:
        dl = {k:dl[k] for k in dl if k not in db_schema_blacklist}
    # avoid storing None as value in db
    dl = {k:dl[k] for k in dl if dl[k] and dl[k] != 'None'}
    # sqlalchemy.exc.IntegrityError: 
    # (psycopg2.IntegrityError) null value in column "client_npi1" 
    # violates not-null constraint 
    dl['client_npi1'] = ''
    dl['emdeon_billing_id'] = ''

    return dl

# A sink.  A coroutine that receives data & persists to db
@coroutine
def store2db(session):
    Base = automap_base(metadata=metadata)
    Base.prepare(engine, reflect=False)
    TempBatchIns0Unstaged = Base.classes.temp_batch_insurance0_unstaged_t
    # session = Session(engine)
    try:
        while True:
            dl = (yield)
            # print('{} {} {}'.format(dl.get('fname'), dl.get('mname'), dl.get('lname')))
            # print(dl)
            # to fix DataError regarding date with PostgreSQL
            dl = curate(dl)
            session.add(TempBatchIns0Unstaged(**dl))
            # print('----- added one row to session ----')

            # except Exception as inst:
            #    session.rollback()
            #    print(inst.statement % inst.params)
        
    except GeneratorExit:
        # print('----- before commit ----')
        try:
            session.commit()
            # print('----- after commit ----')          
        except DataError as derr:
            session.rollback()
            reason = derr.message
            print('Data Error: {}'.format(reason))
            # orig = derr.orig
            # print('Error orig: {}'.format(orig))
            # statement = derr.statement
            # print('Error statement: {}'.format(statement))
            # params = derr.params
            # print('Error params: {}'.format(params))                
        else:       
            print('----- Data batch inserted into DB -----')

    finally:
        print('******** la fin ********')                

        # truncate db source table
        # db_truncate('unstaged_t')                  

# convenient methods
def fixed_size_str(somestring, maxlength):
    return str(somestring)[:maxlength]

def generate_truncation_map():
    fld_map = dict()
    for column in target_tbl.columns:
        if isinstance(column.type, VARCHAR):
            fld_map[column.name] = partial(fixed_size_str, maxlength=column.type.length)
        else:
            fld_map[column.name] = None
    return fld_map

def trucation_exclusion(truncation_map, keys2exclude):
    for k in keys2exclude:
        truncation_map[k] = None
    return truncation_map    

@coroutine
def truncate(trunc, target):
    while True:
        dl = (yield)
        # dl_truncated = {k:(trunc[k](v) if trunc.get(k) else v) for k, v in dl.iteritems()}
        # target.send(dl_truncated)
        for k in trunc:
            if trunc.get(k) and k in dl:
                dl[k] = trunc[k](dl[k])
        target.send(dl)

def ResultIter(cursor, arraysize=7789):
    'An iterator using fetchmany to keep memory usage down'
    while True:
        results = cursor.fetchmany(arraysize)
        if not results:
            break
        yield results

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session(engine)
    try:
        yield session
    except:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == '__main__':
    overall_start_time = time.time()
    # truncate target table for new operation
    db_truncate('temp_batch_insurance0_unstaged_t')

    truncation_map = generate_truncation_map()
    truncation_map_adjusted = trucation_exclusion(truncation_map, 
                                                  TRUNCATION_WHITELIST)
    conn = engine.raw_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        number_of_rows = cursor.execute('select * from unstaged_t')
        # print('*** Total number of rows {}'.format(number_of_rows))
        with session_scope() as session:
            for results in ResultIter(cursor):
                transform(results,
                          truncate(truncation_map_adjusted,
                          store2db(session)))

        cursor.close()
    finally:
        conn.close() 


    print("Overall: --- {} seconds ---".format(time.time() - overall_start_time))