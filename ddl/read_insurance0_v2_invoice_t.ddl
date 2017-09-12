-- Table: read_insurance0_v2_invoice_t

-- DROP TABLE read_insurance0_v2_invoice_t;

CREATE TABLE read_insurance0_v2_invoice_t
(
  cust_id numeric(4,0) NOT NULL,
  treatment_code character varying(6) NOT NULL,
  output_id integer NOT NULL,
  invoice_id character varying(8),
  invoice_sub_id character varying(8),
  hid character varying(6) NOT NULL,
  acctnum character varying(20) NOT NULL,
  cpi character varying(15),
  client_npi1 character varying(10) NOT NULL,
  npi1 character varying(12),
  tax_id1 character varying(12),
  legacy1 character varying(14),
  pin1 character varying(10),
  entity_name1 character varying(50),
  entity_pay_to_street1 character varying(50),
  entity_pay_to_city1 character varying(30),
  entity_pay_to_state1 character varying(2),
  entity_pay_to_zip1 character varying(10),
  entity_information1 character varying(50),
  entity_phone1 character varying(14),
  lname character varying(30),
  mname character varying(1),
  fname character varying(30),
  addr1 character varying(50),
  addr2 character varying(50),
  city character varying(30),
  state character varying(2),
  zip5 character varying(5),
  zip4 character varying(4),
  ssn character varying(11),
  gender character varying(1),
  dob date,
  g_lname character varying(30),
  g_mname character varying(1),
  g_fname character varying(30),
  g_addr1 character varying(50),
  g_addr2 character varying(50),
  g_city character varying(30),
  g_state character varying(2),
  g_zip5 character varying(5),
  g_zip4 character varying(4),
  g_ssn character varying(11),
  g_gender character varying(1),
  g_dob date,
  relationship_flag character varying(3),
  g_employ_name character varying(35),
  provider_state character varying(2),
  service_date_begin date,
  service_date_end date,
  pat_proc_type character varying(3),
  pat_type character varying(25),
  cpt character varying(12),
  drg character varying(12),
  diag1 character varying(8),
  charges numeric(20,2),
  balance numeric(20,2),
  acct_status character varying(15),
  client_field1 character varying(30),
  client_field2 character varying(30),
  client_field3 character varying(30),
  client_date1 date,
  CONSTRAINT read_insurance0_v2_invoice_t_cust_id_check CHECK (cust_id >= 1::numeric AND cust_id <= 9999::numeric)
)
WITH (
  OIDS=FALSE
);
