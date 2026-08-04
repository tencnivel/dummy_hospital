--
-- PostgreSQL database dump
--

\restrict gvaEDEUFnKeHCuZdbGC6353hkj8tieJhub46FOoZQSiX278uw3rBOOMvmCplUUz

-- Dumped from database version 18.1 (Debian 18.1-1.pgdg13+2)
-- Dumped by pg_dump version 18.1 (Debian 18.1-1.pgdg13+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: gender_type; Type: TYPE; Schema: public; Owner: dummy_hospital
--

CREATE TYPE public.gender_type AS ENUM (
    'male',
    'female',
    'other',
    'unknown'
);


ALTER TYPE public.gender_type OWNER TO dummy_hospital;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: doctor; Type: TABLE; Schema: public; Owner: dummy_hospital
--

CREATE TABLE public.doctor (
    doctor_id integer NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    specialty character varying(100),
    license_number character varying(50),
    phone character varying(20),
    email character varying(100),
    unit_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.doctor OWNER TO dummy_hospital;

--
-- Name: doctor_doctor_id_seq; Type: SEQUENCE; Schema: public; Owner: dummy_hospital
--

CREATE SEQUENCE public.doctor_doctor_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.doctor_doctor_id_seq OWNER TO dummy_hospital;

--
-- Name: doctor_doctor_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dummy_hospital
--

ALTER SEQUENCE public.doctor_doctor_id_seq OWNED BY public.doctor.doctor_id;


--
-- Name: exam; Type: TABLE; Schema: public; Owner: dummy_hospital
--

CREATE TABLE public.exam (
    exam_id integer NOT NULL,
    patient_id integer NOT NULL,
    doctor_id integer,
    unit_id integer,
    exam_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    exam_type character varying(100),
    status character varying(50) DEFAULT 'pending'::character varying,
    notes text,
    result text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.exam OWNER TO dummy_hospital;

--
-- Name: exam_exam_id_seq; Type: SEQUENCE; Schema: public; Owner: dummy_hospital
--

CREATE SEQUENCE public.exam_exam_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.exam_exam_id_seq OWNER TO dummy_hospital;

--
-- Name: exam_exam_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dummy_hospital
--

ALTER SEQUENCE public.exam_exam_id_seq OWNED BY public.exam.exam_id;


--
-- Name: patient; Type: TABLE; Schema: public; Owner: dummy_hospital
--

CREATE TABLE public.patient (
    patient_id integer NOT NULL,
    first_name character varying(100),
    last_name character varying(100),
    date_of_birth date,
    gender public.gender_type,
    phone character varying(20),
    email character varying(100),
    address text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.patient OWNER TO dummy_hospital;

--
-- Name: patient_patient_id_seq; Type: SEQUENCE; Schema: public; Owner: dummy_hospital
--

CREATE SEQUENCE public.patient_patient_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.patient_patient_id_seq OWNER TO dummy_hospital;

--
-- Name: patient_patient_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dummy_hospital
--

ALTER SEQUENCE public.patient_patient_id_seq OWNED BY public.patient.patient_id;


--
-- Name: unit; Type: TABLE; Schema: public; Owner: dummy_hospital
--

CREATE TABLE public.unit (
    unit_id integer NOT NULL,
    unit_name character varying(100) NOT NULL,
    unit_code character varying(20),
    description text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.unit OWNER TO dummy_hospital;

--
-- Name: unit_unit_id_seq; Type: SEQUENCE; Schema: public; Owner: dummy_hospital
--

CREATE SEQUENCE public.unit_unit_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.unit_unit_id_seq OWNER TO dummy_hospital;

--
-- Name: unit_unit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dummy_hospital
--

ALTER SEQUENCE public.unit_unit_id_seq OWNED BY public.unit.unit_id;


--
-- Name: doctor doctor_id; Type: DEFAULT; Schema: public; Owner: dummy_hospital
--

ALTER TABLE ONLY public.doctor ALTER COLUMN doctor_id SET DEFAULT nextval('public.doctor_doctor_id_seq'::regclass);


--
-- Name: exam exam_id; Type: DEFAULT; Schema: public; Owner: dummy_hospital
--

ALTER TABLE ONLY public.exam ALTER COLUMN exam_id SET DEFAULT nextval('public.exam_exam_id_seq'::regclass);


--
-- Name: patient patient_id; Type: DEFAULT; Schema: public; Owner: dummy_hospital
--

ALTER TABLE ONLY public.patient ALTER COLUMN patient_id SET DEFAULT nextval('public.patient_patient_id_seq'::regclass);


--
-- Name: unit unit_id; Type: DEFAULT; Schema: public; Owner: dummy_hospital
--

ALTER TABLE ONLY public.unit ALTER COLUMN unit_id SET DEFAULT nextval('public.unit_unit_id_seq'::regclass);


--
-- Name: doctor doctor_license_number_key; Type: CONSTRAINT; Schema: public; Owner: dummy_hospital
--

ALTER TABLE ONLY public.doctor
    ADD CONSTRAINT doctor_license_number_key UNIQUE (license_number);


--
-- Name: doctor doctor_pkey; Type: CONSTRAINT; Schema: public; Owner: dummy_hospital
--

ALTER TABLE ONLY public.doctor
    ADD CONSTRAINT doctor_pkey PRIMARY KEY (doctor_id);


--
-- Name: exam exam_pkey; Type: CONSTRAINT; Schema: public; Owner: dummy_hospital
--

ALTER TABLE ONLY public.exam
    ADD CONSTRAINT exam_pkey PRIMARY KEY (exam_id);


--
-- Name: patient patient_pkey; Type: CONSTRAINT; Schema: public; Owner: dummy_hospital
--

ALTER TABLE ONLY public.patient
    ADD CONSTRAINT patient_pkey PRIMARY KEY (patient_id);


--
-- Name: unit unit_pkey; Type: CONSTRAINT; Schema: public; Owner: dummy_hospital
--

ALTER TABLE ONLY public.unit
    ADD CONSTRAINT unit_pkey PRIMARY KEY (unit_id);


--
-- Name: unit unit_unit_code_key; Type: CONSTRAINT; Schema: public; Owner: dummy_hospital
--

ALTER TABLE ONLY public.unit
    ADD CONSTRAINT unit_unit_code_key UNIQUE (unit_code);


--
-- Name: idx_doctor_last_name; Type: INDEX; Schema: public; Owner: dummy_hospital
--

CREATE INDEX idx_doctor_last_name ON public.doctor USING btree (last_name);


--
-- Name: idx_doctor_unit_id; Type: INDEX; Schema: public; Owner: dummy_hospital
--

CREATE INDEX idx_doctor_unit_id ON public.doctor USING btree (unit_id);


--
-- Name: idx_exam_date; Type: INDEX; Schema: public; Owner: dummy_hospital
--

CREATE INDEX idx_exam_date ON public.exam USING btree (exam_date);


--
-- Name: idx_exam_doctor_id; Type: INDEX; Schema: public; Owner: dummy_hospital
--

CREATE INDEX idx_exam_doctor_id ON public.exam USING btree (doctor_id);


--
-- Name: idx_exam_patient_id; Type: INDEX; Schema: public; Owner: dummy_hospital
--

CREATE INDEX idx_exam_patient_id ON public.exam USING btree (patient_id);


--
-- Name: idx_exam_unit_id; Type: INDEX; Schema: public; Owner: dummy_hospital
--

CREATE INDEX idx_exam_unit_id ON public.exam USING btree (unit_id);


--
-- Name: idx_patient_last_name; Type: INDEX; Schema: public; Owner: dummy_hospital
--

CREATE INDEX idx_patient_last_name ON public.patient USING btree (last_name);


--
-- Name: doctor doctor_unit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dummy_hospital
--

ALTER TABLE ONLY public.doctor
    ADD CONSTRAINT doctor_unit_id_fkey FOREIGN KEY (unit_id) REFERENCES public.unit(unit_id) ON DELETE SET NULL;


--
-- Name: exam exam_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dummy_hospital
--

ALTER TABLE ONLY public.exam
    ADD CONSTRAINT exam_doctor_id_fkey FOREIGN KEY (doctor_id) REFERENCES public.doctor(doctor_id) ON DELETE SET NULL;


--
-- Name: exam exam_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dummy_hospital
--

ALTER TABLE ONLY public.exam
    ADD CONSTRAINT exam_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patient(patient_id) ON DELETE CASCADE;


--
-- Name: exam exam_unit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dummy_hospital
--

ALTER TABLE ONLY public.exam
    ADD CONSTRAINT exam_unit_id_fkey FOREIGN KEY (unit_id) REFERENCES public.unit(unit_id) ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

\unrestrict gvaEDEUFnKeHCuZdbGC6353hkj8tieJhub46FOoZQSiX278uw3rBOOMvmCplUUz

