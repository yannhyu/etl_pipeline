-- Table: temp_batch_insurance0_unstaged_t

-- DROP TABLE temp_batch_insurance0_unstaged_t;

CREATE TABLE temp_batch_insurance0_unstaged_t
(
  id_rec bigint,
  id_acct bigint,
  id_pat bigint,
  cust_id numeric(4,0) NOT NULL,
  treatment_code character varying(6) NOT NULL,
  our_run_date timestamp without time zone NOT NULL,
  seqnum integer NOT NULL,
  cpi character varying(15),
  acctnum character varying(20) NOT NULL,
  acctnum_seq integer NOT NULL,
  hid character varying(6) NOT NULL,
  individual_matchkey character varying(102),
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
  client_npi2 character varying(10),
  npi2 character varying(12),
  tax_id2 character varying(12),
  legacy2 character varying(14),
  pin2 character varying(10),
  entity_name2 character varying(50),
  entity_pay_to_street2 character varying(50),
  entity_pay_to_city2 character varying(30),
  entity_pay_to_state2 character varying(2),
  entity_pay_to_zip2 character varying(10),
  entity_information2 character varying(50),
  entity_phone2 character varying(14),
  name_type character varying(2),
  lname character varying(30),
  mname character varying(1),
  fname character varying(30),
  addr1 character varying(50),
  addr2 character varying(50),
  city character varying(30),
  state character varying(2),
  zip5 character varying(5),
  zip4 character varying(4),
  ssn character varying(9),
  gender character varying(1),
  dob date,
  phone1 character varying(11),
  phone2 character varying(11),
  g_lname character varying(30),
  g_mname character varying(1),
  g_fname character varying(30),
  g_addr1 character varying(50),
  g_addr2 character varying(50),
  g_city character varying(30),
  g_state character varying(2),
  g_zip5 character varying(5),
  g_zip4 character varying(4),
  g_ssn character varying(9),
  g_gender character varying(1),
  g_dob date,
  relationship_flag character varying(3),
  g_employ_name character varying(35),
  provider_state character varying(2),
  service_date_begin date,
  service_date_end date,
  pat_proc_type character varying(3),
  pat_type character varying(25),
  fin_class character varying(8),
  payor_plan1 character varying(120),
  payor_plan2 character varying(120),
  medlytix_class character varying(2),
  cpt character varying(12),
  drg character varying(12),
  diag1 character varying(8),
  diag2 character varying(8),
  charges numeric(20,2),
  balance numeric(20,2),
  acct_status character varying(15),
  obs_ind character varying(1),
  medicaid_max_date date,
  medicare_max_date date,
  third_party_sent_date date,
  hippa_flag_com character varying(1),
  hippa_flag_mcaid character varying(1),
  hippa_flag_mcare character varying(1),
  processing_ssn_flag character varying(1),
  emdeon_sent_date timestamp without time zone,
  emdeon_tpl_flag character varying(1),
  emdeon_commercial_flag character varying(1),
  emdeon_medicare_flag character varying(1),
  emdeon_medicaid_flag character varying(1),
  emdeon_medicare_fast character varying(1),
  com_percent integer,
  tpl_percent integer,
  mcaid_percent integer,
  mcare_percent integer,
  com_bal_override numeric(6,0),
  tpl_bal_override numeric(6,0),
  mcaid_bal_override numeric(6,0),
  mcare_bal_override numeric(6,0),
  minimum_charges numeric(6,0),
  minimum_balance numeric(6,0),
  com_day_toscrub integer,
  tpl_day_toscrub integer,
  mcaid_day_toscrub integer,
  mcare_day_toscrub integer,
  com_i_day_toscrub integer,
  tpl_i_day_toscrub integer,
  mcaid_i_day_toscrub integer,
  mcare_i_day_toscrub integer,
  com_day_timely integer,
  output_id integer NOT NULL,
  invoice_id character varying(8),
  invoice_sub_id character varying(8),
  emdeon_billing_id character varying(6) NOT NULL,
  payor_plan_key character varying(8),
  prior_commercial_run character varying(1),
  prior_tpl_run character varying(1),
  prior_medicaid_run character varying(1),
  prior_medicare_run character varying(1),
  current_commercial_run character varying(1),
  current_tpl_run character varying(1),
  current_medicaid_run character varying(1),
  current_medicare_run character varying(1),
  calc_group character varying(15),
  processing_type character varying(1),
  out_of_state character varying(1),
  commercial_score numeric(10,6),
  scoring_code_commercial character varying(3),
  tpl_score numeric(10,6),
  scoring_code_tpl character varying(3),
  medicaid_score numeric(10,6),
  scoring_code_medicaid character varying(3),
  medicare_score numeric(10,6),
  scoring_code_medicare character varying(3),
  client_field1 character varying(30),
  client_field2 character varying(30),
  client_field3 character varying(30),
  client_date1 date,
  processing_dob_flag character varying(1),
  dob_corrected date,
  cust_carrier_code character varying(10),
  cust_carrier_type character varying(1),
  cust_subscriber_id character varying(20),
  record_npi character varying(10),
  ebureau_sent_flag character varying(1),
  ebureau_ssn character varying(9),
  ebureau_ssn_miskey character varying(1),
  drop_payer character varying(1),
  drop_prior_search character varying(1),
  drop_charges character varying(1),
  drop_balance character varying(1),
  drop_demographics character varying(3),
  drop_customer character varying(3),
  drop_exclude character varying(1),
  drop_date character varying(4),
  new_account character varying(1),
  hash_ssn_match integer,
  hash_addr_match integer,
  hash_ssn character varying(32),
  hash_addr character varying(32),
  CONSTRAINT temp_batch_insurance0_unstaged_t_pkey PRIMARY KEY (seqnum),
  CONSTRAINT temp_batch_insurance0_unstaged_t_cust_id_check CHECK (cust_id >= 1::numeric AND cust_id <= 9999::numeric)
)
WITH (
  OIDS=FALSE
);