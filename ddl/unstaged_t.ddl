-- Table: unstaged_t

-- DROP TABLE unstaged_t;

CREATE TABLE unstaged_t
(
  id_rec bigint NOT NULL DEFAULT nextval('insurance0_all_t_id_rec_seq'::regclass),
  cust_id numeric(4,0) NOT NULL,
  our_run_date timestamp without time zone NOT NULL,
  seqnum integer,
  fail_reason character varying(2),
  dataload jsonb,
  CONSTRAINT unstaged_t_pkey PRIMARY KEY (id_rec),
  --CONSTRAINT cust_id_exists FOREIGN KEY (cust_id)
  --    REFERENCES ml_custid_t (cust_id) MATCH SIMPLE
  --    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT unstaged_t_cust_id_check CHECK (cust_id >= 1::numeric AND cust_id <= 9999::numeric)
)
WITH (
  OIDS=FALSE
);