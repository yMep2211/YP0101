-- PostgreSQL database dump

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
-- TOC entry 15 (class 2615 OID 26040)
-- Name: partner_module; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA partner_module;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 303 (class 1259 OID 26104)
-- Name: material_types; Type: TABLE; Schema: partner_module; Owner: -
--

CREATE TABLE partner_module.material_types (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    defect_percent numeric(6,4) NOT NULL,
    CONSTRAINT material_types_defect_percent_check CHECK ((defect_percent >= (0)::numeric))
);


--
-- TOC entry 302 (class 1259 OID 26103)
-- Name: material_types_id_seq; Type: SEQUENCE; Schema: partner_module; Owner: -
--

CREATE SEQUENCE partner_module.material_types_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5137 (class 0 OID 0)
-- Dependencies: 302
-- Name: material_types_id_seq; Type: SEQUENCE OWNED BY; Schema: partner_module; Owner: -
--

ALTER SEQUENCE partner_module.material_types_id_seq OWNED BY partner_module.material_types.id;


--
-- TOC entry 297 (class 1259 OID 26068)
-- Name: partner_contacts; Type: TABLE; Schema: partner_module; Owner: -
--

CREATE TABLE partner_module.partner_contacts (
    id bigint NOT NULL,
    partner_id bigint NOT NULL,
    email character varying(255) NOT NULL,
    phone character varying(50) NOT NULL
);


--
-- TOC entry 296 (class 1259 OID 26067)
-- Name: partner_contacts_id_seq; Type: SEQUENCE; Schema: partner_module; Owner: -
--

CREATE SEQUENCE partner_module.partner_contacts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5138 (class 0 OID 0)
-- Dependencies: 296
-- Name: partner_contacts_id_seq; Type: SEQUENCE OWNED BY; Schema: partner_module; Owner: -
--

ALTER SEQUENCE partner_module.partner_contacts_id_seq OWNED BY partner_module.partner_contacts.id;


--
-- TOC entry 308 (class 1259 OID 26143)
-- Name: partner_sales_summary; Type: TABLE; Schema: partner_module; Owner: -
--

CREATE TABLE partner_module.partner_sales_summary (
    partner_id bigint NOT NULL,
    total_quantity bigint NOT NULL,
    CONSTRAINT partner_sales_summary_total_quantity_check CHECK ((total_quantity >= 0))
);


--
-- TOC entry 293 (class 1259 OID 26042)
-- Name: partner_types; Type: TABLE; Schema: partner_module; Owner: -
--

CREATE TABLE partner_module.partner_types (
    id bigint NOT NULL,
    name character varying(100) NOT NULL
);


--
-- TOC entry 292 (class 1259 OID 26041)
-- Name: partner_types_id_seq; Type: SEQUENCE; Schema: partner_module; Owner: -
--

CREATE SEQUENCE partner_module.partner_types_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5139 (class 0 OID 0)
-- Dependencies: 292
-- Name: partner_types_id_seq; Type: SEQUENCE OWNED BY; Schema: partner_module; Owner: -
--

ALTER SEQUENCE partner_module.partner_types_id_seq OWNED BY partner_module.partner_types.id;


--
-- TOC entry 295 (class 1259 OID 26051)
-- Name: partners; Type: TABLE; Schema: partner_module; Owner: -
--

CREATE TABLE partner_module.partners (
    id bigint NOT NULL,
    partner_type_id bigint NOT NULL,
    name character varying(255) NOT NULL,
    director_full_name character varying(255) NOT NULL,
    legal_address character varying(500) NOT NULL,
    inn character varying(12) NOT NULL,
    rating integer NOT NULL,
    CONSTRAINT partners_rating_check CHECK ((rating >= 0))
);


--
-- TOC entry 294 (class 1259 OID 26050)
-- Name: partners_id_seq; Type: SEQUENCE; Schema: partner_module; Owner: -
--

CREATE SEQUENCE partner_module.partners_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5140 (class 0 OID 0)
-- Dependencies: 294
-- Name: partners_id_seq; Type: SEQUENCE OWNED BY; Schema: partner_module; Owner: -
--

ALTER SEQUENCE partner_module.partners_id_seq OWNED BY partner_module.partners.id;


--
-- TOC entry 299 (class 1259 OID 26080)
-- Name: product_types; Type: TABLE; Schema: partner_module; Owner: -
--

CREATE TABLE partner_module.product_types (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    type_coefficient numeric(10,4) NOT NULL
);


--
-- TOC entry 298 (class 1259 OID 26079)
-- Name: product_types_id_seq; Type: SEQUENCE; Schema: partner_module; Owner: -
--

CREATE SEQUENCE partner_module.product_types_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5141 (class 0 OID 0)
-- Dependencies: 298
-- Name: product_types_id_seq; Type: SEQUENCE OWNED BY; Schema: partner_module; Owner: -
--

ALTER SEQUENCE partner_module.product_types_id_seq OWNED BY partner_module.product_types.id;


--
-- TOC entry 301 (class 1259 OID 26089)
-- Name: products; Type: TABLE; Schema: partner_module; Owner: -
--

CREATE TABLE partner_module.products (
    id bigint NOT NULL,
    product_type_id bigint NOT NULL,
    name character varying(255) NOT NULL,
    article character varying(50) NOT NULL,
    min_price_for_partner numeric(12,2) NOT NULL,
    CONSTRAINT products_min_price_for_partner_check CHECK ((min_price_for_partner >= (0)::numeric))
);


--
-- TOC entry 300 (class 1259 OID 26088)
-- Name: products_id_seq; Type: SEQUENCE; Schema: partner_module; Owner: -
--

CREATE SEQUENCE partner_module.products_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5142 (class 0 OID 0)
-- Dependencies: 300
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: partner_module; Owner: -
--

ALTER SEQUENCE partner_module.products_id_seq OWNED BY partner_module.products.id;


--
-- TOC entry 307 (class 1259 OID 26126)
-- Name: sale_items; Type: TABLE; Schema: partner_module; Owner: -
--

CREATE TABLE partner_module.sale_items (
    id bigint NOT NULL,
    sale_id bigint NOT NULL,
    product_id bigint NOT NULL,
    quantity integer NOT NULL,
    CONSTRAINT sale_items_quantity_check CHECK ((quantity > 0))
);


--
-- TOC entry 306 (class 1259 OID 26125)
-- Name: sale_items_id_seq; Type: SEQUENCE; Schema: partner_module; Owner: -
--

CREATE SEQUENCE partner_module.sale_items_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5143 (class 0 OID 0)
-- Dependencies: 306
-- Name: sale_items_id_seq; Type: SEQUENCE OWNED BY; Schema: partner_module; Owner: -
--

ALTER SEQUENCE partner_module.sale_items_id_seq OWNED BY partner_module.sale_items.id;


--
-- TOC entry 305 (class 1259 OID 26114)
-- Name: sales; Type: TABLE; Schema: partner_module; Owner: -
--

CREATE TABLE partner_module.sales (
    id bigint NOT NULL,
    partner_id bigint NOT NULL,
    sale_date date NOT NULL
);


--
-- TOC entry 304 (class 1259 OID 26113)
-- Name: sales_id_seq; Type: SEQUENCE; Schema: partner_module; Owner: -
--

CREATE SEQUENCE partner_module.sales_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5144 (class 0 OID 0)
-- Dependencies: 304
-- Name: sales_id_seq; Type: SEQUENCE OWNED BY; Schema: partner_module; Owner: -
--

ALTER SEQUENCE partner_module.sales_id_seq OWNED BY partner_module.sales.id;


--
-- TOC entry 4927 (class 2604 OID 26107)
-- Name: material_types id; Type: DEFAULT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.material_types ALTER COLUMN id SET DEFAULT nextval('partner_module.material_types_id_seq'::regclass);


--
-- TOC entry 4924 (class 2604 OID 26071)
-- Name: partner_contacts id; Type: DEFAULT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.partner_contacts ALTER COLUMN id SET DEFAULT nextval('partner_module.partner_contacts_id_seq'::regclass);


--
-- TOC entry 4922 (class 2604 OID 26045)
-- Name: partner_types id; Type: DEFAULT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.partner_types ALTER COLUMN id SET DEFAULT nextval('partner_module.partner_types_id_seq'::regclass);


--
-- TOC entry 4923 (class 2604 OID 26054)
-- Name: partners id; Type: DEFAULT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.partners ALTER COLUMN id SET DEFAULT nextval('partner_module.partners_id_seq'::regclass);


--
-- TOC entry 4925 (class 2604 OID 26083)
-- Name: product_types id; Type: DEFAULT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.product_types ALTER COLUMN id SET DEFAULT nextval('partner_module.product_types_id_seq'::regclass);


--
-- TOC entry 4926 (class 2604 OID 26092)
-- Name: products id; Type: DEFAULT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.products ALTER COLUMN id SET DEFAULT nextval('partner_module.products_id_seq'::regclass);


--
-- TOC entry 4929 (class 2604 OID 26129)
-- Name: sale_items id; Type: DEFAULT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.sale_items ALTER COLUMN id SET DEFAULT nextval('partner_module.sale_items_id_seq'::regclass);


--
-- TOC entry 4928 (class 2604 OID 26117)
-- Name: sales id; Type: DEFAULT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.sales ALTER COLUMN id SET DEFAULT nextval('partner_module.sales_id_seq'::regclass);


--
-- TOC entry 5126 (class 0 OID 26104)
-- Dependencies: 303
-- Data for Name: material_types; Type: TABLE DATA; Schema: partner_module; Owner: -
--

COPY partner_module.material_types (id, name, defect_percent) FROM stdin;
1	Тип материала 1	0.0010
2	Тип материала 2	0.0095
3	Тип материала 3	0.0028
4	Тип материала 4	0.0055
5	Тип материала 5	0.0034
\.


--
-- TOC entry 5120 (class 0 OID 26068)
-- Dependencies: 297
-- Data for Name: partner_contacts; Type: TABLE DATA; Schema: partner_module; Owner: -
--

COPY partner_module.partner_contacts (id, partner_id, email, phone) FROM stdin;
1	1	aleksandraivanova@ml.ru	493 123 45 67
2	2	vppetrov@vl.ru	987 123 56 78
3	3	ansolovev@st.ru	812 223 32 00
4	4	ekaterina.vorobeva@ml.ru	444 222 33 11
5	5	stepanov@stepan.ru	912 888 33 33
6	8	test.partner@example.com	900 123 45 67
\.


--
-- TOC entry 5131 (class 0 OID 26143)
-- Dependencies: 308
-- Data for Name: partner_sales_summary; Type: TABLE DATA; Schema: partner_module; Owner: -
--

COPY partner_module.partner_sales_summary (partner_id, total_quantity) FROM stdin;
1	65250
2	44800
3	9750
4	100750
5	780000
8	0
\.


--
-- TOC entry 5116 (class 0 OID 26042)
-- Dependencies: 293
-- Data for Name: partner_types; Type: TABLE DATA; Schema: partner_module; Owner: -
--

COPY partner_module.partner_types (id, name) FROM stdin;
1	ЗАО
2	ООО
3	ПАО
4	ОАО
\.


--
-- TOC entry 5118 (class 0 OID 26051)
-- Dependencies: 295
-- Data for Name: partners; Type: TABLE DATA; Schema: partner_module; Owner: -
--

COPY partner_module.partners (id, partner_type_id, name, director_full_name, legal_address, inn, rating) FROM stdin;
1	1	База Строитель	Иванова Александра Ивановна	652050, Кемеровская область, город Юрга, ул. Лесная, 15	2222455179	7
2	2	Паркет 29	Петров Василий Петрович	164500, Архангельская область, город Северодвинск, ул. Строителей, 18	3333888520	7
3	3	Стройсервис	Соловьев Андрей Николаевич	188910, Ленинградская область, город Приморск, ул. Парковая, 21	4440391035	7
4	4	Ремонт и отделка	Воробьева Екатерина Валерьевна	143960, Московская область, город Реутов, ул. Свободы, 51	1111520857	5
5	1	МонтажПро	Степанов Степан Сергеевич	309500, Белгородская область, город Старый Оскол, ул. Рабочая, 122	5552431140	10
8	2	Тестовый партнёр	Тестов Тест Тестович	000000, Тестовый город, ул. Тестовая, д. 1	9999999991	5
\.


--
-- TOC entry 5122 (class 0 OID 26080)
-- Dependencies: 299
-- Data for Name: product_types; Type: TABLE DATA; Schema: partner_module; Owner: -
--

COPY partner_module.product_types (id, name, type_coefficient) FROM stdin;
1	Ламинат	2.3500
2	Массивная доска	5.1500
3	Паркетная доска	4.3400
4	Пробковое покрытие	1.5000
\.


--
-- TOC entry 5124 (class 0 OID 26089)
-- Dependencies: 301
-- Data for Name: products; Type: TABLE DATA; Schema: partner_module; Owner: -
--

COPY partner_module.products (id, product_type_id, name, article, min_price_for_partner) FROM stdin;
1	3	Паркетная доска Ясень темный однополосная 14 мм	8758385	4456.90
2	3	Инженерная доска Дуб Французская елка однополосная 12 мм	8858958	7330.99
3	1	Ламинат Дуб дымчато-белый 33 класс 12 мм	7750282	1799.33
4	1	Ламинат Дуб серый 32 класс 8 мм с фаской	7028748	3890.41
5	4	Пробковое напольное клеевое покрытие 32 класс 4 мм	5012543	5450.59
\.


--
-- TOC entry 5130 (class 0 OID 26126)
-- Dependencies: 307
-- Data for Name: sale_items; Type: TABLE DATA; Schema: partner_module; Owner: -
--

COPY partner_module.sale_items (id, sale_id, product_id, quantity) FROM stdin;
1	1	1	15500
2	2	3	12350
3	3	4	37400
4	4	2	35000
5	5	5	1250
6	6	3	1000
7	7	1	7550
8	8	1	7250
9	9	2	2500
10	10	4	59050
11	11	3	37200
12	12	5	4500
13	13	3	50000
14	14	4	670000
15	15	1	35000
16	16	2	25000
17	18	1	100
\.


--
-- TOC entry 5128 (class 0 OID 26114)
-- Dependencies: 305
-- Data for Name: sales; Type: TABLE DATA; Schema: partner_module; Owner: -
--

COPY partner_module.sales (id, partner_id, sale_date) FROM stdin;
1	1	2023-03-23
2	1	2023-12-18
3	1	2024-06-07
4	2	2022-12-02
5	2	2023-05-17
6	2	2024-06-07
7	2	2024-07-01
8	3	2023-01-22
9	3	2024-07-05
10	4	2023-03-20
11	4	2024-03-12
12	4	2024-05-14
13	5	2023-09-19
14	5	2023-11-10
15	5	2024-04-15
16	5	2024-06-12
17	8	2024-01-01
18	8	2024-01-01
\.


--
-- TOC entry 5145 (class 0 OID 0)
-- Dependencies: 302
-- Name: material_types_id_seq; Type: SEQUENCE SET; Schema: partner_module; Owner: -
--

SELECT pg_catalog.setval('partner_module.material_types_id_seq', 1, false);


--
-- TOC entry 5146 (class 0 OID 0)
-- Dependencies: 296
-- Name: partner_contacts_id_seq; Type: SEQUENCE SET; Schema: partner_module; Owner: -
--

SELECT pg_catalog.setval('partner_module.partner_contacts_id_seq', 11, true);


--
-- TOC entry 5147 (class 0 OID 0)
-- Dependencies: 292
-- Name: partner_types_id_seq; Type: SEQUENCE SET; Schema: partner_module; Owner: -
--

SELECT pg_catalog.setval('partner_module.partner_types_id_seq', 1, false);


--
-- TOC entry 5148 (class 0 OID 0)
-- Dependencies: 294
-- Name: partners_id_seq; Type: SEQUENCE SET; Schema: partner_module; Owner: -
--

SELECT pg_catalog.setval('partner_module.partners_id_seq', 17, true);


--
-- TOC entry 5149 (class 0 OID 0)
-- Dependencies: 298
-- Name: product_types_id_seq; Type: SEQUENCE SET; Schema: partner_module; Owner: -
--

SELECT pg_catalog.setval('partner_module.product_types_id_seq', 1, false);


--
-- TOC entry 5150 (class 0 OID 0)
-- Dependencies: 300
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: partner_module; Owner: -
--

SELECT pg_catalog.setval('partner_module.products_id_seq', 1, false);


--
-- TOC entry 5151 (class 0 OID 0)
-- Dependencies: 306
-- Name: sale_items_id_seq; Type: SEQUENCE SET; Schema: partner_module; Owner: -
--

SELECT pg_catalog.setval('partner_module.sale_items_id_seq', 17, true);


--
-- TOC entry 5152 (class 0 OID 0)
-- Dependencies: 304
-- Name: sales_id_seq; Type: SEQUENCE SET; Schema: partner_module; Owner: -
--

SELECT pg_catalog.setval('partner_module.sales_id_seq', 18, true);


--
-- TOC entry 4954 (class 2606 OID 26112)
-- Name: material_types material_types_name_key; Type: CONSTRAINT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.material_types
    ADD CONSTRAINT material_types_name_key UNIQUE (name);


--
-- TOC entry 4956 (class 2606 OID 26110)
-- Name: material_types material_types_pkey; Type: CONSTRAINT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.material_types
    ADD CONSTRAINT material_types_pkey PRIMARY KEY (id);


--
-- TOC entry 4944 (class 2606 OID 26073)
-- Name: partner_contacts partner_contacts_pkey; Type: CONSTRAINT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.partner_contacts
    ADD CONSTRAINT partner_contacts_pkey PRIMARY KEY (id);


--
-- TOC entry 4962 (class 2606 OID 26148)
-- Name: partner_sales_summary partner_sales_summary_pkey; Type: CONSTRAINT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.partner_sales_summary
    ADD CONSTRAINT partner_sales_summary_pkey PRIMARY KEY (partner_id);


--
-- TOC entry 4936 (class 2606 OID 26049)
-- Name: partner_types partner_types_name_key; Type: CONSTRAINT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.partner_types
    ADD CONSTRAINT partner_types_name_key UNIQUE (name);


--
-- TOC entry 4938 (class 2606 OID 26047)
-- Name: partner_types partner_types_pkey; Type: CONSTRAINT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.partner_types
    ADD CONSTRAINT partner_types_pkey PRIMARY KEY (id);


--
-- TOC entry 4940 (class 2606 OID 26061)
-- Name: partners partners_inn_key; Type: CONSTRAINT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.partners
    ADD CONSTRAINT partners_inn_key UNIQUE (inn);


--
-- TOC entry 4942 (class 2606 OID 26059)
-- Name: partners partners_pkey; Type: CONSTRAINT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.partners
    ADD CONSTRAINT partners_pkey PRIMARY KEY (id);


--
-- TOC entry 4946 (class 2606 OID 26087)
-- Name: product_types product_types_name_key; Type: CONSTRAINT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.product_types
    ADD CONSTRAINT product_types_name_key UNIQUE (name);


--
-- TOC entry 4948 (class 2606 OID 26085)
-- Name: product_types product_types_pkey; Type: CONSTRAINT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.product_types
    ADD CONSTRAINT product_types_pkey PRIMARY KEY (id);


--
-- TOC entry 4950 (class 2606 OID 26097)
-- Name: products products_article_key; Type: CONSTRAINT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.products
    ADD CONSTRAINT products_article_key UNIQUE (article);


--
-- TOC entry 4952 (class 2606 OID 26095)
-- Name: products products_pkey; Type: CONSTRAINT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- TOC entry 4960 (class 2606 OID 26132)
-- Name: sale_items sale_items_pkey; Type: CONSTRAINT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.sale_items
    ADD CONSTRAINT sale_items_pkey PRIMARY KEY (id);


--
-- TOC entry 4958 (class 2606 OID 26119)
-- Name: sales sales_pkey; Type: CONSTRAINT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.sales
    ADD CONSTRAINT sales_pkey PRIMARY KEY (id);


--
-- TOC entry 4964 (class 2606 OID 26074)
-- Name: partner_contacts partner_contacts_partner_id_fkey; Type: FK CONSTRAINT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.partner_contacts
    ADD CONSTRAINT partner_contacts_partner_id_fkey FOREIGN KEY (partner_id) REFERENCES partner_module.partners(id) ON DELETE CASCADE;


--
-- TOC entry 4969 (class 2606 OID 26149)
-- Name: partner_sales_summary partner_sales_summary_partner_id_fkey; Type: FK CONSTRAINT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.partner_sales_summary
    ADD CONSTRAINT partner_sales_summary_partner_id_fkey FOREIGN KEY (partner_id) REFERENCES partner_module.partners(id) ON DELETE CASCADE;


--
-- TOC entry 4963 (class 2606 OID 26062)
-- Name: partners partners_partner_type_id_fkey; Type: FK CONSTRAINT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.partners
    ADD CONSTRAINT partners_partner_type_id_fkey FOREIGN KEY (partner_type_id) REFERENCES partner_module.partner_types(id);


--
-- TOC entry 4965 (class 2606 OID 26098)
-- Name: products products_product_type_id_fkey; Type: FK CONSTRAINT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.products
    ADD CONSTRAINT products_product_type_id_fkey FOREIGN KEY (product_type_id) REFERENCES partner_module.product_types(id);


--
-- TOC entry 4967 (class 2606 OID 26138)
-- Name: sale_items sale_items_product_id_fkey; Type: FK CONSTRAINT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.sale_items
    ADD CONSTRAINT sale_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES partner_module.products(id);


--
-- TOC entry 4968 (class 2606 OID 26133)
-- Name: sale_items sale_items_sale_id_fkey; Type: FK CONSTRAINT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.sale_items
    ADD CONSTRAINT sale_items_sale_id_fkey FOREIGN KEY (sale_id) REFERENCES partner_module.sales(id) ON DELETE CASCADE;


--
-- TOC entry 4966 (class 2606 OID 26120)
-- Name: sales sales_partner_id_fkey; Type: FK CONSTRAINT; Schema: partner_module; Owner: -
--

ALTER TABLE ONLY partner_module.sales
    ADD CONSTRAINT sales_partner_id_fkey FOREIGN KEY (partner_id) REFERENCES partner_module.partners(id);


-- Completed on 2025-12-10 07:29:48

--
-- PostgreSQL database dump complete
--

