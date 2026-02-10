--
-- PostgreSQL database dump
--

\restrict DWdRjj1jwiNQZsmmhenCdcXrbuMlGI64iiJJbiDFS7bo8RgM93BGbgIGhcTgkIh

-- Dumped from database version 17.7
-- Dumped by pg_dump version 17.7

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
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$

BEGIN

    NEW.updated_at = CURRENT_TIMESTAMP;

    RETURN NEW;

END;

$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: exam_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exam_sessions (
    session_id integer NOT NULL,
    user_id character varying,
    status character varying NOT NULL,
    n_questions integer NOT NULL,
    current_question_num integer NOT NULL,
    theta_math double precision NOT NULL,
    theta_tech double precision NOT NULL,
    theta_se_math double precision NOT NULL,
    theta_se_tech double precision NOT NULL,
    math_count integer NOT NULL,
    tech_count integer NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    completed_at timestamp without time zone
);


ALTER TABLE public.exam_sessions OWNER TO postgres;

--
-- Name: exam_sessions_session_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.exam_sessions_session_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.exam_sessions_session_id_seq OWNER TO postgres;

--
-- Name: exam_sessions_session_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.exam_sessions_session_id_seq OWNED BY public.exam_sessions.session_id;


--
-- Name: questions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.questions (
    unique_id integer NOT NULL,
    domain character varying(100) NOT NULL,
    concept_tag character varying(200) NOT NULL,
    question_text text NOT NULL,
    options jsonb NOT NULL,
    correct_answer jsonb NOT NULL,
    image_url text,
    question_type character varying(10) DEFAULT 'MCQ'::character varying,
    a_values double precision[] NOT NULL,
    b_value double precision NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    calibration_status character varying(20) DEFAULT 'operational'::character varying
);


ALTER TABLE public.questions OWNER TO postgres;

--
-- Name: responses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.responses (
    response_id integer NOT NULL,
    session_id integer NOT NULL,
    question_id integer NOT NULL,
    question_num integer NOT NULL,
    user_answer character varying,
    is_correct boolean,
    theta_math_after double precision,
    theta_tech_after double precision,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.responses OWNER TO postgres;

--
-- Name: responses_response_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.responses_response_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.responses_response_id_seq OWNER TO postgres;

--
-- Name: responses_response_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.responses_response_id_seq OWNED BY public.responses.response_id;


--
-- Name: exam_sessions session_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exam_sessions ALTER COLUMN session_id SET DEFAULT nextval('public.exam_sessions_session_id_seq'::regclass);


--
-- Name: responses response_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.responses ALTER COLUMN response_id SET DEFAULT nextval('public.responses_response_id_seq'::regclass);


--
-- Data for Name: exam_sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exam_sessions (session_id, user_id, status, n_questions, current_question_num, theta_math, theta_tech, theta_se_math, theta_se_tech, math_count, tech_count, created_at, updated_at, completed_at) FROM stdin;
1	string	in_progress	40	0	0	0	1	1	0	0	2026-01-23 00:43:11.863003	\N	\N
2	string	in_progress	40	0	0	0	1	1	0	0	2026-01-23 00:44:04.156123	\N	\N
21	string	in_progress	40	2	-0.0066747968203235055	-0.006184264348818691	0.4925545705265781	0.6567255726181813	2	0	2026-01-27 13:54:43.565976	2026-01-27 22:55:32.899543	\N
3	string	in_progress	40	0	0	0	1	1	0	0	2026-01-23 00:50:08.858082	\N	\N
4	ag	in_progress	40	0	0	0	1	1	0	0	2026-01-23 00:53:03.673625	\N	\N
61	\N	in_progress	50	5	0.38981028872678464	0.6734300930448026	0.4603171832342206	0.5436883570142129	4	1	2026-01-29 21:28:46.690423	2026-01-29 21:29:00.41175	\N
59	\N	in_progress	50	2	-0.37152763555168755	-0.17238162451950403	0.5765042833385017	0.6905897411543986	2	0	2026-01-29 21:27:26.010868	2026-01-29 21:27:32.636556	\N
39	\N	in_progress	40	0	0	0	1	1	0	0	2026-01-27 23:44:29.871455	2026-01-27 23:44:29.871455	\N
38	\N	in_progress	40	3	0.7610785213674428	0.7896561862863986	0.5318724429925918	0.5482902360331715	2	1	2026-01-27 23:23:57.537807	2026-01-27 23:59:09.680444	\N
40	\N	in_progress	40	2	0.32522549229892067	-0.04391490607473294	0.56762528971345	0.566162356515218	1	1	2026-01-28 10:10:29.176959	2026-01-28 10:10:40.112871	\N
55	\N	completed	50	50	-0.5588607737234272	-0.5772435827476242	0.2539063019250522	0.27038220954081554	20	20	2026-01-29 16:56:05.243645	2026-01-29 17:12:28.894021	2026-01-29 17:12:28.89682
41	\N	in_progress	40	2	-0.7174354970013663	-0.3699643441601837	0.5128615811196593	0.6575694454134794	2	0	2026-01-28 10:38:46.511544	2026-01-28 10:38:49.803704	\N
42	\N	in_progress	40	1	0.39819192717689855	0.2072280171248071	0.5770995923742086	0.6742485348276949	1	0	2026-01-28 10:49:55.217403	2026-01-28 11:15:37.165599	\N
43	\N	in_progress	40	1	0.3574075133337231	0.16755958556925019	0.6058485997023006	0.6898475246369596	1	0	2026-01-28 11:20:58.968904	2026-01-28 11:21:23.860135	\N
44	\N	in_progress	40	0	0	0	1	1	0	0	2026-01-29 00:06:42.287754	2026-01-29 00:06:42.287754	\N
45	\N	in_progress	40	0	0	0	1	1	0	0	2026-01-29 00:06:49.210608	2026-01-29 00:06:49.210608	\N
46	\N	in_progress	40	0	0	0	1	1	0	0	2026-01-29 00:13:51.585481	2026-01-29 00:13:51.585481	\N
47	\N	in_progress	40	0	0	0	1	1	0	0	2026-01-29 10:46:48.78896	2026-01-29 10:46:48.78896	\N
48	\N	in_progress	40	0	0	0	1	1	0	0	2026-01-29 10:54:11.755294	2026-01-29 10:54:11.755294	\N
49	\N	in_progress	40	0	0	0	1	1	0	0	2026-01-29 11:15:12.317854	2026-01-29 11:15:12.317854	\N
5	sg	in_progress	40	20	-0.3562861995454416	-0.03726461487040826	0.28592976264656594	0.34250635435445975	0	20	2026-01-23 00:54:05.207777	2026-01-23 00:58:35.574969	\N
6	sg	in_progress	40	0	0	0	1	1	0	0	2026-01-23 01:00:07.95379	\N	\N
7	string	in_progress	40	0	0	0	1	1	0	0	2026-01-23 01:01:10.763857	\N	\N
50	\N	in_progress	40	1	0	0	1	1	1	0	2026-01-29 11:21:35.049762	2026-01-29 11:22:00.356576	\N
64	\N	in_progress	50	1	0	0	1	1	1	0	2026-01-29 21:52:30.803005	2026-01-29 21:52:36.166733	\N
60	\N	in_progress	50	3	0.5885852155879178	0.28998770379769573	0.5277606938008818	0.6620085780695621	2	1	2026-01-29 21:27:38.715181	2026-01-29 21:27:46.673362	\N
26	johnn	completed	40	40	2.194468231720819	1.847618395330106	0.48393334313298175	0.32473713405411075	20	20	2026-01-27 14:42:54.142484	2026-01-27 14:54:26.688607	2026-01-27 09:09:27.517188
10	s3	completed	40	40	0.3607787422024842	0.3890882037528862	0.27637665353392277	0.28599851211388794	20	20	2026-01-23 11:50:30.742287	2026-01-23 12:19:25.689289	2026-01-23 06:34:26.603237
11	string	in_progress	40	0	0	0	1	1	0	0	2026-01-23 12:27:27.089779	\N	\N
12	string	in_progress	40	0	0	0	1	1	0	0	2026-01-26 15:42:11.653462	\N	\N
13	string	in_progress	40	0	0	0	1	1	0	0	2026-01-26 15:42:43.404365	\N	\N
25	jon	completed	40	40	-0.05537385703491348	0.4401495777304417	0.25181192596278545	0.2696227736873159	20	20	2026-01-27 14:35:27.383956	2026-01-27 14:40:28.888511	2026-01-27 08:55:29.645515
8	s1	in_progress	40	20	0.38657670578361397	0.22796577300255488	0.34921191657111966	0.31748738526956183	0	20	2026-01-23 10:16:15.605203	2026-01-23 10:19:59.743902	\N
9	string	in_progress	40	0	0	0	1	1	0	0	2026-01-23 11:44:30.361997	\N	\N
14	student123	in_progress	40	5	-0.8994534090359122	-0.4347516284971398	0.47754380094286497	0.529722693139681	3	2	2026-01-26 15:43:53.043802	2026-01-26 15:44:24.421378	\N
65	\N	in_progress	50	1	0	0	1	1	1	0	2026-01-29 21:52:42.1878	2026-01-29 21:53:22.532456	\N
28	string	in_progress	40	1	0.3767498613336524	0.17001264057623514	0.6025983313523648	0.6934627014571366	1	0	2026-01-27 16:26:23.349285	2026-01-27 16:27:07.198963	\N
29	string	in_progress	40	1	0.3789393796273084	0.21094559077343078	0.5936379563720939	0.6823163103808094	1	0	2026-01-27 16:32:07.67186	2026-01-27 16:32:26.881846	\N
34	lk	in_progress	40	1	0.3945842334733626	0.20400461459036806	0.6246296992455898	0.6818761601529666	1	0	2026-01-27 16:57:44.464387	2026-01-27 16:57:47.26995	\N
35	string	in_progress	40	0	0	0	1	1	0	0	2026-01-27 17:14:35.760028	2026-01-27 17:14:35.760028	\N
27	string	in_progress	40	1	-0.4440502331321965	-0.2349126747322577	0.603859316452915	0.6859919491075364	1	0	2026-01-27 16:23:03.024712	2026-01-27 19:58:29.590735	\N
36	string	in_progress	40	0	0	0	1	1	0	0	2026-01-27 22:53:55.480324	2026-01-27 22:53:55.480324	\N
51	\N	in_progress	40	5	-0.10978531858817756	-0.05802888661742837	0.40835395105264544	0.6383589377697606	5	0	2026-01-29 11:51:49.813683	2026-01-29 11:52:13.600254	\N
68	\N	in_progress	50	7	-1.1578182121349745	-0.8824042770959909	0.45682258149166205	0.5950341423550595	5	2	2026-01-30 01:05:18.729763	2026-01-30 01:05:51.717018	\N
56	\N	completed	50	50	-0.25412753728949744	0.17998585926901095	0.25835931504551946	0.27380153505963956	20	20	2026-01-29 20:36:01.48898	2026-01-29 20:40:25.246794	2026-01-29 20:40:25.250495
53	\N	completed	50	50	-0.6941518130826374	-0.8974686964268564	0.26511697569394993	0.3065997578769114	20	20	2026-01-29 12:38:21.904193	2026-01-29 12:41:25.558787	2026-01-29 12:41:25.564169
52	\N	completed	40	40	-1.1006804541837512	-0.8772608366793326	0.32528625444468096	0.31619057019164915	16	15	2026-01-29 12:19:40.400597	2026-01-29 12:22:39.176605	2026-01-29 12:22:39.182389
57	\N	in_progress	50	1	0	0	1	1	1	0	2026-01-29 21:27:05.91254	2026-01-29 21:27:08.790093	\N
54	\N	completed	50	50	-0.9440491510763656	-1.2988416750085758	0.25956211520250316	0.3299449073466591	20	20	2026-01-29 16:00:29.241791	2026-01-29 16:08:06.291296	2026-01-29 16:08:06.293521
58	\N	in_progress	50	1	0	0	1	1	1	0	2026-01-29 21:27:15.655353	2026-01-29 21:27:18.48588	\N
66	\N	in_progress	50	23	-1.0272871389783282	-1.0283376172433463	0.35488830451051995	0.4101026285243076	9	8	2026-01-30 00:40:40.405597	2026-01-30 00:48:02.375715	\N
62	\N	in_progress	50	6	0.6963178565770196	0.27282274046045	0.47354295289891457	0.506418735499215	3	3	2026-01-29 21:29:06.448026	2026-01-29 21:29:25.124689	\N
63	\N	in_progress	50	1	0	0	1	1	1	0	2026-01-29 21:52:22.697644	2026-01-29 21:52:25.753571	\N
70	\N	in_progress	50	4	0.788234609825408	0.8126138172742831	0.5320071420399395	0.5564881776052121	2	2	2026-01-30 10:39:02.081668	2026-01-30 10:39:57.777444	\N
69	\N	in_progress	50	42	-1.011983556118005	-0.9426213460767717	0.29620970992642026	0.31115415676713737	18	16	2026-01-30 01:07:12.685536	2026-01-30 01:15:07.344624	\N
67	\N	in_progress	50	38	-0.4888075858931619	-0.21292119438220572	0.26905335619303844	0.2948098505778102	16	17	2026-01-30 00:58:10.190762	2026-01-30 01:18:46.849338	\N
72	\N	completed	50	50	-1.0996702244260985	-0.30307165990196383	0.2872800702577407	0.2853082823746712	20	22	2026-01-30 10:54:26.592595	2026-01-30 10:59:23.668886	2026-01-30 10:59:23.67145
71	\N	in_progress	50	24	-0.5598399833914206	-0.9659357889747343	0.28350487731198337	0.4029227644197523	14	7	2026-01-30 10:52:09.698013	2026-01-30 10:52:45.179911	\N
73	\N	in_progress	50	3	-0.580416492419973	-0.2850300889648732	0.543346416208494	0.6780526478250088	3	0	2026-01-30 10:54:45.785262	2026-01-30 10:55:04.149743	\N
74	\N	completed	50	50	-0.5647234614635666	0.0752960342347337	0.24270022729402235	0.263837327545181	22	22	2026-01-30 11:09:03.91469	2026-01-30 11:24:28.944672	2026-01-30 11:24:28.948617
75	\N	in_progress	50	14	-0.37273976588836755	-0.7121257161472851	0.3714604027943458	0.4138862021214251	6	5	2026-01-30 11:22:03.110309	2026-01-30 11:23:01.766073	\N
76	\N	completed	50	50	2.189315415553187	1.9095624781285387	0.5089953967936286	0.3970388532333153	19	28	2026-01-30 11:24:35.596356	2026-01-30 11:31:26.773149	2026-01-30 11:31:26.776442
78	\N	in_progress	50	2	-0.3625720269817973	-0.1848328535480918	0.5751801990571133	0.6463113453674634	2	0	2026-01-30 13:49:28.208513	2026-01-30 13:57:16.018703	\N
77	\N	in_progress	50	2	0.4309533055858173	0.21295512917911283	0.5900270356646463	0.6822990822241427	2	0	2026-01-30 13:49:23.273627	2026-01-30 13:57:19.510483	\N
80	\N	in_progress	50	2	-0.3732274159584525	-0.20076352470934103	0.5865875852272253	0.668637251792985	2	0	2026-01-30 13:57:35.642499	2026-01-30 14:09:16.626847	\N
79	\N	in_progress	50	14	0.42272374132678425	0.3829216253341201	0.39086972977182133	0.40329097080575754	6	5	2026-01-30 13:57:32.937381	2026-01-30 14:56:05.212973	\N
82	\N	in_progress	50	5	0.27673980236749174	0.12151596524515493	0.41805580218429966	0.6540564148971063	5	0	2026-01-30 15:05:35.36426	2026-01-30 15:06:15.019999	\N
83	\N	in_progress	50	19	-1.2996948651707214	-1.0033612532827252	0.42398887905140203	0.37444034998482884	8	8	2026-01-30 15:05:40.077993	2026-01-30 15:07:55.077179	\N
81	\N	in_progress	50	28	-1.0784170138323736	-0.38017099274458277	0.350881537264729	0.3093578781909153	11	14	2026-01-30 14:09:28.780575	2026-01-30 14:57:47.165854	\N
84	\N	in_progress	50	0	0	0	1	1	0	0	2026-02-06 15:06:33.678908	2026-02-06 15:06:33.678908	\N
85	\N	in_progress	50	0	0	0	1	1	0	0	2026-02-06 15:08:14.49117	2026-02-06 15:08:14.49117	\N
86	\N	in_progress	50	0	0	0	1	1	0	0	2026-02-06 15:21:24.415799	2026-02-06 15:21:24.415799	\N
\.


--
-- Data for Name: questions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.questions (unique_id, domain, concept_tag, question_text, options, correct_answer, image_url, question_type, a_values, b_value, created_at, updated_at, calibration_status) FROM stdin;
19	tech	Python / Lists	Given a = [1,2,3,4,5,6]. Here, which of the following will remove element 4 from the list?	["a[3:4] = [ ]", "a.pop(3)", "a[3] = [ ]", "a.remove(4)"]	["a.remove(4)", "a[3:4] = [ ]", "a.pop(3)"]	\N	MSQ	{0,2.0540130011}	2.3653834054	2026-01-22 23:07:51.972777	2026-01-23 11:40:34.56634	operational
56	math	Statistics / Hypothesis Testing	A software company is running an A/B test to compare two versions of their homepage Version A (current design) and Version B (new design). After conducting the test with a sample of users, they calculate a p-value of 0.02. What does this p-value indicate about the results of the A/B test?	["There is a 2% chance that the observed user behavior would occur if the new homepage (Version B) is better than the current homepage (Version A).", "There is a 2% chance that the new homepage (Version B) is better than the current homepage (Version A).", "There is a 2% chance that the observed user behavior would occur if the current homepage (Version A) is equally effective as the new homepage (Version B)", "There is a 2% chance that the new homepage (Version B) is worse than the current homepage (Version A)."]	"There is a 2% chance that the observed user behavior would occur if the current homepage (Version A) is equally effective as the new homepage (Version B)"	\N	MCQ	{0.5419879944,0}	0.5838367915	2026-01-22 23:07:51.987325	2026-01-23 11:40:34.56634	operational
58	tech	Python / Data Structures	Suppose d = {"Ben": 40, "Ten": 45}. To obtain the number of entries in the dictionary, which command do we use?	["d.size()", "len(d)", "size(d)", "d.len()"]	"len(d)"	\N	MCQ	{0,1.7741933218}	-0.5635470531	2026-01-22 23:07:51.988327	2026-01-23 11:40:34.56634	operational
59	tech	Python / Debugging	Debug the code 	["Error in line 1", "Error in 6", "Error in line 14", "No Error, the works"]	"Error in 6"	https://s3.amazonaws.com/fuseclassroom-resources-prod/quiz/image/60c84a9ac0f08d0098f132ce/1743755344662.png	MCQ	{0,0.1549376809}	2.9706474626	2026-01-22 23:07:51.988327	2026-01-23 11:40:34.56634	operational
60	tech	Programming / OOP	You are designing a system with different types of sensors. Using Object-Oriented Programming (OOP) principles, how would you best represent these sensors?	["Creating a single function to handle all sensor types.", "Designing a class hierarchy of sensors", "Storing sensor data in a dictionary", "Using a global variable to represent an object for each sensor."]	"Designing a class hierarchy of sensors"	\N	MCQ	{0,1.3418147755}	-1.0445557768	2026-01-22 23:07:51.989327	2026-01-23 11:40:34.56634	operational
61	tech	Data Structures / Complexity	What is the space complexity for deleting a linked list?	["O(1)", "O(n)", "Either O(1) or O(n)", "O(log n)"]	"O(1)"	https://s3.amazonaws.com/fuseclassroom-resources-prod/quiz/image/60c84a9ac0f08d0098f132ce/1743755867074.png	MCQ	{0,1.5939278479}	-0.0753287693	2026-01-22 23:07:51.989327	2026-01-23 11:40:34.56634	operational
62	tech	Algorithms / Search	Which of the following algorithm always manages to reach the final goal state with the least cost path?	["Breadth-First Search", "Modest Search", "A* Search", "Greedy Search"]	"A* Search"	\N	MCQ	{0,0.9781856845}	-0.5322294249	2026-01-22 23:07:51.99033	2026-01-23 11:40:34.56634	operational
63	tech	Algorithms / Binary Search	You need to efficiently find a specific record in a large sorted database. Which algorithm would you use?	["Linear Search", "Efficient Bubble Search", "Binary Search", "Insertion Sort"]	"Binary Search"	\N	MCQ	{0,1.6201805562}	-1.1726522764	2026-01-22 23:07:51.99033	2026-01-23 11:40:34.56634	operational
64	math	Logic / Pattern Recognition	What is the next number in this sequence of numbers 21,13,34,47,71,18, ?	["81", "85", "89", "91"]	"89"	\N	MCQ	{0.2269370567,0}	-1.9574323156	2026-01-22 23:07:51.991328	2026-01-23 11:40:34.56634	operational
65	tech	Machine Learning / Research Comprehension	We present a novel neural architecture, Sparse Attentive Feature Aggregation (SAFA), designed to enhance feature representation in high-dimensional image data. SAFA utilizes a sparse attention mechanism, focusing on salient image regions while minimizing computational overhead. This is achieved through a learnable gating function that dynamically selects relevant feature channels. By applying a localized attention kernel, SAFA aggregates contextual information within these salient regions, leading to improved object detection and segmentation performance. Experiments on benchmark datasets demonstrate that SAFA outperforms existing attention mechanisms, particularly in scenarios with complex object occlusions and varying illumination conditions.How does SAFA minimize computational overhead?	["By using a dense localized attention mechanism.", "By applying a sparse attention mechanism.", "By increasing the number of feature channels through selection.", "By simply applying the problem in complex object occlusion and varying illumination condition"]	"By applying a sparse attention mechanism."	\N	MCQ	{0,0.7302457251}	-0.0214105369	2026-01-22 23:07:51.991328	2026-01-23 11:40:34.56634	operational
66	tech	Logic / Reasoning	Determine the tribe of each islander.	["Truth-tellers: B  Liars: A, C", "Truth-tellers: A,B  Liars: C", "Truth-tellers: A  Liars: B, C", "Truth-tellers: A,C  Liars: B"]	"Truth-tellers: A,C  Liars: B"	\N	MCQ	{0,0.611417273}	-0.5135583077	2026-01-22 23:07:51.992329	2026-01-23 11:40:34.56634	operational
67	tech	Logic / Puzzles	Puzzle	["1", "2", "3", "4", "5", "6"]	"2"	https://s3.amazonaws.com/fuseclassroom-resources-prod/quiz/image/60c84a9ac0f08d0098f132ce/1743755967770.png	MCQ	{0,0.1983431381}	-0.4115142302	2026-01-22 23:07:51.992329	2026-01-23 11:40:34.56634	operational
68	tech	Python / List Comprehension	The list all_numbers contains numbers from 1 to 100. Which of the following code creates a new list even_numbers that contains all even numbers filtered from the list all_numbers.	["even_numbers = [i for i in all_numbers if i%2==2]", "even_numbers = [i for i in all_numbers if i%2==1]", "even_numbers = [i for i in all_numbers if i%2==0]", "even_numbers = [i for i in all_numbers if i%2==0.5]"]	"even_numbers = [i for i in all_numbers if i%2==0]"	\N	MCQ	{0,1.4129730772}	-2.2865864729	2026-01-22 23:07:51.992329	2026-01-23 11:40:34.56634	operational
69	tech	Python / Exception Handling	What is the output of the following code snippet.\ny = 0\ntry:\nresult = x/y\nprint (result)\nexcept ZeroDivisionError:\nprint("Division by zero is not allowed.")\nexcept NameError:\nprint("The variables is/are not defined.")\nexcept:\nprint("Error occurred during division")	["Division by zero is not allowed.", "The variables is/are not defined.", "Error occurred during division.", "Syntax error."]	"The variables is/are not defined."	https://s3.amazonaws.com/fuseclassroom-resources-prod/quiz/image/60c84a9ac0f08d0098f132ce/1743756894836.png	MCQ	{0,0.4990635759}	1.2754688411	2026-01-22 23:07:51.992329	2026-01-23 11:40:34.56634	operational
2	math	Linear Algebra / Matrix Rank	A sensor network uses a matrix A to represent signal transformations. If the rank of A is less than the number of sensors, what does this imply?	["The sensor network is perfectly calibrated.", "Some sensor signals are linearly dependent.", "The sensor network can capture all possible signals.", "The sensor network is overdetermined."]	"Some sensor signals are linearly dependent."	\N	MCQ	{1.9802515324,0}	-0.6875646303	2026-01-22 23:07:51.96377	2026-01-23 11:40:34.56634	operational
3	math	Linear Algebra / Orthogonality	An acoustic engineer is designing a noise-canceling system.  They decompose a sound wave into orthogonal components.  What does the orthogonality of these components signify in terms of the sound waves?	["The components have the same frequency.", "The components are linearly dependent.", "The components represent independent, non-overlapping sound sources.", "The components have the same amplitude."]	"The components represent independent, non-overlapping sound sources."	\N	MCQ	{1.1449109143,0}	-0.6528719376	2026-01-22 23:07:51.964806	2026-01-23 11:40:34.56634	operational
4	math	Linear Algebra / SVD	A digital image is represented as a matrix. Using Singular Value Decomposition (SVD), you find that the first few singular values capture most of the image's information. What is the practical application of this?	["Enhancing image resolution by selecting significant singular values", "Compressing the image by discarding less significant values.", "Detecting edges in the image through decomposition", "Rotating the image."]	"Compressing the image by discarding less significant values."	\N	MCQ	{1.5867942971,0}	-0.5489014647	2026-01-22 23:07:51.964806	2026-01-23 11:40:34.56634	operational
5	math	Linear Algebra / Least Squares	A sensor's readings are known to have a linear relationship with the actual values, but with some noise. You have a set of measured data points (x,y,) and want to find the best-fit line y=mx+c to calibrate the sensor. What is the goal of using least squares in this context?	["To find the exact line that passes through all data points.", "To minimize the sum of the squared differences between the measured and predicted values.", "To maximize the correlation between the measured and predicted values.", "To find the median of the measured values."]	"To minimize the sum of the squared differences between the measured and predicted values."	\N	MCQ	{1.7802717162,0}	-0.6892354505	2026-01-22 23:07:51.965807	2026-01-23 11:40:34.56634	operational
6	math	Calculus / Partial Derivatives	Given function f(x, y) = sin(x) * y ^ 2 . Compute f_{xy}	["-sin(x) * y^2", "cos(x) * 2y", "2sin(x)", "None of the above"]	"cos(x) * 2y"	https://s3.amazonaws.com/fuseclassroom-resources-prod/quiz/image/60c84a9ac0f08d0098f132ce/1743753112484.png	MCQ	{0.6429814126,0}	-0.017415994	2026-01-22 23:07:51.965807	2026-01-23 11:40:34.56634	operational
7	math	Calculus / Optimization	A company's profit P (in dollars) from selling x units of a product is given by P(x) = -0.01x^2 + 300x - 200000. How many units should the company sell to maximize profit?	["10000 units", "15000 units", "20000 units", "25000 units"]	"15000 units"	\N	MCQ	{1.6537495105,0}	-0.5152622071	2026-01-22 23:07:51.966805	2026-01-23 11:40:34.56634	operational
8	math	Calculus / Gradient Vector	For a function w=g(x,y,z)= exyz + xy┬▓, Determine the gradient vector?	["yzexyz+y┬▓, xzexyz+2xy, xyexyz", "xyexyz, xzexyz+2xy, yxexyz+y┬▓", "yxex+y┬▓, xze+2xy, xye┬▓", "-yxex+y┬▓, -xze+2xy, -xye┬▓"]	"xyexyz, xzexyz+2xy, yxexyz+y┬▓"	https://s3.amazonaws.com/fuseclassroom-resources-prod/quiz/image/60c84a9ac0f08d0098f132ce/1743753296111.png	MCQ	{1.282415977,0}	-0.0217263094	2026-01-22 23:07:51.966805	2026-01-23 11:40:34.56634	operational
9	math	Calculus / Integration	The rate of water flow into a tank is given by R(t) = 100*t liters per minute, where t is in minutes. How much water enters the tank between t = 1 and t = 5 minutes?	["1200 liters", "1500 liters", "1800 liters", "2400 liters", "2500 liters"]	"1200 liters"	\N	MCQ	{1.8286960149,0}	0.0078082688	2026-01-22 23:07:51.967797	2026-01-23 11:40:34.56634	operational
10	math	Probability / Binomial Distribution	Suppose you have a 60% chance of passing this exam and you are given 4 chances, each having similar but different questions. Assuming that each exam is independent of other, what is the probability that you will pass the majority of the time?	["0.6*0.6*0.6*0.6", "0.6*0.6*0.6*0.4", "4C3*0.6^3*0.4 + 4C4 * 0.6^4", "4C3*0.4^3*0.6 + 4C4 * 0.4^4"]	"4C3*0.6^3*0.4 + 4C4 * 0.6^4"	\N	MCQ	{1.1621567152,0}	-0.1178488846	2026-01-22 23:07:51.967797	2026-01-23 11:40:34.56634	operational
11	math	Probability / Bayes Theorem	A spam filter uses Bayes' Theorem to classify emails. Given the probability of an email being spam and the filter's accuracy, how does it update its belief about an email being spam after analyzing its content?	["It ignores the prior probability.", "It multiplies the prior probability by the likelihood of the content given spam.", "It calculates the conditional probability of the email being spam given its content.", "It ignores the probability of being spam and just takes the filter's accuracy into consideration."]	"It calculates the conditional probability of the email being spam given its content."	\N	MCQ	{0.5024499764,0}	-1.6148857315	2026-01-22 23:07:51.968806	2026-01-23 11:40:34.56634	operational
12	math	Probability / Poisson Distribution	You are tasked to create a statistical distribution based estimate for a server. If the average rate is 5 requests per minute, what is the probability of receiving exactly 7 requests in a minute?	["e^(ΓêÆ7) Γêù 7^5 / 5!", "5^7 / 7!", "e^(ΓêÆ5)Γêù5^7 / 7!", "7^5 / 5!"]	"e^(ΓêÆ5)Γêù5^7 / 7!"	\N	MCQ	{1.3436669044,0}	-0.3568847195	2026-01-22 23:07:51.968806	2026-01-23 11:40:34.56634	operational
13	math	Probability / Uniform Distribution	A continuous random variable T has a uniform distribution between 0 and 10. What is the expected value of T?	["2.5", "5", "7.5", "10"]	"5"	\N	MCQ	{1.3203035017,0}	-0.9380524659	2026-01-22 23:07:51.969797	2026-01-23 11:40:34.56634	operational
14	math	Statistics / Moments	For a standard normal distribution, what is the value of the third central moment?	["0", "1", "2", "3"]	"0"	\N	MCQ	{2.1754166112,0}	-0.0930865128	2026-01-22 23:07:51.969797	2026-01-23 11:40:34.56634	operational
15	math	Statistics / Central Limit Theorem	A large population has a mean weight of 150 lbs and a standard deviation of 20 lbs. If you take a random sample of 100 individuals, what is the approximate standard deviation of the sample mean?	["2 lbs", "20 lbs", "0.2 lbs", "15 lbs"]	"2 lbs"	\N	MCQ	{2.2033212571,0}	0.0249848052	2026-01-22 23:07:51.969797	2026-01-23 11:40:34.56634	operational
18	tech	Python / Data Types	What is the result of [1, 2, 3] + "4"	["[1, 2, 3, 4]", "[1, 2, 3, '4']", "\\"1234\\"", "A TypeError"]	"A TypeError"	\N	MCQ	{0,0.647746189}	-1.6804865578	2026-01-22 23:07:51.972777	2026-01-23 11:40:34.56634	operational
16	math	Statistics / Correlation	If X and Y are uncorrelated variable then this implies	["ThereΓÇÖs a linear relationship between X & Y", "Absence of any linear relationship between X & Y", "Absence of any quadratic or other polynomial relationship between X & Y", "The absence of logarithmic or trigonometric relationship between two variables"]	"Absence of any linear relationship between X & Y"	\N	MCQ	{1.3644552171,0}	-1.2731446478	2026-01-22 23:07:51.971166	2026-01-23 11:40:34.56634	operational
17	math	Statistics / Hypothesis Testing	A software company is running an A/B test to compare two versions of their homepage Version A (current design) and Version B (new design). After conducting the test with a sample of users, they calculate a p-value of 0.02. What does this p-value indicate about the results of the A/B test?	["There is a 2% chance that the observed user behavior would occur if the new homepage (Version B) is better than the current homepage (Version A).", "There is a 2% chance that the new homepage (Version B) is better than the current homepage (Version A).", "There is a 2% chance that the observed user behavior would occur if the current homepage (Version A) is equally effective as the new homepage (Version B)", "There is a 2% chance that the new homepage (Version B) is worse than the current homepage (Version A)."]	"There is a 2% chance that the observed user behavior would occur if the current homepage (Version A) is equally effective as the new homepage (Version B)"	\N	MCQ	{0.9379643738,0}	0.415312319	2026-01-22 23:07:51.971166	2026-01-23 11:40:34.56634	operational
20	tech	Python / Exception Handling	What is the output of the following code snippet?	["Division by zero is not allowed.", "The variables is/are not defined.", "Error occurred during division.", "Syntax error."]	"The variables is/are not defined."	https://s3.amazonaws.com/fuseclassroom-resources-prod/quiz/image/60c84a9ac0f08d0098f132ce/1743755344662.png	MCQ	{0,0.5511583018}	1.3350456238	2026-01-22 23:07:51.972777	2026-01-23 11:40:34.56634	operational
22	tech	Python / List Comprehension	What is the output of the following codenew_list = [2*x for x in range(1,5)]print(new_list)	["[0, 1, 4, 9, 16, 25]", "[2, 4, 6, 8, 10]", "[0, 2, 4, 6, 8, 10]", "[2, 4, 6, 8]"]	"[2, 4, 6, 8]"	\N	MCQ	{0,1.1338434043}	-0.5889587911	2026-01-22 23:07:51.97388	2026-01-23 11:40:34.56634	operational
23	tech	Python / Regular Expressions	You want to extract all email addresses from a webpage's HTML content. What Python module is most suitable for this task?	["Pandas", "RegEx", "Pytorch", "Requests"]	"RegEx"	\N	MCQ	{0,1.2175225491}	-0.2654863761	2026-01-22 23:07:51.97388	2026-01-23 11:40:34.56634	operational
24	tech	Python / NumPy	If Z is a NumPy array, what does the following code do?Z[(4 < Z) & (Z < 8)] *= -1	["Set all elements to -1", "Negate all elements between 4 and 8 exclusively", "Set all elements between 4 and 8 to -1", "Multiply all elements greater than 4 and less than or equal to 9 by -1"]	"Negate all elements between 4 and 8 exclusively"	\N	MCQ	{0,0.5831080746}	0.1833888582	2026-01-22 23:07:51.974786	2026-01-23 11:40:34.56634	operational
25	tech	Python / Pandas	You have a large dataset in a CSV file and need to calculate the average sales per product category. Which Pandas function would you use?	["data.filter(mean())", "data.pivot_table()", "data.groupby().mean()", "data.apply(mean())"]	"data.groupby().mean()"	\N	MCQ	{0,1.7113116705}	-1.0162914655	2026-01-22 23:07:51.974786	2026-01-23 11:40:34.56634	operational
26	tech	Python / Matplotlib	What command implies that we are making two figures side-by-side ?	["plt.subplot(2,1,1)", "plt.subplot(0,2,1)", "plt.subplot(1,2,1)", "plt.subplot(0,0,2)"]	"plt.subplot(1,2,1)"	\N	MCQ	{0,1.3734783157}	-0.314649402	2026-01-22 23:07:51.975787	2026-01-23 11:40:34.56634	operational
27	tech	Python / Package Management	Which of the following commands would you use to save the version of all the modules installed in your current environment?	["Python -m venv requirements.txt", "venv freeze >> requirements.txt", "pip --requirements >> requirements.txt", "pip freeze >> requirements.txt"]	"pip freeze >> requirements.txt"	\N	MCQ	{0,1.8265593378}	-0.355429449	2026-01-22 23:07:51.975787	2026-01-23 11:40:34.56634	operational
28	tech	Data Structures / Linked Lists	You are working with a data structure as shown below where data points are stored in nodes and each node points to the next node. What is the space complexity for deleting a point C from this data structure?	["O(1)", "O(n)", "Either O(1) or O(n)", "O(log n)"]	"O(1)"	https://s3.amazonaws.com/fuseclassroom-resources-prod/quiz/image/60c84a9ac0f08d0098f132ce/1743755867074.png	MCQ	{0,1.4303088625}	0.3141263197	2026-01-22 23:07:51.976879	2026-01-23 11:40:34.56634	operational
29	tech	Algorithms / Graph Algorithms	In a recommendation system, users and items can be represented as nodes in a graph, and their interactions (e.g., ratings, purchases) as edges. Which graph algorithm approach could be used to find similar items for a given user?	["Topological sort: Order the nodes in a directed acyclic graph (DAG) based on dependencies", "PageRank: Ranks nodes based on the number and quality of incoming links", "Graph clustering/community detection: Groups nodes into clusters based on their connectivity", "Depth-First Search (DFS): Traverses a graph by exploring as far as possible along each branch before backtracking"]	"Graph clustering/community detection: Groups nodes into clusters based on their connectivity"	\N	MCQ	{0,0.9359149932}	-0.4333477968	2026-01-22 23:07:51.976879	2026-01-23 11:40:34.56634	operational
30	tech	Data Structures / Stack	A web browser maintains a history of pages visited by the user. When the user clicks the "Back" button, the browser loads the most recently visited page. Which data structure would be best suited to implement this functionality?	["Stack", "Queue", "Hash", "Heap"]	"Stack"	\N	MCQ	{0,1.4793064376}	-1.3531587697	2026-01-22 23:07:51.976879	2026-01-23 11:40:34.56634	operational
31	tech	Algorithms / Sorting	A beginner programmer is tasked with implementing a sorting algorithm to arrange a small list of numbers in ascending order. She implemented a simple sorting algorithm that repeatedly compares the adjacent elements in a list and swaps them if they are out of order, continuing until the list is fully sorted. What is this algorithm called?	["Nearest neighbor Sort", "Quick Sort", "Bubble sort", "Insertion sort"]	"Bubble sort"	\N	MCQ	{0,1.1623327837}	-0.8683036182	2026-01-22 23:07:51.976879	2026-01-23 11:40:34.56634	operational
32	tech	Git / Version Control	In git, which of the following commands (in sequence)  are used when we want to reflect a change of file from the local working directory to the staging area and finally to the repository?	["git add -> git commit", "git reset -> git add", "git commit -> git push", "git merge -> git push"]	"git add -> git commit"	\N	MCQ	{0,1.0627920165}	-0.0187649601	2026-01-22 23:07:51.977863	2026-01-23 11:40:34.56634	operational
33	tech	Software Engineering / SDLC	In which phase of SDLC, the cost of changes is least?	["Early Stage of Requirement Analysis.", "At the last stage of implementation.", "After completion of the project.", "At the testing phase."]	"Early Stage of Requirement Analysis."	\N	MCQ	{0,1.8369521566}	-1.1863411136	2026-01-22 23:07:51.977863	2026-01-23 11:40:34.56634	operational
34	tech	Database / Relational Design	When designing a relational database, what is the primary purpose of defining a "primary key"?	["To uniquely identify each record within a table.", "To uniquely identify each record within a table.", "To generate unique numbers for each instance", "To store large amounts of text data."]	"To uniquely identify each record within a table."	\N	MCQ	{0,0.2320851633}	-3.414874036	2026-01-22 23:07:51.977863	2026-01-23 11:40:34.56634	operational
35	tech	Database / SQL	The given Query can also be replaced with_______SELECT name, course_id  FROM instructor, teaches  WHERE instructor_ID= teaches_ID;	["Select name,course_id from teaches,instructor where instructor_id=course_id;", "Select name, course_id from instructor natural join teaches;", "Select name, course_id from instructor;", "Select course_id from instructor join teaches;"]	"Select name, course_id from instructor natural join teaches;"	\N	MCQ	{0,0.8930977305}	-0.691503707	2026-01-22 23:07:51.978869	2026-01-23 11:40:34.56634	operational
36	tech	Computer Architecture / GPU	GPUs have 100s of smaller cores that enable it to process a large amount of data in parallel. Which of the following parallel paradigms does it follow?	["Single Instruction Single Data (SISD)", "Single Instruction Multiple Data (SIMD)", "Multiple Instruction Single Data (MISD)", "Multiple Instruction Multiple Data (MIMD)"]	"Single Instruction Multiple Data (SIMD)"	\N	MCQ	{0,1.8593832665}	-0.211183686	2026-01-22 23:07:51.978869	2026-01-23 11:40:34.56634	operational
39	math	Logic / Deductive Reasoning	"Three individuals, X, Y, and Z, are standing in a line, facing forward. Each is wearing a hat that is either red or blue. They cannot see their own hat.Someone announces, 'At least one of you is wearing a red hat.'X says, 'I do not know the color of my hat.'Y says, 'I do not know the color of my hat.'Z then says, 'I know the color of my hat.'What color is Z's hat,	["Red", "Blue"]	"Red"	\N	MCQ	{0.5359312616,0}	-2.0625867156	2026-01-22 23:07:51.979874	2026-01-23 11:40:34.56634	operational
40	math	Logic / Puzzles	Guess the correct answer.	["A", "B", "C", "D", "E", "F", "G", "H"]	"A"	https://s3.amazonaws.com/fuseclassroom-resources-prod/quiz/image/60c84a9ac0f08d0098f132ce/1743755967770.png	MCQ	{0.2883541278,0}	3	2026-01-22 23:07:51.979874	2026-01-23 11:40:34.56634	operational
41	math	Linear Algebra / Graphics	A 3D graphics programmer is calculating the diffuse reflection of light from a surface.  This involves projecting the light vector onto the surface normal.  If the projection of the light vector onto the normal vector is the zero vector, what does this imply?	["The light source is directly above (perpendicular) the surface.", "The light source is behind the surface.", "The light source is grazing the surface (parallel to the surface).", "The surface is perfectly reflective."]	"The light source is grazing the surface (parallel to the surface)."	\N	MCQ	{0.7422141098,0}	0.3328327152	2026-01-22 23:07:51.979874	2026-01-23 11:40:34.56634	operational
42	math	Linear Algebra / Eigenvectors	Eigenvectors of a matrix represent	["(a) The matrix's inverse.", "(b) The matrix's determinant.", "(c) Directions along which the linear transformation acts by scaling.", "(d) The matrix's transpose times its inverse."]	"(c) Directions along which the linear transformation acts by scaling."	\N	MCQ	{1.9060192092,0}	-0.9359388536	2026-01-22 23:07:51.980876	2026-01-23 11:40:34.56634	operational
43	math	Probability / Expected Value	A lottery ticket costs $2. There's a 1% chance of winning $100, a 5% chance of winning $10, and a 94% chance of winning nothing. Let X be the random variable representing your profit. What is the expected profit from buying one ticket?	["-$0.50", "$0", "$0.50", "$1.00"]	"-$0.50"	\N	MCQ	{1.9981647936,0}	-0.0442023179	2026-01-22 23:07:51.980876	2026-01-23 11:40:34.56634	operational
44	math	Statistics / Central Limit Theorem	A manufacturing process produces items with varying dimensions. The Central Limit Theorem is used to analyze the distribution of sample means. Why is this useful?	["To determine the exact dimensions of each item.", "To estimate the population mean and confidence intervals.", "To eliminate all variations in dimensions.", "To calculate the sample variance."]	"To estimate the population mean and confidence intervals."	\N	MCQ	{1.4357557705,0}	-0.7688064014	2026-01-22 23:07:51.98179	2026-01-23 11:40:34.56634	operational
45	tech	Data Structures / Queue	In an airport baggage claim system, luggage is processed in the order it arrives. Each piece of luggage is loaded onto a conveyor belt, and the first piece loaded is the first to be delivered to passengers.  Which data structure would be best suited to model this luggage delivery system?	["Stack", "Queue", "Heap", "Priority Queue"]	"Queue"	\N	MCQ	{0,1.1558545493}	-1.8319167998	2026-01-22 23:07:51.982307	2026-01-23 11:40:34.56634	operational
46	tech	Python / Data Visualization	A data scientist needs to visualise clusters or groups of data points of six dimensional data. He uses a certain dimensionality reduction technique to reduce the dimensions to two. Which of the following would be the best visualisation method in order to identify the visual clusters in the reduced dataset and identify potential outliers?	["Density Plot", "Bar Chart", "Heatmap", "Scatter Plot"]	"Scatter Plot"	\N	MCQ	{0,1.2224181093}	-0.7367309395	2026-01-22 23:07:51.982307	2026-01-23 11:40:34.56634	operational
47	tech	Python / String Operations	What is the output of the following?\n\ns = "we are humans"\nprint(tuple(s.split()))	["('we', 'are', 'humans')", "(we, are, humans)", "('we', 'humans')", "'we are humans'"]	"('we', 'are', 'humans')"	\N	MCQ	{0,1.073403865}	0.1804622217	2026-01-22 23:07:51.983316	2026-01-23 11:40:34.56634	operational
48	tech	Statistics / Hypothesis Testing	A company wants to determine if a new website design increases conversion rates. What statistical tool is most appropriate for this analysis?	["Linear regression.", "Hypothesis testing (e.g., t-test).", "Analysis of variance (ANOVA).", "Principal component analysis."]	"Hypothesis testing (e.g., t-test)."	\N	MCQ	{0,1.6710901152}	-0.5187947735	2026-01-22 23:07:51.983316	2026-01-23 11:40:34.56634	operational
51	math	Calculus / Derivatives	The derivative of x^2 * ln(x) is:	["2x ln(x) + x", "x^2 ln(x)", "2x ln(x) - x", "ln(x) + x^2"]	"2x ln(x) + x"	\N	MCQ	{0.8778309069,0}	-1.4519209058	2026-01-22 23:07:51.985327	2026-01-23 11:40:34.56634	operational
38	tech	Machine Learning / Research Comprehension	In this sentence, ΓÇ£circumventsΓÇ¥ means that the proposed method avoids or overcomes the common problems associated with standard gradient descent, rather than directly confronting them, by adjusting the learning rate dynamically.	["Completely replaces", "Avoids or bypasses", "Enhances or Amplifies", "Reduces or Attenuate"]	"Avoids or bypasses"	\N	MCQ	{0,1.4506081683}	-0.2454041652	2026-01-22 23:07:51.979874	2026-01-29 23:37:36.531403	operational
49	math	Statistics / Least Squares	What is the primary objective of the least squares method?	["Maximize the accuracy of least squares prediction", "Minimize the sum of squared differences between observed and predicted values", "Maximize the correlation between variables", "Minimize the determinant of the design matrix"]	"Minimize the sum of squared differences between observed and predicted values"	\N	MCQ	{1.9937804052,0}	-1.1009697928	2026-01-22 23:07:51.984327	2026-01-23 11:40:34.56634	operational
50	math	Linear Algebra / Rotation	 A robotic arm's end effector is at position v = [3, 4]^T in a 2D plane. \nTo rotate the arm's end effector by pi/2 radians counterclockwise using a rotation matrix R, \nwhat is the new position v' of the end effector after this rotation?	["[4,  ΓêÆ3ΓÇï]^T", "[ΓêÆ4, 3ΓÇï]^T", "[ΓêÆ3, 4ΓÇï]^T", "[3, ΓêÆ4ΓÇï]^T"]	"[ΓêÆ4, 3ΓÇï]^T"	\N	MCQ	{0.5477780238,0}	0.1862834582	2026-01-22 23:07:51.984327	2026-01-23 11:40:34.56634	operational
52	tech	Machine Learning / Neural Networks	During the training of a neural network, you use gradient descent to minimize a loss function. What does this process involve?	["Finding the integral of the loss function", "Finding the points where the derivative of the loss function is zero.", "Approximating the loss function with a linear function.", "Randomly changing the model's parameters."]	"Finding the points where the derivative of the loss function is zero."	\N	MCQ	{0,0.7615889384}	-0.4454496391	2026-01-22 23:07:51.985327	2026-01-23 11:40:34.56634	operational
53	math	Calculus / Integration	A rain gauge measures the rainfall rate r(t)= 2*t mm/hour, where t is time in hours. What is the total rainfall (in mm) from t=0 to t=3 hours?	["6 mm", "9 mm", "12 mm", "18 mm"]	"9 mm"	\N	MCQ	{0.8599067666,0}	-0.0711635708	2026-01-22 23:07:51.986326	2026-01-23 11:40:34.56634	operational
54	math	Probability / Conditional Probability	In a certain locality, 6% of men have diabetes and 3% of women have diabetes. The total population is divided in the ratio 32 in favour of women. If a person is selected at random from among all those with diabetes, what is the probability that the person is a man?	["4/7", "3/7", "5/9", "2/3"]	"4/7"	\N	MCQ	{0.7853317067,0}	0.5351853496	2026-01-22 23:07:51.986326	2026-01-23 11:40:34.56634	operational
55	math	Statistics / Standard Deviation	WhatΓÇÖs the Standard deviation for the following sample data 2,4,6,8,10 and 12	["4.42", "2.42", "3.42", "5.42"]	"3.42"	\N	MCQ	{1.1590210987,0}	-1.0114444791	2026-01-22 23:07:51.986326	2026-01-23 11:40:34.56634	operational
102	math	calculus/derivatives	What is the derivative of a function?	["The area under the curve of the function", "The average rate of change over a given interval", "The limit of the difference quotient as h approaches zero", "The slope of the tangent line at a single point"]	"The limit of the difference quotient as h approaches zero"	\N	MCQ	{0,0}	0	2026-01-28 23:54:47.406124	2026-01-30 00:03:37.615127	pretest
70	tech	Machine Learning / Research Comprehension	Consider a sentence from an ML paper ΓÇ£Our approach circumvents the pitfalls of conventional gradient descent by adaptively modulating the learning rate.ΓÇ¥ What does ΓÇ£circumventsΓÇ¥ imply in this context?	["Completely replaces", "Avoids or bypasses", "Enhances or Amplifies", "Reduces or Attenuate"]	"Avoids or bypasses"	\N	MCQ	{0,1.114421932}	-0.3672380317	2026-01-22 23:07:51.993836	2026-01-23 11:40:34.56634	operational
81	tech	Data Structures / Complexity	Which data structure is used to store a collection of unique values?	["Stack", "Queue", "Linked List", "Set"]	"Set"	\N	MCQ	{0,0.8258714783397627}	-2.0421320347194722	2026-01-22 23:07:51.996316	2026-01-23 11:40:34.56634	operational
223	math	Calculus / Integration	Evaluate the integral of the function f(x) = sin(x) / (1 + cos^2(x)) from 0 to pi/2.	["tan(x) | from 0 to pi/2", "╧Ç/4", "log(1 + ΓêÜ2)", "╧Ç/2"]	"╧Ç/2"	\N	MCQ	{1.7100248429266576,0}	2.0259751671862127	2026-01-22 23:07:51.995087	2026-01-23 11:40:34.56634	operational
108	math	statistics/inference	What type of statistical inference involves making conclusions about a population based on a sample?	["Descriptive statistics", "Inferential statistics", "Probability theory", "Data visualization"]	"Inferential statistics"	\N	MCQ	{0,0}	0	2026-01-28 23:57:19.008633	2026-01-29 23:57:32.411739	pretest
109	tech	algorithms/sorting	Consider a hybrid sorting algorithm that combines elements of Merge Sort and Insertion Sort. If the input array has a length of n, and the Merge Sort and Insertion Sort phases are executed in a way that the Merge Sort phase is applied to the first n/2 elements and the Insertion Sort phase is applied to the last n/2 elements, what is the time complexity of this hybrid sorting algorithm?	["O(n^3)", "O(n^2)", "O(n log log n)", "O(n log n)"]	"O(n log n)"	\N	MCQ	{0,0}	0	2026-01-29 00:05:20.921115	2026-01-29 23:57:58.923162	pretest
107	math	statistics/inference	What is the primary goal of confidence intervals in statistics?	["To estimate the population mean with a certain level of precision", "To determine the sample size needed for a study", "To test a hypothesis about a population parameter", "To calculate the standard deviation of a sample"]	"To estimate the population mean with a certain level of precision"	\N	MCQ	{0,0}	0	2026-01-28 23:57:19.008633	2026-01-29 23:58:40.941933	pretest
106	math	statistics/inference	What does a p-value represent in hypothesis testing?	["The probability of observing the data given that the null hypothesis is true", "The probability that the null hypothesis is true", "The probability that the alternative hypothesis is true", "The probability of rejecting the null hypothesis"]	"The probability of observing the data given that the null hypothesis is true"	\N	MCQ	{0,0}	0	2026-01-28 23:57:19.008633	2026-01-29 23:59:31.749641	pretest
105	math	statistics/inference	What does the term 'parameter' refer to in statistics?	["A numerical value calculated from the sample data", "A numerical value that summarizes the entire population", "A statistical measure used to summarize the sample data", "A type of statistical test used to compare samples"]	"A numerical value that summarizes the entire population"	\N	MCQ	{0,0}	0	2026-01-28 23:57:19.008633	2026-01-30 00:00:00.264937	pretest
104	math	statistics/inference	A statistical inference is a conclusion drawn from a sample of data. What is the primary purpose of statistical inference?	["To compare the means of two or more samples", "To describe the characteristics of a sample", "To make a prediction about a population", "To determine the probability of an event occurring"]	"To make a prediction about a population"	\N	MCQ	{0,0}	0	2026-01-28 23:57:19.008633	2026-01-30 00:00:26.69526	pretest
101	math	calculus/derivatives	What is the definition of a derivative in calculus?	["The derivative of a function is the slope of the line tangent to the function's graph at a given point.", "The derivative of a function is the area under the function's graph.", "The derivative of a function is the limit of the difference quotient as the change in x approaches zero.", "The derivative of a function is the average rate of change of the function over a given interval."]	"A"	\N	MCQ	{0,0}	0	2026-01-28 23:54:47.406124	2026-01-29 12:17:43.254285	pretest
100	math	calculus/derivatives	Given a function f(x) = e^(-x^2) * sin(x), find the derivative of f(x) using the product rule and chain rule, and then evaluate it at x = ╧Ç/4.	["f'(x) = e^(-x^2) * (cos(x) + 2x * sin(x)) at x = ╧Ç/4", "f'(x) = e^(-x^2) * (cos(x) - x * sin(x)) at x = ╧Ç/4", "f'(x) = e^(-x^2) * (cos(x) - 2x * sin(x)) at x = ╧Ç/4", "f'(x) = e^(-x^2) * (cos(x) + x * sin(x)) at x = ╧Ç/4"]	"f(x) = e^(-x^2) * (cos(x) - 2x * sin(x)) at x = ╧Ç/4"	\N	MCQ	{0,0}	0	2026-01-28 23:54:47.406124	2026-01-29 23:52:47.949439	pretest
112	tech	algorithms/sorting	Given a sequence of n integers, where n is even, determine the time and space complexity of the following algorithm. The algorithm first applies a stable sorting algorithm (with a time complexity of O(n log n)) and then removes every other element from the sorted sequence, starting from the first element. Which of the following is the time complexity of this algorithm?	["O(n log n) due to the sorting step, then O(n/2) due to the removal step, resulting in O(n log n) overall", "O(n log n) due to the sorting step, then O(n log n) due to the removal step, resulting in O(n log n log n)", "O(n log n) due to the sorting step, but the removal step has no effect on the overall time complexity, resulting in O(n log n)", "O(n log n) due to the sorting step, then O(n/2) due to the removal step, resulting in O(n) overall"]	"O(n log n) due to the sorting step, then O(n/2) due to the removal step, resulting in O(n) overall"	\N	MCQ	{0,0}	0	2026-01-29 00:05:20.921115	2026-01-29 23:55:30.295267	pretest
111	tech	algorithms/sorting	Given an array of integers that is partially sorted in ascending order, but with a certain number of elements out of order, what is the time complexity of the Heapsort algorithm when applied to this array?	["O(n log k), where n is the length of the array and k is the number of elements out of order", "╬⌐(n log n), where n is the length of the array", "O(n log k), where n is the length of the array and k is the length of the input array", "O(n log n), where n is the length of the array"]	"╬⌐(n log n), where n is the length of the array"	\N	MCQ	{0,0}	0	2026-01-29 00:05:20.921115	2026-01-29 23:56:27.664875	pretest
110	tech	algorithms/sorting	What is the main goal of the Bubble Sort algorithm?	["To compare and swap adjacent elements in a list until it is sorted", "To find the smallest and largest elements in a list", "To sort a list by dividing it into smaller chunks", "To insert each element into its correct position in a sorted list"]	"To compare and swap adjacent elements in a list until it is sorted"	\N	MCQ	{0,0}	0	2026-01-29 00:05:20.921115	2026-01-30 00:05:36.899359	pretest
1	math	Linear Algebra / Transformations	The orthogonal basis vectors ├« and ─╡ are transformed by a linear transformation T into a new set of orthogonal basis vectors 3├« ΓêÆ 2─╡ and 4├« + 6─╡, respectively. Find the transformation matrix T.	["[[3, -4], [2, 6]]", "[[3, 4], [-2, 6]]", "[[3, -2], [4, 6]]", "[[3, -2], [-4, 6]]"]	"[[3, 4], [-2, 6]]"	https://s3.amazonaws.com/fuseclassroom-resources-prod/quiz/image/60c84a9ac0f08d0098f132ce/1743752386776.png	MCQ	{0.7523154641,0}	-0.4404106655	2026-01-22 23:07:51.954206	2026-01-29 23:39:29.342153	operational
21	tech	Python / Operator Overloading	Which function overloads the > operator?	["__more__()", "_greater_than()", "__gt__()", "__ge__()", "_gt_()"]	"__gt__()"	\N	MCQ	{0,1.4937741818}	-0.273045648	2026-01-22 23:07:51.97388	2026-01-23 11:40:34.56634	operational
37	math	Logic / Pattern Recognition	What is the next number in this sequence of numbers 77,49,36,18, __ ?	["11", "7", "8", "3"]	"8"	\N	MCQ	{0.6393896601,0}	0.3779074038	2026-01-22 23:07:51.978869	2026-01-23 11:40:34.56634	operational
57	tech	Python / Programming	Which of the following are keywords in python ?	["yield", "assert", "with", "next"]	["yield", "assert", "with"]	\N	MSQ	{0,1.6504120282}	0.4022609806	2026-01-22 23:07:51.987325	2026-01-23 11:40:34.56634	operational
152	tech	Software Engineering / SDLC	In the context of Agile software development, which of the following is the primary goal of the 'Definition of Done' (DoD)?	["To establish a shared understanding of what it means for a task to be completed", "To clearly define the scope of work for each iteration", "To prioritize features based on business value", "To create a detailed project schedule"]	"To establish a shared understanding of what it means for a task to be completed"	\N	MCQ	{0,2.539088657437951}	1.7322225659483266	2026-01-22 23:07:51.995087	2026-01-23 11:40:34.56634	operational
189	math	Linear Algebra / Least Squares	Consider a set of data points in a least squares problem that lies on a plane, but the normal vector to the plane is not orthogonal to any of the column vectors of the design matrix A. Which of the following is true?	["There exists a unique solution to the normal equations A^T A x = A^T b.", "The system is inconsistent, and there is no solution.", "The normal equations A^T A x = A^T b must be modified to A^T A x = A^T b + c for some vector c.", "The system is consistent but may have infinitely many solutions."]	"The system is consistent but may have infinitely many solutions."	\N	MCQ	{0.8570611725854633,0}	1.7861119115084292	2026-01-22 23:07:51.999838	2026-01-23 11:40:34.56634	operational
195	math	Linear Algebra / Eigenvectors	What is an eigenvector of a matrix?	["A vector that, when multiplied by the matrix, results in a vector with the same direction but different magnitude.", "A vector that, when multiplied by the matrix, results in the zero vector.", "A nonzero vector that, when multiplied by the matrix, results in a scaled version of itself.", "A vector that, when multiplied by the matrix, results in a vector with a different direction and magnitude."]	"A nonzero vector that, when multiplied by the matrix, results in a scaled version of itself."	\N	MCQ	{0.9836561560593442,0}	-1.1979189900864209	2026-01-22 23:07:51.995087	2026-01-23 11:40:34.56634	operational
196	math	Linear Algebra / Eigenvectors	An eigenvector of a square matrix A is a non-zero vector v such that Av = ╬╗v. If v is an eigenvector of A, what does ╬╗ represent?	["A column vector in the matrix A", "A scalar value that the matrix A multiplies v by", "A row vector in the matrix A", "An identity matrix"]	"A scalar value that the matrix A multiplies v by"	\N	MCQ	{0.7826558377227741,0}	-0.5443696376912266	2026-01-22 23:07:51.996316	2026-01-23 11:40:34.56634	operational
204	math	Linear Algebra / Matrix Rank	What is the rank of a square matrix if it has no zero rows or columns?	["The rank is equal to the number of rows in the matrix", "The rank is equal to the number of non-zero elements in the matrix", "The rank is equal to the number of columns in the matrix", "The rank is always 1"]	"The rank is equal to the number of columns in the matrix"	\N	MCQ	{2.2886938676801356,0}	-1.3561546130636666	2026-01-22 23:07:51.997331	2026-01-23 11:40:34.56634	operational
208	math	Calculus / Gradient Vector	Find the gradient vector of the function f(x, y) = 3x^2 + 2y^2 at the point (1, 2).	["Γêçf(1, 2) = (3, 4)", "Γêçf(1, 2) = (12, 8)", "Γêçf(1, 2) = (9, 6)", "Γêçf(1, 2) = (6, 12)"]	"Γêçf(1, 2) = (12, 8)"	\N	MCQ	{2.3497450218413882,0}	0.1624363931337082	2026-01-22 23:07:51.999838	2026-01-23 11:40:34.56634	operational
209	math	Calculus / Derivatives	Given the function f(x) = (2x^2 + 3x - 5) / (x^2 - 4), find the derivative of f(x) at the point x = 2, where f'(2) = A/(x^2 - 4)^2. What is the value of A?	["17/25", "23/25", "13/25", "11/25"]	"13/25"	\N	MCQ	{0.8705709968884154,0}	2.7202687474957057	2026-01-22 23:07:51.998316	2026-01-23 11:40:34.56634	operational
234	math	Logic / Puzzles	Five houses are located in a row containing different numbers of books, different numbers of computers, and different numbers of pianos. Each house has a different number of books, a different number of computers, and a different number of pianos.	["The house with 10 computers is located next to the house with 200 books, and the house with 25 pianos is located next to the house with 15 computers.", "The house with 200 books is located next to the house with 5 computers, and the house with 15 pianos is located next to the house with 300 books.", "The house with 5 computers is located next to the house with 15 pianos, and the house with 300 books is located next to the house with 20 computers.", "The house with 25 pianos is located next to the house with 10 computers, and the house with 200 books is located next to the house with 5 pianos."]	"The house with 10 computers is located nexat to the house with 200 books, and the house with 25 pianos is located next to the house with 15 computers."	\N	MCQ	{0.3962451666580306,0}	1.3349486716793573	2026-01-22 23:07:52.000851	2026-01-23 11:40:34.56634	operational
254	math	Probability / Poisson Distribution	A call center receives an average of 10 customer calls per hour. If the probability of a customer call being an emergency is 0.1, and the call center needs to determine the probability that at least 5 calls are emergency calls within a 2-hour period, what is the probability of this event?	["The probability of at least 5 emergency calls within a 2-hour period is approximately 0.245", "The probability of at least 5 emergency calls within a 2-hour period is approximately 0.082", "The probability of at least 5 emergency calls within a 2-hour period is approximately 0.382", "The probability of at least 5 emergency calls within a 2-hour period is approximately 0.921"]	"The probability of at least 5 emergency calls within a 2-hour period is approximately 0.245"	\N	MCQ	{0.6892458614890682,0}	1.23688152529107	2026-01-22 23:07:52.000851	2026-01-23 11:40:34.56634	operational
261	math	Probability / Uniform Distribution	For a uniform distribution with a minimum value of X and a maximum value of Y, where X and Y are random variables, what is the probability that a randomly selected value from this distribution falls within the interval [0, 3]? Given that Y = 10 and X is uniformly distributed over [0, 10].	["The probability is calculated as (3 - X) / (Y - X) since X is a random variable.", "The probability is calculated as (3 - 0) / (10 - X) = 3 / (10 - X).", "The probability is calculated as (3 - X) / 10 since X is a random variable.", "The probability is calculated as (3 - 0) / (10 - 0) = 3/10."]	"The probability is calculated as (3 - 0) / (10 - 0) = 3/10."	\N	MCQ	{1.1050708548042527,0}	1.7104302979488533	2026-01-22 23:07:51.994363	2026-01-23 11:40:34.56634	operational
268	math	Statistics / Least Squares	A researcher wants to model the relationship between the number of hours studied and exam scores. Using least squares, we find that the regression equation is y = 2x + 3. What is the expected score for a student who studied 5 hours?	["19", "15", "17", "13"]	"13"	\N	MCQ	{0.5442239779029087,0}	0.5972146630308689	2026-01-22 23:07:51.997331	2026-01-23 11:40:34.56634	operational
282	math	Statistics / Correlation	What does a positive correlation coefficient indicate in a dataset?	["That there is no relationship between variables.", "That variables are moving in the same direction.", "That variables are moving in opposite directions.", "That the relationship is not significant."]	"That variables are moving in the same direction."	\N	MCQ	{1.2120416177507494,0}	-0.5693817049766464	2026-01-22 23:07:51.997331	2026-01-23 11:40:34.56634	operational
313	tech	Python / Data Visualization	A Python programmer wants to create an interactive dashboard using Plotly. They decide to use a combination of Plotly Express and Dash. What is the main reason for using both Plotly Express and Dash in this scenario?	["To create a complex layout with multiple subplots", "To leverage the performance benefits of Plotly Express and the interactivity features of Dash", "To create a simple line chart and a scatter plot with hover-over text", "To use a specific plot type that is only available in Plotly"]	"To leverage the performance benefits of Plotly Express and the interactivity features of Dash"	\N	MCQ	{0,1.119625487847175}	1.628705741900671	2026-01-22 23:07:51.998316	2026-01-23 11:40:34.56634	operational
321	tech	Python / String Operations	Given a string 'Hello World', how can you extract the word 'World' from the string, excluding the first 5 characters?	["string = 'Hello World'; word = string[6:11]", "string = 'Hello World'; word = string[5:10]", "string = 'Hello World'; word = string[-5:10]", "string = 'Hello World'; word = string[5:15]"]	"string = 'Hello World'; word = string[5:10]"	\N	MCQ	{0,0.9980482433490144}	0.13080619940772786	2026-01-22 23:07:51.999838	2026-01-23 11:40:34.56634	operational
326	tech	Programming / OOP	Given a class hierarchy where Animal is the parent class and Dog, Cat, and Bird are child classes, which of the following statements about the inheritance of methods is CORRECT?	["If a child class overrides a method, all other child classes that inherit from it will automatically inherit the override.", "When you override a method in a child class, you can still invoke the parent class's method using 'super()'.", "You can call a method from a child class in a parent class using 'this'.", "If a method is defined in a parent class with the 'final' keyword, it cannot be overridden in any child classes."]	"When you override a method in a child class, you can still invoke the parent class's method using 'super()'."	\N	MCQ	{0,1.4586812619399057}	1.4950605566077662	2026-01-22 23:07:51.994363	2026-01-23 11:40:34.56634	operational
366	tech	Programming / OOP	Which of the following are ways to implement dependency injection in a Python class?	["Using a factory function to create objects", "Using a constructor with parameters", "Using a singleton pattern to ensure a single instance", "Using a setter method to inject dependencies"]	["Using a constructor with parameters", "Using a setter method to inject dependencies"]	\N	MSQ	{0,1.72}	0.68	2026-01-22 23:07:52.000851	2026-01-23 11:40:34.56634	operational
369	tech	Python / Lists	Given a list of students with their grades, which methods can be used to sort the list in descending order by grade?	["a = sorted(a, key=lambda x: x[1], reverse=True)", "a = a.sort()", "a = a.sort(key=lambda x: x[1], reverse=True)", "a.sort(reverse=True)"]	["a = sorted(a, key=lambda x: x[1], reverse=True)", "a.sort(reverse=True)"]	\N	MSQ	{0,1.95}	1.96	2026-01-22 23:07:52.001856	2026-01-23 11:40:34.56634	operational
372	tech	Git / Version Control	What are the main purposes of the Git stash feature in version control?	["To temporarily save changes made in the working directory for later use", "To revert changes made in the previous commit", "To manage conflicts between different branches in a Git repository", "To track changes made in a specific branch without committing them"]	["To temporarily save changes made in the working directory for later use", "To track changes made in a specific branch without committing them"]	\N	MSQ	{0,1.11}	0.53	2026-01-22 23:07:52.001856	2026-01-23 11:40:34.56634	operational
\.


--
-- Data for Name: responses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.responses (response_id, session_id, question_id, question_num, user_answer, is_correct, theta_math_after, theta_tech_after, created_at) FROM stdin;
1	2	2	1	\N	\N	\N	\N	2026-01-23 00:44:04.163492
2	3	43	1	\N	\N	\N	\N	2026-01-23 00:50:08.864362
3	4	14	1	\N	\N	\N	\N	2026-01-23 00:53:03.678976
4	5	208	1	"b"	t	0.38795698541087836	0.19045194848706046	2026-01-23 00:54:05.223289
5	5	152	2	"a"	t	0.605208569707886	0.7591748338183086	2026-01-23 00:54:24.096976
6	5	19	3	"abd"	f	0.5599607859189566	0.5802338582013585	2026-01-23 00:54:50.497264
7	5	15	4	"ab"	f	0.1575438298690126	0.48350229394377026	2026-01-23 00:55:03.224398
8	5	14	5	"a"	t	0.35257574679048176	0.5265539915464195	2026-01-23 00:55:13.712664
9	5	43	6	"a"	t	0.4620223249610816	0.5474954023567359	2026-01-23 00:55:26.337572
10	5	369	7	"a,b"	f	0.4089760923891358	0.4351534739105149	2026-01-23 00:55:29.989355
11	5	366	8	"b,d"	f	0.38320363843761474	0.2710420360263033	2026-01-23 00:55:46.229029
12	5	36	9	"b"	t	0.40666209666799735	0.3845626478635069	2026-01-23 00:56:38.262838
13	5	9	10	"b"	f	0.23832571990656842	0.33982169957197045	2026-01-23 00:56:46.580529
14	5	2	11	"b"	t	0.28360469390575127	0.33561893269553794	2026-01-23 00:56:50.546871
15	5	57	12	["a", "b", "c"]	t	0.33236857852720725	0.48622676676914933	2026-01-23 00:56:54.790435
16	5	27	13	"A"	f	0.28989672088263696	0.2946525892190772	2026-01-23 00:58:08.778514
17	5	58	14	"A"	f	0.2686291616715856	0.13010991337804398	2026-01-23 00:58:26.654516
18	5	61	15	"A"	t	0.27652401594157766	0.21477591126053824	2026-01-23 00:58:32.179375
19	5	48	16	"A"	f	0.2571683862199687	0.08788260183896442	2026-01-23 00:58:32.839329
20	5	5	17	"A"	f	0.09117996034141265	0.04487179081964964	2026-01-23 00:58:33.472722
21	5	204	18	"A"	f	-0.08254182758690065	0.03735510365380281	2026-01-23 00:58:34.038688
22	5	49	19	"A"	f	-0.22937852290509655	0.005476031293417058	2026-01-23 00:58:34.650314
23	5	42	20	"A"	f	-0.3562861995454416	-0.03726461487040826	2026-01-23 00:58:35.343797
24	6	2	1	\N	\N	\N	\N	2026-01-23 01:00:07.960584
25	7	43	1	\N	\N	\N	\N	2026-01-23 01:01:10.76978
26	8	14	1	"a"	t	0.3520699084373638	0.16491567365493973	2026-01-23 10:16:15.626518
27	8	208	2	"b"	t	0.5890109701771944	0.31649545014963426	2026-01-23 10:16:34.052862
28	8	152	3	"b"	f	0.5271425230284082	0.05314062492401376	2026-01-23 10:16:54.385308
29	8	15	4	"b"	f	0.19135394455444732	-0.04960129909074734	2026-01-23 10:16:58.540065
30	8	43	5	"a"	t	0.3306334271224128	-0.04775774396140351	2026-01-23 10:17:01.482392
31	8	36	6	"b"	t	0.35582676841841926	0.19458974745339847	2026-01-23 10:17:08.582332
32	8	9	7	"b"	f	0.2009733459635793	0.1406453317305539	2026-01-23 10:17:13.778994
33	8	27	8	"c"	f	0.14915371915426076	-0.1202991808742998	2026-01-23 10:17:17.820835
34	8	2	9	"b"	t	0.21363810362796826	-0.09046524428454368	2026-01-23 10:17:23.95279
35	8	58	10	"b"	t	0.2560253960288217	0.05428472241466672	2026-01-23 10:17:35.268625
36	8	366	11	"b"	f	0.2391540183721638	-0.055529473257153274	2026-01-23 10:17:48.506676
37	8	48	12	"b"	t	0.2531699476044572	0.034637443100698884	2026-01-23 10:18:09.749676
38	8	57	13	["a", "b", "d"]	f	0.23261800975587843	-0.02142460761267205	2026-01-23 10:18:14.370091
39	8	61	14	"a"	t	0.25763889719760913	0.04662915435454774	2026-01-23 10:18:32.025198
40	8	5	15	"b"	t	0.30702233382740507	0.047301783809671906	2026-01-23 10:18:58.86043
41	8	33	16	"a"	t	0.3227273020644741	0.12403728757498625	2026-01-23 10:19:06.492739
42	8	21	17	"c"	t	0.3225017350097682	0.17567040249623636	2026-01-23 10:19:12.539863
43	8	7	18	"b"	t	0.3609582568920572	0.17096568797884	2026-01-23 10:19:20.722457
44	8	369	19	["b", "d"]	f	0.3486073750317806	0.1534245605562454	2026-01-23 10:19:26.949545
45	8	28	20	"a"	t	0.38657670578361397	0.22796577300255488	2026-01-23 10:19:47.442558
46	9	15	1	\N	\N	\N	\N	2026-01-23 11:44:30.373717
47	10	14	1	"a"	t	0.38251683315371743	0.20738436669141966	2026-01-23 11:50:30.752301
48	10	208	2	"b"	t	0.5889148365559564	0.3017724644149586	2026-01-23 11:51:33.747839
49	10	152	3	"c"	f	0.49755551413641746	0.03331789803367977	2026-01-23 11:51:53.947616
50	10	15	4	"b"	f	0.18848902730536388	-0.08980710232083719	2026-01-23 11:52:30.201967
51	10	43	5	"a"	t	0.323323364141743	-0.028887950779289052	2026-01-23 11:52:39.55285
52	10	36	6	"b"	t	0.38909354759382836	0.19353698488121474	2026-01-23 11:54:37.064083
53	10	9	7	"b"	f	0.21430590422008114	0.13860328513203868	2026-01-23 11:54:41.904474
54	10	27	8	"c"	f	0.16895097548371632	-0.10526837332045402	2026-01-23 11:54:45.288626
55	10	2	9	"c"	f	-0.00925295672436142	-0.15169693273906645	2026-01-23 11:54:52.662889
56	10	204	10	"c"	t	0.032228753956152406	-0.13175366769483	2026-01-23 11:54:56.850481
57	10	58	11	"b"	t	0.048877538443035176	0.010903561014225292	2026-01-23 11:54:58.859768
58	10	49	12	"b"	t	0.0918506475835224	0.019382785253313398	2026-01-23 11:55:05.396319
59	10	42	13	"c"	t	0.15359923229355057	0.0168209684400389	2026-01-23 11:55:12.19238
60	10	366	14	"c"	f	0.14071691098239808	-0.06009404686490791	2026-01-23 11:55:22.3866
61	10	48	15	"b"	t	0.1614890631462705	0.03470474059184446	2026-01-23 11:55:30.752835
62	10	57	16	["a", "b", "c"]	t	0.16423227917389313	0.1370362321778602	2026-01-23 11:55:38.081214
63	10	5	17	"b"	t	0.2026116773740578	0.14329085451925455	2026-01-23 11:55:50.527786
64	10	61	18	"a"	t	0.21974536774258394	0.26493019986219873	2026-01-23 11:56:17.373956
65	10	369	19	"a"	f	0.20980221072639452	0.20955985110972467	2026-01-23 11:56:24.4573
66	10	7	20	"b"	t	0.2840854802610528	0.21041181047719532	2026-01-23 11:56:30.530879
67	10	21	21	"c"	t	0.267904920297951	0.2727267243099187	2026-01-23 11:56:36.445998
68	10	19	22	"b"	f	0.25924769818773713	0.23288238905901243	2026-01-23 11:56:44.381208
69	10	28	23	"a"	t	0.2646849212407641	0.31127277046722146	2026-01-23 12:16:49.924079
70	10	4	24	"a"	f	0.17629387190957993	0.30191897906663806	2026-01-23 12:17:00.292873
71	10	38	25	"b"	t	0.19464247764709908	0.36292491918706415	2026-01-23 12:17:08.283625
72	10	326	26	"b"	t	0.17920038508583178	0.452992323471655	2026-01-23 12:17:15.633129
73	10	12	27	"c"	t	0.2196802321115235	0.4487762664919493	2026-01-23 12:17:25.851037
74	10	8	28	"b"	t	0.2799680233150424	0.45255239011806603	2026-01-23 12:17:34.515121
75	10	223	29	"b"	f	0.2400385544796987	0.4515042960352142	2026-01-23 12:17:51.256587
76	10	44	30	"b"	t	0.2655820877560726	0.45413298549134934	2026-01-23 12:17:55.899718
77	10	26	31	"c"	t	0.28749035211511564	0.47515627522372983	2026-01-23 12:18:00.119951
78	10	25	32	"d"	f	0.2702454730021033	0.3808228780746004	2026-01-23 12:18:06.683075
79	10	33	33	"a"	t	0.278392681749888	0.3926577509546848	2026-01-23 12:18:17.209614
80	10	23	34	"b"	t	0.3019334081619022	0.3940879179793252	2026-01-23 12:18:25.457488
81	10	10	35	"c"	t	0.3343142766096343	0.41793645220505604	2026-01-23 12:18:33.988055
82	10	63	36	"c"	t	0.33846784249192763	0.44835619446097336	2026-01-23 12:18:40.625306
83	10	372	37	"c"	f	0.32692817515239475	0.38007989880403575	2026-01-23 12:18:45.728372
84	10	282	38	"b"	t	0.3334514624225229	0.41007168063312466	2026-01-23 12:18:58.590222
85	10	13	39	"b"	t	0.3596438606418384	0.43327941368339434	2026-01-23 12:19:11.534364
86	10	3	40	"c"	t	0.3607787422024842	0.3890882037528862	2026-01-23 12:19:15.974131
87	11	208	1	\N	\N	\N	\N	2026-01-23 12:27:27.094269
88	12	15	1	\N	\N	\N	\N	2026-01-26 15:42:11.673791
89	13	2	1	\N	\N	\N	\N	2026-01-26 15:42:43.409406
90	14	208	1	"a"	f	-0.33268359112443585	-0.1498362781578818	2026-01-26 15:43:53.047145
91	14	204	2	"a"	f	-0.7197258499608115	-0.3376802657566758	2026-01-26 15:44:10.860948
92	14	49	3	"a"	f	-0.9093857141916122	-0.47091234261530635	2026-01-26 15:44:18.037592
93	14	33	4	"a"	t	-0.8356897963941223	-0.19997836373907937	2026-01-26 15:44:21.125571
94	14	36	5	"a"	f	-0.8994534090359122	-0.4347516284971398	2026-01-26 15:44:23.125211
95	14	27	6	\N	\N	\N	\N	2026-01-26 15:44:24.581577
96	21	14	1	"a"	t	0.3501865494873348	0.16600652645612618	2026-01-27 13:54:43.578109
98	25	15	1	"A"	t	0.403579514447043	0.20330199122120368	2026-01-27 14:35:27.396687
99	25	208	2	"A"	f	0.01438009431493286	0.0029716598884564874	2026-01-27 14:35:29.453498
100	25	14	3	"A"	t	0.19003141480497354	0.0942257134628915	2026-01-27 14:36:53.936201
101	25	152	4	"A"	t	0.3576251298223688	0.6493813706191375	2026-01-27 14:36:58.432702
102	25	43	5	"A"	t	0.45902257805130114	0.6914203785138435	2026-01-27 14:37:02.044538
103	25	369	6	["A", "C"]	f	0.4401693108471119	0.5304945161991064	2026-01-27 14:37:06.739547
97	21	208	2	"a"	f	-0.0066747968203235055	-0.006184264348818691	2026-01-27 13:55:01.933589
104	25	366	7	["A"]	f	0.3807248607920639	0.32697513540817164	2026-01-27 14:37:12.439859
105	25	9	8	"B"	f	0.21446175280100366	0.29523519557975125	2026-01-27 14:37:17.819288
106	25	36	9	"B"	t	0.21773539286388555	0.4052119910204063	2026-01-27 14:37:22.60945
107	25	2	10	"C"	f	0.03589189121357947	0.36593302584831544	2026-01-27 14:37:26.537864
108	25	204	11	"B"	f	-0.1457827503861414	0.340350133615875	2026-01-27 14:37:30.787254
109	25	49	12	"B"	t	-0.09328798202022272	0.33878209428940925	2026-01-27 14:37:35.112865
110	25	42	13	"C"	t	-0.038468949353283426	0.3678655255302303	2026-01-27 14:37:40.338707
111	25	5	14	"B"	t	0.01923103211401111	0.38692228995845684	2026-01-27 14:37:45.737289
112	25	57	15	["A", "B", "C"]	t	0.05278417185152061	0.4667992161061182	2026-01-27 14:37:51.545671
113	25	19	16	["A", "C", "D"]	f	0.03257977432193761	0.4095540331523712	2026-01-27 14:37:57.93597
114	25	7	17	"A"	f	-0.07158692785257545	0.39785074986278157	2026-01-27 14:38:05.916111
115	25	27	18	"C"	f	-0.06640777724063236	0.23379301587407994	2026-01-27 14:38:16.108176
116	25	58	19	"B"	t	-0.06087147440119421	0.27895979716029456	2026-01-27 14:38:20.901746
117	25	4	20	"B"	t	-0.015775101937362028	0.29729975966428845	2026-01-27 14:38:26.758955
118	25	61	21	"A"	t	-0.01089752331423766	0.3764371613892012	2026-01-27 14:38:29.98241
119	25	48	22	"B"	t	-0.008342824339643066	0.4187401231107169	2026-01-27 14:38:44.259357
120	25	28	23	"A"	t	0.0012698195759816466	0.48708783214476054	2026-01-27 14:38:49.276597
121	25	326	24	"A"	f	-0.0006807510870075858	0.4246104681803566	2026-01-27 14:38:58.137384
122	25	21	25	"C"	t	0.006572803872365798	0.4582104783290733	2026-01-27 14:39:02.012745
123	25	44	26	"B"	t	0.026989599876885352	0.4708781190832936	2026-01-27 14:39:07.589946
124	25	12	27	"C"	t	0.09455030018931769	0.47218763169485767	2026-01-27 14:39:13.384434
125	25	38	28	"C"	f	0.062675780598947	0.3858349415935556	2026-01-27 14:39:18.288477
126	25	8	29	"C"	f	-0.013996589374837165	0.38958110767946913	2026-01-27 14:39:23.686049
127	25	26	30	"C"	t	0.02574711033659108	0.43368925266313085	2026-01-27 14:39:33.452373
128	25	25	31	"C"	t	0.01056646004693255	0.4503615367889884	2026-01-27 14:39:38.529654
129	25	33	32	"A"	t	0.03363135574162848	0.48482190478495546	2026-01-27 14:39:43.532289
130	25	13	33	"B"	t	0.039246478839241476	0.46548736616855074	2026-01-27 14:39:48.223491
131	25	10	34	"C"	t	0.08106037135403457	0.4909007268735714	2026-01-27 14:39:53.206631
132	25	223	35	"C"	f	0.043113965478175226	0.46088176211358794	2026-01-27 14:39:57.884752
133	25	282	36	"C"	f	0.014972899122362377	0.4599261928895095	2026-01-27 14:40:03.342263
134	25	16	37	"C"	f	-0.06406899751184256	0.4500482812542747	2026-01-27 14:40:07.615797
135	25	23	38	"B"	t	-0.08535199658022234	0.4890007218509543	2026-01-27 14:40:13.385626
136	25	372	39	["A", "C", "D"]	f	-0.05221953007861983	0.45399826887953104	2026-01-27 14:40:17.137729
137	25	63	40	"C"	t	-0.05537385703491348	0.4401495777304417	2026-01-27 14:40:24.31625
138	26	15	1	"A"	t	0.37383220045875065	0.19073567859591625	2026-01-27 14:42:54.147638
139	26	208	2	"B"	t	0.5882712559354192	0.30366085906384965	2026-01-27 14:42:57.582309
140	26	152	3	"A"	t	0.747627726379786	0.7650340128250598	2026-01-27 14:43:51.232815
141	26	19	4	["A", "B", "D"]	t	0.8614047264382477	1.0955307752711283	2026-01-27 14:44:36.123943
142	26	369	5	["A", "D"]	t	0.9640472266862391	1.2649295076796667	2026-01-27 14:45:10.256552
143	26	223	6	"D"	t	1.1710825026324816	1.356746673759886	2026-01-27 14:45:35.513648
144	26	326	7	"B"	t	1.1751822958563691	1.4278091248363913	2026-01-27 14:46:07.79069
145	26	366	8	["B", "D"]	t	1.2402645608383718	1.5044914565554721	2026-01-27 14:46:21.709139
146	26	313	9	"B"	t	1.279576628517887	1.6523603262883602	2026-01-27 14:46:56.008821
147	26	261	10	"D"	t	1.41538718307395	1.70008136798859	2026-01-27 14:47:37.731691
148	26	9	11	"A"	t	1.4414707285667259	1.6868738425718883	2026-01-27 14:47:57.197309
149	26	57	12	["A", "B", "C"]	t	1.4552791040361217	1.6810049147891466	2026-01-27 14:48:11.983086
150	26	372	13	["A", "D"]	t	1.5440798972236587	1.7751380441842675	2026-01-27 14:48:17.889623
151	26	28	14	"A"	t	1.521210413362253	1.7693818407635902	2026-01-27 14:49:18.099686
152	26	8	15	"B"	t	1.55881768255183	1.7418585458584128	2026-01-27 14:49:21.777027
153	26	189	16	"D"	t	1.6790819896697038	1.7979526779390393	2026-01-27 14:49:25.973837
154	26	17	17	"C"	t	1.6598068100389394	1.8375070739209651	2026-01-27 14:49:44.025961
155	26	47	18	"A"	t	1.686134833533343	1.7628357314106367	2026-01-27 14:49:49.158032
156	26	321	19	"B"	t	1.703260031448679	1.8421961761446781	2026-01-27 14:49:52.537296
157	26	209	20	"C"	t	1.8942660775784825	1.9145733666209193	2026-01-27 14:50:10.49881
158	26	54	21	"A"	t	1.9407559356498234	2.009601950897475	2026-01-27 14:50:28.30513
159	26	254	22	"A"	t	1.948834743832403	1.9257431392232005	2026-01-27 14:50:54.743966
160	26	32	23	"C"	f	1.9944613162722309	1.7105253540492518	2026-01-27 14:51:09.735823
161	26	61	24	"A"	t	2.0355081358224787	1.8330715055883877	2026-01-27 14:51:13.938842
162	26	23	25	"B"	t	1.8755981119857514	1.7602693113532875	2026-01-27 14:51:19.349404
163	26	38	26	"B"	t	1.96422394914758	1.7973272595622356	2026-01-27 14:51:23.186646
164	26	21	27	"C"	t	1.9870161592771869	1.8629374519145185	2026-01-27 14:51:26.296982
165	26	41	28	"C"	t	1.9617513005749465	1.786229415230543	2026-01-27 14:51:29.484909
166	26	26	29	"C"	t	1.9968815897272456	1.800482208267064	2026-01-27 14:51:33.571463
167	26	10	30	"C"	t	1.9779957188535595	1.8749869099977132	2026-01-27 14:51:37.040287
168	26	53	31	"B"	t	2.031545213870897	1.7932683323198266	2026-01-27 14:51:40.065935
169	26	70	32	"B"	t	2.048406396006312	1.8770929451156935	2026-01-27 14:52:10.647429
170	26	65	33	"B"	t	2.142084074981175	1.898507993695356	2026-01-27 14:52:14.997241
171	26	37	34	"C"	t	2.081210889213787	1.8805278417520919	2026-01-27 14:52:30.161692
172	26	36	35	"B"	t	2.121822593022716	1.8875892018445137	2026-01-27 14:52:34.271582
173	26	268	36	"D"	t	2.026041298601637	1.8753150861358954	2026-01-27 14:52:37.782918
174	26	12	37	"C"	t	2.1042664476862547	1.9145892802854885	2026-01-27 14:53:23.611111
175	26	56	38	"C"	t	2.1512619588073365	1.8441480303873101	2026-01-27 14:53:26.702782
176	26	6	39	"B"	t	2.3538397082134517	2.027713652013773	2026-01-27 14:53:30.853664
177	26	50	40	"B"	f	2.194468231720819	1.847618395330106	2026-01-27 14:53:40.027962
179	28	43	1	"a"	t	0.3767498613336524	0.17001264057623514	2026-01-27 16:26:23.355801
180	28	208	2	\N	\N	\N	\N	2026-01-27 16:27:07.254725
181	29	14	1	"a"	t	0.3789393796273084	0.21094559077343078	2026-01-27 16:32:07.677011
182	29	208	2	\N	\N	\N	\N	2026-01-27 16:32:26.950888
183	34	43	1	"A"	t	0.3945842334733626	0.20400461459036806	2026-01-27 16:57:44.468679
184	34	208	2	\N	\N	\N	\N	2026-01-27 16:57:47.310771
185	35	14	1	\N	\N	\N	\N	2026-01-27 17:14:35.778578
178	27	2	1	"a"	f	-0.4440502331321965	-0.2349126747322577	2026-01-27 16:23:03.032038
186	27	204	2	\N	\N	\N	\N	2026-01-27 19:58:29.665738
187	36	208	1	\N	\N	\N	\N	2026-01-27 22:53:55.499007
188	21	15	3	\N	\N	\N	\N	2026-01-27 22:55:32.987049
189	38	43	1	"a"	t	0.36475435565811415	0.17056404994972107	2026-01-27 23:23:57.55503
190	38	208	2	"b"	t	0.6041427916002812	0.30636136903797706	2026-01-27 23:26:24.355311
192	39	15	1	\N	\N	\N	\N	2026-01-27 23:44:29.881852
191	38	152	3	"A"	t	0.7610785213674428	0.7896561862863986	2026-01-27 23:26:38.362879
193	38	19	4	\N	\N	\N	\N	2026-01-27 23:59:09.836474
194	40	208	1	"B"	t	0.4152363987406794	0.1945548199906196	2026-01-28 10:10:29.207353
195	40	152	2	"C"	f	0.32522549229892067	-0.04391490607473294	2026-01-28 10:10:34.239436
196	40	15	3	\N	\N	\N	\N	2026-01-28 10:10:40.179415
197	41	208	1	"A"	f	-0.34751592743987453	-0.182295251486662	2026-01-28 10:38:46.516869
198	41	204	2	"A"	f	-0.7174354970013663	-0.3699643441601837	2026-01-28 10:38:48.211635
199	41	49	3	\N	\N	\N	\N	2026-01-28 10:38:49.881706
200	42	208	1	"B"	t	0.39819192717689855	0.2072280171248071	2026-01-28 10:49:55.222403
201	42	152	2	\N	\N	\N	\N	2026-01-28 11:15:37.213652
202	43	14	1	"a"	t	0.3574075133337231	0.16755958556925019	2026-01-28 11:20:58.972831
203	43	208	2	\N	\N	\N	\N	2026-01-28 11:21:23.903772
204	49	208	1	\N	\N	\N	\N	2026-01-29 11:15:12.335434
205	50	208	1	"a"	f	0	0	2026-01-29 11:21:35.070984
206	50	15	2	\N	\N	\N	\N	2026-01-29 11:22:00.416247
207	51	208	1	"a"	f	0	0	2026-01-29 11:51:49.831916
269	53	48	17	"a"	f	0.6916333255806459	-0.17752308071796982	2026-01-29 12:39:40.397377
208	51	15	2	"a"	t	-0.3820228572843784	-0.1961794410944066	2026-01-29 11:52:04.151018
247	52	26	35	"c"	t	-1.0814535333302122	-0.9497862064824116	2026-01-29 12:22:26.137424
209	51	204	3	"a"	f	0.0005256533386883871	0.029506206036957226	2026-01-29 11:52:07.546729
210	51	14	4	"a"	t	-0.3391403235727371	-0.18433066638190115	2026-01-29 11:52:10.742423
211	51	2	5	"a"	f	-0.10978531858817756	-0.05802888661742837	2026-01-29 11:52:12.239901
212	51	108	6	\N	\N	\N	\N	2026-01-29 11:52:13.625177
213	52	208	1	"c"	f	0	0	2026-01-29 12:19:40.418572
248	52	46	36	"c"	f	-1.0636859657091187	-0.8324170835840976	2026-01-29 12:22:28.286951
214	52	15	2	"b"	f	-0.3882003318679035	-0.19453193424939363	2026-01-29 12:20:01.032582
215	52	204	3	"c"	t	-0.5808173494674337	-0.3027455892695588	2026-01-29 12:20:14.656268
270	53	102	18	"a"	f	0.6916333255806459	-0.17752308071796982	2026-01-29 12:39:41.225692
216	52	49	4	"c"	f	-0.33910038897673583	-0.17542020056234556	2026-01-29 12:20:22.009368
217	52	110	5	"c"	f	-0.33910038897673583	-0.17542020056234556	2026-01-29 12:20:24.87974
249	52	9	37	"c"	f	-1.065557242752836	-0.8840084708789272	2026-01-29 12:22:30.405201
218	52	14	6	"c"	f	-0.5250894426913556	-0.27675415950711985	2026-01-29 12:20:26.971363
219	52	2	7	"c"	f	-0.6445267408145663	-0.3328816783787671	2026-01-29 12:20:28.493165
220	52	109	8	"c"	f	-0.6445267408145663	-0.3328816783787671	2026-01-29 12:20:33.112189
250	52	108	38	"c"	f	-1.065557242752836	-0.8840084708789272	2026-01-29 12:22:33.05877
221	52	42	9	"c"	t	-0.7099072555151286	-0.32586937255013987	2026-01-29 12:20:34.990538
222	52	36	10	"c"	f	-0.5692041383012335	-0.27657090363187853	2026-01-29 12:20:36.686321
251	52	101	39	"c"	f	-1.065557242752836	-0.8840084708789272	2026-01-29 12:22:34.76018
223	52	27	11	"c"	f	-0.6296366536324955	-0.5319049065687467	2026-01-29 12:20:37.918963
224	52	33	12	"c"	f	-0.6575655303274874	-0.7323536107573118	2026-01-29 12:20:39.07738
225	52	100	13	"c"	t	-0.6575655303274874	-0.7323536107573118	2026-01-29 12:20:40.202025
226	52	5	14	"c"	f	-0.6928620306657358	-0.9285806243321767	2026-01-29 12:20:40.65527
252	52	12	40	"c"	t	-1.1006804541837512	-0.8772608366793326	2026-01-29 12:22:36.918384
227	52	25	15	"c"	t	-0.7567640219801561	-0.9410311582120728	2026-01-29 12:20:41.962807
228	52	63	16	"c"	t	-0.7388570458209812	-0.7320468167218435	2026-01-29 12:20:42.82468
253	53	208	1	"b"	t	0	0	2026-01-29 12:38:21.918617
229	52	58	17	"c"	f	-0.689873740412142	-0.5761566544842849	2026-01-29 12:20:43.545964
230	52	48	18	"c"	f	-0.7203017930434834	-0.6963360353460899	2026-01-29 12:20:45.33616
282	53	2	30	"a"	f	0.5741739965928898	-0.465509291976582	2026-01-29 12:40:42.289021
231	52	43	19	"c"	f	-0.7275724118232886	-0.7681206915081118	2026-01-29 12:20:46.76683
254	53	15	2	"a"	t	0.4286080424592187	0.19012480023458672	2026-01-29 12:38:34.330734
232	52	7	20	"c"	f	-0.7606527441559796	-0.7869380439564837	2026-01-29 12:20:48.197575
233	52	4	21	"c"	f	-0.8375697312374107	-0.8005517262254951	2026-01-29 12:20:49.592014
271	53	25	19	"a"	f	0.6433967197755237	-0.30991747408067005	2026-01-29 12:39:41.558301
234	52	30	22	"c"	f	-0.8874385634987522	-0.7901404841284414	2026-01-29 12:20:50.798135
255	53	152	3	"a"	t	0.6310239293443726	0.32843326691800123	2026-01-29 12:39:27.454101
235	52	44	23	"c"	f	-0.8826274628063732	-0.9231962116005554	2026-01-29 12:20:52.314298
236	52	16	24	"c"	f	-0.9601108191689419	-0.9495545202306801	2026-01-29 12:20:53.641075
237	52	60	25	"c"	f	-1.0026460087834848	-0.9301763569623215	2026-01-29 12:20:54.971626
238	52	106	26	"c"	f	-1.0026460087834848	-0.9301763569623215	2026-01-29 12:20:56.696649
239	52	105	27	"c"	f	-1.0026460087834848	-0.9301763569623215	2026-01-29 12:20:56.986518
256	53	366	4	"a"	f	0.7926451167993145	0.8093931938096602	2026-01-29 12:39:32.709166
240	52	13	28	"c"	f	-1.0643510075967404	-1.0084388309792767	2026-01-29 12:20:58.026114
241	52	102	29	"c"	t	-1.0643510075967404	-1.0084388309792767	2026-01-29 12:21:00.028423
242	52	111	30	"c"	f	-1.0643510075967404	-1.0084388309792767	2026-01-29 12:21:00.754163
243	52	68	31	"c"	t	-1.0806816474728773	-1.001365553680212	2026-01-29 12:21:01.64601
272	53	109	20	"a"	f	0.6433967197755237	-0.30991747408067005	2026-01-29 12:39:42.382314
244	52	21	32	"c"	t	-1.074307779708817	-0.955845156913287	2026-01-29 12:21:03.630726
257	53	19	5	"a"	f	0.6822566593722635	0.5599376543381043	2026-01-29 12:39:33.190089
245	52	61	33	"c"	f	-1.05067287306183	-0.8512456900589326	2026-01-29 12:21:05.525407
246	52	38	34	"c"	f	-1.0838839848468886	-0.8529344405429033	2026-01-29 12:21:07.343518
258	53	369	6	"a"	f	0.6490183322795628	0.4142417519352033	2026-01-29 12:39:33.830711
259	53	110	7	"a"	t	0.6490183322795628	0.4142417519352033	2026-01-29 12:39:34.523865
273	53	105	21	"a"	f	0.6433967197755237	-0.30991747408067005	2026-01-29 12:39:42.562279
260	53	14	8	"a"	t	0.6117528638237558	0.3096102197011014	2026-01-29 12:39:35.002148
261	53	107	9	"a"	t	0.6117528638237558	0.3096102197011014	2026-01-29 12:39:35.515343
262	53	36	10	"a"	f	0.7058599018976667	0.36545647928197544	2026-01-29 12:39:35.739387
274	53	108	22	"a"	f	0.6433967197755237	-0.30991747408067005	2026-01-29 12:39:42.729426
263	53	57	11	"a"	f	0.6438424757157419	0.11524018115056772	2026-01-29 12:39:36.387948
264	53	27	12	"a"	f	0.6159810783971634	-0.002093940955724042	2026-01-29 12:39:37.206637
265	53	58	13	"a"	f	0.6117176220762244	-0.15212027516293988	2026-01-29 12:39:37.980949
266	53	101	14	"a"	t	0.6117176220762244	-0.15212027516293988	2026-01-29 12:39:38.756876
275	53	61	23	"a"	t	0.6185496712557151	-0.4278966661237928	2026-01-29 12:39:42.92791
267	53	33	15	"a"	t	0.5424640249491296	-0.2830973680814851	2026-01-29 12:39:38.918396
268	53	43	16	"a"	t	0.5582991749074739	-0.19585133442600938	2026-01-29 12:39:39.619765
283	53	26	31	"a"	f	0.35308093252462175	-0.5196821685165565	2026-01-29 12:40:44.059313
276	53	63	24	"a"	f	0.6686958479516748	-0.30989276692017825	2026-01-29 12:39:43.815112
277	53	223	25	"a"	f	0.624387388779425	-0.4179548331135471	2026-01-29 12:39:44.835436
278	53	9	26	"a"	t	0.5011972803803557	-0.4465509454507686	2026-01-29 12:39:45.782255
284	53	5	32	"a"	f	0.34272738517557827	-0.5619702987451705	2026-01-29 12:40:45.896252
279	53	21	27	"a"	f	0.6117520020258135	-0.42441063603895174	2026-01-29 12:39:46.869185
280	53	38	28	"a"	f	0.6027243935986584	-0.5027709223792601	2026-01-29 12:39:52.624356
289	53	4	37	"a"	f	-0.3142502082546728	-0.6268108633874537	2026-01-29 12:40:55.100241
281	53	30	29	"a"	t	0.5790576200038998	-0.5242322990825051	2026-01-29 12:40:40.475316
285	53	7	33	"a"	f	0.20444893631449496	-0.5942403592526172	2026-01-29 12:40:47.358032
286	53	204	34	"a"	f	0.06043321248786552	-0.6115966762459372	2026-01-29 12:40:49.243296
290	53	44	38	"a"	f	-0.3745454558865174	-0.6322653023374236	2026-01-29 12:40:57.12671
287	53	49	35	"a"	f	-0.0815095160113522	-0.6143017570147096	2026-01-29 12:40:51.235219
288	53	42	36	"a"	f	-0.2101472659204135	-0.610955694513405	2026-01-29 12:40:52.938609
294	53	60	42	"a"	f	-0.4836712990632099	-0.6372128222752158	2026-01-29 12:41:03.502519
291	53	12	39	"a"	f	-0.44238262868348643	-0.65456035744181	2026-01-29 12:40:59.361026
292	53	111	40	"a"	f	-0.44238262868348643	-0.65456035744181	2026-01-29 12:41:01.579797
293	53	106	41	"a"	t	-0.44238262868348643	-0.65456035744181	2026-01-29 12:41:02.455764
296	53	16	44	"a"	f	-0.5395727207102391	-0.7037291547232618	2026-01-29 12:41:08.53248
295	53	13	43	"a"	f	-0.48918100108792084	-0.7283923614027886	2026-01-29 12:41:06.242156
297	53	46	45	"a"	f	-0.5962109029722547	-0.7341302714021863	2026-01-29 12:41:10.638338
298	53	282	46	"a"	f	-0.5952461042567706	-0.7812082261673325	2026-01-29 12:41:13.064938
299	53	8	47	"a"	f	-0.613935289371145	-0.7830318303405511	2026-01-29 12:41:15.64938
300	53	68	48	"a"	f	-0.6552014001403711	-0.8013496699719986	2026-01-29 12:41:18.823205
301	53	55	49	"a"	f	-0.6941518130826374	-0.8974686964268564	2026-01-29 12:41:21.721121
302	53	104	50	"a"	f	-0.6941518130826374	-0.8974686964268564	2026-01-29 12:41:24.619029
303	54	208	1	"a"	f	0	0	2026-01-29 16:00:29.254632
304	54	15	2	"a"	t	-0.35602745706606886	-0.15495134092281435	2026-01-29 16:02:55.09098
305	54	204	3	"a"	f	0.0071649674138877075	-0.01219006869184053	2026-01-29 16:02:59.335043
306	54	14	4	"a"	t	-0.33691924864995465	-0.17840278616342464	2026-01-29 16:03:02.226634
307	54	2	5	"a"	f	-0.12398259448255691	-0.0530454345131264	2026-01-29 16:03:03.712824
308	54	112	6	"a"	f	-0.12398259448255691	-0.0530454345131264	2026-01-29 16:03:05.021567
309	54	110	7	"a"	t	-0.12398259448255691	-0.0530454345131264	2026-01-29 16:04:19.948821
310	54	43	8	"a"	t	-0.29229806037730127	-0.1343677310139974	2026-01-29 16:04:57.353586
311	54	49	9	"a"	f	-0.12569385107671638	-0.07067834146083522	2026-01-29 16:05:02.193759
348	54	26	46	"a"	f	-0.960554174776856	-1.344290657609373	2026-01-29 16:07:57.127993
312	54	36	10	"a"	f	-0.2911991090781677	-0.1381245563727937	2026-01-29 16:05:04.006863
313	54	42	11	"a"	f	-0.3351542890801276	-0.45609114485131297	2026-01-29 16:05:05.619874
383	55	61	31	"c"	f	-0.3664119190139171	-0.32398169694913587	2026-01-29 17:02:41.447604
314	54	33	12	"a"	t	-0.44542253188111086	-0.500572941006487	2026-01-29 16:05:06.95228
349	54	22	47	"a"	f	-0.9595472825968432	-1.4497582432522182	2026-01-29 16:07:58.771455
315	54	5	13	"a"	f	-0.3900906454812651	-0.28487914839131545	2026-01-29 16:05:08.769917
316	54	27	14	"a"	f	-0.509346304280714	-0.30251279800429315	2026-01-29 16:05:57.734891
371	55	58	19	"b"	t	-0.3364604934625486	-0.2022713550617905	2026-01-29 16:59:07.454198
317	54	58	15	"a"	f	-0.514206677895986	-0.45572581042485094	2026-01-29 16:05:59.49411
350	54	61	48	"a"	t	-0.9894159121511631	-1.4654311561715454	2026-01-29 16:08:01.015708
318	54	25	16	"a"	f	-0.5298746742046851	-0.63510836093502	2026-01-29 16:06:00.95323
319	54	9	17	"a"	t	-0.56800010866154	-0.7677094013765908	2026-01-29 16:06:02.264622
320	54	63	18	"a"	f	-0.4407648505251983	-0.755084368248469	2026-01-29 16:06:03.470798
351	54	23	49	"a"	f	-0.9574879475927338	-1.2897258612282956	2026-01-29 16:08:02.718996
321	54	7	19	"a"	f	-0.42906661476160446	-0.8897851960148953	2026-01-29 16:06:04.774037
322	54	4	20	"a"	f	-0.5165996769815371	-0.8887409912409094	2026-01-29 16:06:06.196097
323	54	111	21	"a"	f	-0.5165996769815371	-0.8887409912409094	2026-01-29 16:06:08.348033
324	54	100	22	"a"	f	-0.5165996769815371	-0.8887409912409094	2026-01-29 16:06:11.445778
372	55	101	20	"b"	f	-0.3364604934625486	-0.2022713550617905	2026-01-29 17:00:15.536358
325	54	48	23	"a"	f	-0.5703735775896219	-0.8995675037535962	2026-01-29 16:06:14.481025
352	54	70	50	"a"	f	-0.9440491510763656	-1.2988416750085758	2026-01-29 16:08:04.473895
326	54	30	24	"a"	t	-0.5803306982739048	-0.9635511028790522	2026-01-29 16:06:16.296131
327	54	44	25	"a"	f	-0.5798456724589341	-0.8488803585019763	2026-01-29 16:06:34.812466
353	55	208	1	"b"	t	0	0	2026-01-29 16:56:05.256291
328	54	60	26	"a"	f	-0.6135205944858839	-0.8805215389529331	2026-01-29 16:06:37.393215
329	54	16	27	"a"	f	-0.6195077158170145	-0.9588495954482542	2026-01-29 16:06:39.028419
330	54	13	28	"a"	f	-0.6785896827566763	-0.9464080127316977	2026-01-29 16:06:40.567848
354	55	15	2	"b"	f	0.4054037058156011	0.20103531555001988	2026-01-29 16:56:28.566095
331	54	12	29	"a"	f	-0.757160210715053	-0.9987528228491274	2026-01-29 16:06:42.245899
332	54	68	30	"a"	f	-0.8106280030191979	-1.010567013880206	2026-01-29 16:07:35.679778
333	54	106	31	"a"	t	-0.8106280030191979	-1.010567013880206	2026-01-29 16:07:36.871755
334	54	21	32	"a"	f	-0.7881113073272096	-1.0945635814729457	2026-01-29 16:07:37.677658
335	54	104	33	"a"	f	-0.7881113073272096	-1.0945635814729457	2026-01-29 16:07:39.58138
336	54	105	34	"a"	f	-0.7881113073272096	-1.0945635814729457	2026-01-29 16:07:40.297161
355	55	152	3	"b"	f	0.029274089035861716	0.01193479761401379	2026-01-29 16:56:40.708746
337	54	282	35	"a"	f	-0.8160994247775676	-1.16074468446914	2026-01-29 16:07:41.249851
338	54	55	36	"a"	f	-0.8776681974745815	-1.1347266870599184	2026-01-29 16:07:42.799897
339	54	109	37	"a"	f	-0.8776681974745815	-1.1347266870599184	2026-01-29 16:07:44.386183
340	54	101	38	"a"	t	-0.8776681974745815	-1.1347266870599184	2026-01-29 16:07:45.114531
341	54	102	39	"a"	f	-0.8776681974745815	-1.1347266870599184	2026-01-29 16:07:46.005499
373	55	9	21	"b"	f	-0.30603439313288966	-0.09066933111662148	2026-01-29 17:00:17.074707
342	54	46	40	"a"	f	-0.8882824483081039	-1.1512646250495633	2026-01-29 16:07:46.863193
356	55	14	4	"b"	f	-0.008532320024793994	-0.160232105223657	2026-01-29 16:56:44.866557
343	54	38	41	"a"	f	-0.8846868435412903	-1.1943162999500743	2026-01-29 16:07:48.308482
344	54	45	42	"a"	f	-0.8954644470851656	-1.297830441861082	2026-01-29 16:07:49.327191
345	54	3	43	"a"	f	-0.8998620395722751	-1.3446184882504084	2026-01-29 16:07:50.673535
357	55	43	5	"b"	f	-0.21680826268514883	-0.23179284399305053	2026-01-29 16:56:47.285715
346	54	8	44	"a"	f	-0.949391109187525	-1.3327935464269927	2026-01-29 16:07:53.892874
347	54	31	45	"a"	f	-0.972288004573717	-1.3592177667395837	2026-01-29 16:07:55.446679
358	55	204	6	"b"	f	-0.362428871296853	-0.3211568499473807	2026-01-29 16:56:48.718617
359	55	102	7	"b"	f	-0.362428871296853	-0.3211568499473807	2026-01-29 16:56:50.806449
374	55	7	22	"b"	t	-0.36813302607141335	-0.11613252947288363	2026-01-29 17:00:18.349202
360	55	2	8	"b"	t	-0.5740401292852111	-0.40465816155218604	2026-01-29 16:56:52.386538
361	55	104	9	"b"	f	-0.5740401292852111	-0.40465816155218604	2026-01-29 16:56:54.044627
362	55	49	10	"b"	t	-0.42352114446620853	-0.29972195840228744	2026-01-29 16:56:55.226442
384	55	21	32	"c"	t	-0.39669347588326026	-0.3657279004884622	2026-01-29 17:02:44.668577
363	55	42	11	"b"	f	-0.3231820958268027	-0.2738487017657524	2026-01-29 16:57:03.087191
375	55	48	23	"b"	t	-0.27728473527005826	-0.07490978320652135	2026-01-29 17:00:19.540367
364	55	36	12	"b"	t	-0.42373489336398107	-0.34019604531780595	2026-01-29 16:57:04.6629
365	55	105	13	"b"	t	-0.42373489336398107	-0.34019604531780595	2026-01-29 16:57:06.105262
366	55	27	14	"b"	f	-0.3828926914945187	-0.028458408700402935	2026-01-29 16:57:14.388853
367	55	107	15	"b"	f	-0.3828926914945187	-0.028458408700402935	2026-01-29 16:57:56.259728
368	55	100	16	"b"	f	-0.3828926914945187	-0.028458408700402935	2026-01-29 16:57:59.296793
369	55	5	17	"b"	t	-0.420387834618867	-0.27649105781855016	2026-01-29 16:58:00.540173
370	55	106	18	"b"	f	-0.420387834618867	-0.27649105781855016	2026-01-29 16:58:04.107162
376	55	33	24	"d"	f	-0.28919116233213976	0.0042296269632600015	2026-01-29 17:00:20.83618
377	55	111	25	"d"	f	-0.28919116233213976	0.0042296269632600015	2026-01-29 17:01:26.951915
378	55	112	26	"d"	t	-0.28919116233213976	0.0042296269632600015	2026-01-29 17:01:32.741782
390	55	26	38	"c"	t	-0.46664013843262336	-0.49399499211510967	2026-01-29 17:04:01.720837
379	55	366	27	"d"	f	-0.29573204319307383	-0.14768550945062317	2026-01-29 17:01:34.211631
385	55	57	33	"c"	f	-0.36495642164523173	-0.27852451944651746	2026-01-29 17:02:47.373369
380	55	25	28	"d"	f	-0.3122149691111709	-0.21944710319872557	2026-01-29 17:01:35.724518
381	55	4	29	"d"	f	-0.32229362485119706	-0.38711647679738453	2026-01-29 17:01:42.222939
382	55	63	30	"c"	t	-0.3850560432269114	-0.37026518674249526	2026-01-29 17:02:29.612511
396	55	8	44	"b"	t	-0.49454174340961615	-0.44393393512300294	2026-01-29 17:04:52.586434
386	55	38	34	"c"	f	-0.38512224188591154	-0.34705255909616284	2026-01-29 17:02:49.800006
391	55	12	39	"c"	t	-0.4744774683795579	-0.43476164926857086	2026-01-29 17:04:03.606575
387	55	44	35	"c"	f	-0.4137091597539401	-0.4127830289463173	2026-01-29 17:02:54.190669
388	55	30	36	"c"	f	-0.4535456730180282	-0.40661486214159803	2026-01-29 17:02:56.236854
389	55	110	37	"c"	f	-0.4535456730180282	-0.40661486214159803	2026-01-29 17:03:08.262183
394	55	16	42	"c"	f	-0.45286082387071347	-0.49065350490203163	2026-01-29 17:04:18.933129
392	55	60	40	"c"	f	-0.39412291293644036	-0.4311724450055423	2026-01-29 17:04:12.366201
393	55	13	41	"c"	f	-0.39432424904319635	-0.48661319310931506	2026-01-29 17:04:16.188141
395	55	28	43	"a"	t	-0.5073413631194977	-0.5048915611380881	2026-01-29 17:04:41.277398
397	55	46	45	"a"	f	-0.4613171758737378	-0.39417321004940514	2026-01-29 17:05:02.094087
398	55	282	46	"a"	f	-0.472591787332829	-0.48263763072863325	2026-01-29 17:06:27.022883
399	55	23	47	"d"	f	-0.5017978808721912	-0.4730991753715599	2026-01-29 17:06:36.213658
400	55	31	48	"d"	f	-0.5123329793745519	-0.5096617805812509	2026-01-29 17:06:48.715129
401	55	3	49	"d"	f	-0.5073017634592168	-0.5725379692027037	2026-01-29 17:11:38.800304
402	55	55	50	"d"	f	-0.5588607737234272	-0.5772435827476242	2026-01-29 17:12:25.348383
403	56	208	1	"B"	t	0	0	2026-01-29 20:36:01.509984
404	56	15	2	"A"	t	0.438638817789584	0.21211232178663542	2026-01-29 20:36:04.431717
405	56	152	3	"A"	t	0.6113530875241304	0.3027701505761542	2026-01-29 20:36:06.044256
406	56	36	4	"A"	f	0.757607105385797	0.8069873980107405	2026-01-29 20:36:07.849321
407	56	19	5	["A", "B", "D"]	t	0.6459517322354983	0.4373125203091136	2026-01-29 20:36:08.846888
408	56	366	6	["C"]	f	0.7158947624611252	0.7544553014088	2026-01-29 20:36:14.057343
409	56	369	7	["A", "B", "D"]	f	0.6930376540617762	0.5762472308204306	2026-01-29 20:36:18.353472
410	56	109	8	"D"	t	0.6930376540617762	0.5762472308204306	2026-01-29 20:36:24.339231
448	56	282	46	"C"	f	-0.23099869477696833	0.3480156795601163	2026-01-29 20:40:01.548455
411	56	14	9	"A"	t	0.6698922756583506	0.473281832412551	2026-01-29 20:36:30.531423
412	56	57	10	["A", "B", "C"]	t	0.7652807873966162	0.49250596324124957	2026-01-29 20:36:32.717053
413	56	223	11	"A"	f	0.7989129713528357	0.5845049246443526	2026-01-29 20:36:45.219518
449	56	10	47	"C"	t	-0.2468156823477826	0.3388924837244897	2026-01-29 20:40:05.212451
414	56	43	12	"A"	t	0.6690803891131981	0.5579854671408677	2026-01-29 20:36:49.861309
415	56	9	13	"A"	t	0.7461439387436247	0.5835824350437374	2026-01-29 20:36:52.132385
474	62	36	5	"B"	t	0.6515814292053437	0.0745512600892086	2026-01-29 21:29:16.062768
416	56	27	14	"D"	t	0.800215299448136	0.6094960506964459	2026-01-29 20:36:54.865893
450	56	63	48	"E"	f	-0.23907019807127664	0.3324827264861352	2026-01-29 20:40:08.662681
417	56	61	15	"A"	t	0.7992920362704203	0.619531871443332	2026-01-29 20:37:01.633757
418	56	326	16	"C"	f	0.8209011246247779	0.6830862751828389	2026-01-29 20:37:05.94046
419	56	28	17	"A"	t	0.8168198518274333	0.618941524594936	2026-01-29 20:37:15.537096
451	56	23	49	"A"	f	-0.2298235208679904	0.22991739894992297	2026-01-29 20:40:14.412687
420	56	58	18	"B"	t	0.8035234872546985	0.671292233618541	2026-01-29 20:37:18.458608
421	56	21	19	"B"	f	0.8159273017415902	0.709251330572475	2026-01-29 20:37:23.486882
422	56	48	20	"D"	f	0.7825010227363209	0.5937585322691245	2026-01-29 20:37:29.684229
452	56	372	50	["C", "D"]	f	-0.25412753728949744	0.17998585926901095	2026-01-29 20:40:18.776124
423	56	38	21	"A"	f	0.7761866615272307	0.47641090979305145	2026-01-29 20:37:47.462895
424	56	26	22	"C"	t	0.775413013607446	0.3642158277654696	2026-01-29 20:37:49.156966
425	56	108	23	"A"	f	0.775413013607446	0.3642158277654696	2026-01-29 20:37:53.720613
453	57	208	1	"C"	f	0	0	2026-01-29 21:27:05.924956
426	56	25	24	"C"	t	0.7549620590051861	0.3912943340023576	2026-01-29 20:39:00.997637
427	56	106	25	"A"	t	0.7549620590051861	0.3912943340023576	2026-01-29 20:39:04.194857
454	57	15	2	\N	\N	\N	\N	2026-01-29 21:27:08.828064
428	56	33	26	"A"	t	0.7467542410659594	0.41928099732925656	2026-01-29 20:39:07.464624
429	56	2	27	"C"	f	0.7901055675993203	0.44262009977930294	2026-01-29 20:39:09.673499
430	56	102	28	"C"	t	0.7901055675993203	0.44262009977930294	2026-01-29 20:39:12.552874
455	58	208	1	"B"	t	0	0	2026-01-29 21:27:15.662987
431	56	7	29	"A"	f	0.5150630083529001	0.41505759885170124	2026-01-29 20:39:16.253954
432	56	104	30	"A"	f	0.5150630083529001	0.41505759885170124	2026-01-29 20:39:18.196597
433	56	111	31	"A"	f	0.5150630083529001	0.41505759885170124	2026-01-29 20:39:19.250453
434	56	112	32	"A"	f	0.5150630083529001	0.41505759885170124	2026-01-29 20:39:21.039145
456	58	15	2	\N	\N	\N	\N	2026-01-29 21:27:18.515738
435	56	5	33	"A"	f	0.36178031157192825	0.39448441128061146	2026-01-29 20:39:24.217259
436	56	42	34	"C"	t	0.20130957233109276	0.3943300327528205	2026-01-29 20:39:26.015256
457	59	208	1	"D"	f	0	0	2026-01-29 21:27:26.015935
437	56	204	35	"A"	f	0.2602194141139829	0.39398628579744094	2026-01-29 20:39:32.2874
438	56	49	36	"A"	f	0.06350910483546907	0.3711298681359864	2026-01-29 20:39:34.789072
475	62	27	6	"C"	f	0.6963178565770196	0.27282274046045	2026-01-29 21:29:20.270121
439	56	4	37	"A"	f	-0.04380024672100953	0.3556392220248398	2026-01-29 20:39:36.382163
440	56	101	38	"A"	t	-0.04380024672100953	0.3556392220248398	2026-01-29 20:39:39.249001
458	59	15	2	"B"	f	-0.37152763555168755	-0.17238162451950403	2026-01-29 21:27:29.627789
441	56	44	39	"A"	f	-0.1343806530307155	0.33834952258781004	2026-01-29 20:39:40.625637
442	56	110	40	"A"	t	-0.1343806530307155	0.33834952258781004	2026-01-29 20:39:42.707296
459	59	204	3	\N	\N	\N	\N	2026-01-29 21:27:32.663495
443	56	12	41	"A"	f	-0.18980067985706991	0.3428419589049161	2026-01-29 20:39:44.437529
444	56	100	42	"A"	f	-0.18980067985706991	0.3428419589049161	2026-01-29 20:39:46.396284
445	56	8	43	"B"	t	-0.2282768561903752	0.35106033864678754	2026-01-29 20:39:47.718104
460	60	208	1	"B"	t	0	0	2026-01-29 21:27:38.719821
446	56	13	44	"B"	t	-0.18962586479909346	0.35478640427826746	2026-01-29 20:39:52.431704
447	56	16	45	"C"	f	-0.15624741560120908	0.36126621399442604	2026-01-29 20:39:56.493464
476	62	366	7	\N	\N	\N	\N	2026-01-29 21:29:25.138949
461	60	15	2	"A"	t	0.4397774767518471	0.21652283503452965	2026-01-29 21:27:41.426977
477	63	208	1	"A"	f	0	0	2026-01-29 21:52:22.713423
462	60	152	3	"A"	t	0.5885852155879178	0.28998770379769573	2026-01-29 21:27:43.037376
463	60	100	4	\N	\N	\N	\N	2026-01-29 21:27:46.688907
464	61	208	1	"B"	t	0	0	2026-01-29 21:28:46.694981
478	63	14	2	\N	\N	\N	\N	2026-01-29 21:52:25.810043
465	61	15	2	"B"	f	0.40875093566946513	0.21826911184955627	2026-01-29 21:28:50.069734
466	61	152	3	"A"	t	0.033672840615647646	0.004791276489037184	2026-01-29 21:28:55.459712
479	64	208	1	"B"	t	0	0	2026-01-29 21:52:30.80831
467	61	14	4	"A"	t	0.207255323303769	0.6061987304381751	2026-01-29 21:28:57.689482
480	64	15	2	\N	\N	\N	\N	2026-01-29 21:52:36.192075
468	61	43	5	"A"	t	0.38981028872678464	0.6734300930448026	2026-01-29 21:28:58.960011
469	61	369	6	\N	\N	\N	\N	2026-01-29 21:29:00.424738
470	62	208	1	"B"	t	0	0	2026-01-29 21:29:06.453284
471	62	15	2	"A"	t	0.4154995719903565	0.2011759456193856	2026-01-29 21:29:09.456615
481	65	208	1	"C"	f	0	0	2026-01-29 21:52:42.19241
472	62	152	3	"B"	f	0.6014265047702115	0.3275058282909962	2026-01-29 21:29:10.724944
482	65	14	2	\N	\N	\N	\N	2026-01-29 21:53:22.561584
473	62	14	4	"A"	t	0.518454834371616	0.03987031159723356	2026-01-29 21:29:14.042412
483	66	208	1	"b"	t	0	0	2026-01-30 00:40:40.42314
490	66	204	8	"d"	f	-0.37979516950454284	-0.30657158924380973	2026-01-30 00:42:53.795612
484	66	15	2	"b"	f	0.41209483074155884	0.21028645441767851	2026-01-30 00:41:22.667238
485	66	152	3	"b"	f	0.06321578112599319	0.042816719156988266	2026-01-30 00:41:27.027002
495	66	27	13	"d"	t	-0.8912355924467421	-0.5255267983033687	2026-01-30 00:43:01.028603
486	66	14	4	"b"	f	-0.01133899273195333	-0.1493299573807664	2026-01-30 00:41:28.197069
487	66	110	5	"d"	f	-0.01133899273195333	-0.1493299573807664	2026-01-30 00:41:29.139299
488	66	111	6	"d"	f	-0.01133899273195333	-0.1493299573807664	2026-01-30 00:42:46.540057
491	66	2	9	"d"	f	-0.5688385809802181	-0.38039563107844854	2026-01-30 00:42:54.953036
489	66	43	7	"d"	f	-0.23280706921973632	-0.24162703472103486	2026-01-30 00:42:52.568754
492	66	112	10	"d"	t	-0.5688385809802181	-0.38039563107844854	2026-01-30 00:42:57.02535
493	66	49	11	"d"	f	-0.6961319333490392	-0.43656584834988854	2026-01-30 00:42:58.762178
496	66	109	14	"d"	t	-0.8912355924467421	-0.5255267983033687	2026-01-30 00:43:02.421848
494	66	42	12	"d"	f	-0.8008111714794225	-0.47329222201524157	2026-01-30 00:42:59.944998
497	66	106	15	"d"	f	-0.8912355924467421	-0.5255267983033687	2026-01-30 00:43:04.857995
500	66	58	18	"a"	f	-0.910445567233592	-0.6129223077204021	2026-01-30 00:43:20.466084
498	66	33	16	"d"	f	-0.8322643171775597	-0.21099731324363125	2026-01-30 00:43:05.987412
499	66	36	17	"a"	f	-0.8814433318789824	-0.49239466664052983	2026-01-30 00:43:07.732825
501	66	25	19	"a"	f	-0.9338474774148976	-0.7395539606495313	2026-01-30 00:44:23.656591
502	66	5	20	"a"	f	-0.9350205638302523	-0.8630976494527928	2026-01-30 00:44:25.192633
503	66	105	21	"a"	f	-0.9350205638302523	-0.8630976494527928	2026-01-30 00:44:26.983762
504	66	63	22	"a"	f	-1.0314439466761394	-0.8979306129402748	2026-01-30 00:44:29.246517
506	66	30	24	\N	\N	\N	\N	2026-01-30 00:48:02.389284
505	66	48	23	"d"	f	-1.0272871389783282	-1.0283376172433463	2026-01-30 00:46:48.926966
507	67	208	1	"a"	f	0	0	2026-01-30 00:58:10.203864
508	67	15	2	"a"	t	-0.36644865268890464	-0.17594148182140842	2026-01-30 00:58:36.107649
509	67	204	3	"a"	f	0.0009145651513895634	0.011592917621324401	2026-01-30 00:58:39.74031
510	67	14	4	"a"	t	-0.34135366234817033	-0.1769396518241046	2026-01-30 00:58:41.393061
511	67	2	5	"a"	f	-0.10711844428486147	-0.05249000491800697	2026-01-30 00:58:42.581603
512	67	43	6	"a"	t	-0.2960081380111451	-0.1622786908836223	2026-01-30 00:58:43.690112
513	67	49	7	"a"	f	-0.13083531097549106	-0.047355570841243026	2026-01-30 00:58:45.268505
551	69	44	25	"a"	f	-0.7020828231606019	-0.6381324756275525	2026-01-30 01:09:02.074516
514	67	36	8	"a"	f	-0.28549791159689075	-0.15547207251742065	2026-01-30 00:58:47.432426
515	67	42	9	"a"	f	-0.33645872074609595	-0.403391142178387	2026-01-30 00:58:55.818617
552	69	107	26	"a"	t	-0.7020828231606019	-0.6381324756275525	2026-01-30 01:09:03.846186
516	67	27	10	"a"	f	-0.42712326181922383	-0.487386630410139	2026-01-30 00:58:59.964235
517	67	33	11	"a"	t	-0.45538002271763967	-0.6762792367255264	2026-01-30 00:59:06.183614
519	68	208	1	"d"	f	0	0	2026-01-30 01:05:18.741363
585	67	112	28	"b"	f	-0.32079604804190653	-0.23718001974155944	2026-01-30 01:17:57.016752
520	68	15	2	"d"	f	-0.37188686296988555	-0.16029845511412666	2026-01-30 01:05:33.48791
553	69	61	27	"a"	t	-0.7209868840425362	-0.6464949350582025	2026-01-30 01:09:05.652676
521	68	204	3	"d"	f	-0.5767229842868777	-0.26370033497572515	2026-01-30 01:05:36.654291
522	68	49	4	"d"	f	-0.813980805583517	-0.4125871387804962	2026-01-30 01:05:39.041774
573	67	9	16	"b"	f	-0.493456556152487	-0.3407105093096446	2026-01-30 01:17:09.653136
523	68	42	5	"d"	f	-1.0013275773837216	-0.5259030636731169	2026-01-30 01:05:40.658159
554	69	21	28	"a"	f	-0.7110992393760543	-0.5302316025066764	2026-01-30 01:09:09.385668
524	68	33	6	"d"	f	-1.0933902717770525	-0.5241296330438996	2026-01-30 01:05:42.153062
525	68	27	7	"a"	f	-1.1578182121349745	-0.8824042770959909	2026-01-30 01:05:43.286251
526	68	25	8	\N	\N	\N	\N	2026-01-30 01:05:51.734719
527	69	208	1	"a"	f	0	0	2026-01-30 01:07:12.697472
555	69	101	29	"a"	t	-0.7110992393760543	-0.5302316025066764	2026-01-30 01:09:13.675923
528	69	15	2	"a"	t	-0.37338576196137974	-0.19966742611704658	2026-01-30 01:07:30.375528
529	69	204	3	"a"	f	0.013680249652571981	0.019149124676324097	2026-01-30 01:07:33.495759
530	69	14	4	"a"	t	-0.3428090224185679	-0.13463473002903456	2026-01-30 01:07:34.463728
556	69	38	30	"a"	f	-0.7343406735693495	-0.5892251871554202	2026-01-30 01:09:15.55891
531	69	2	5	"a"	f	-0.10639086295634224	-0.04939199842824669	2026-01-30 01:07:35.643285
532	69	43	6	"a"	t	-0.2826379029022751	-0.12758478283203503	2026-01-30 01:07:37.338878
533	69	49	7	"a"	f	-0.11479668945102789	-0.06263952837462951	2026-01-30 01:07:39.580832
557	69	16	31	"a"	f	-0.7527899787467707	-0.6284529512298768	2026-01-30 01:09:20.210023
534	69	36	8	"a"	f	-0.2795031045502804	-0.14805117173302482	2026-01-30 01:07:41.399383
535	69	42	9	"a"	f	-0.3353141965093388	-0.44975930487183424	2026-01-30 01:07:42.664305
574	67	7	17	"b"	t	-0.566040773636985	-0.3167414022179551	2026-01-30 01:17:11.199107
536	69	33	10	"a"	t	-0.43055151301051375	-0.4557062149742328	2026-01-30 01:07:44.032639
558	69	60	32	"a"	f	-0.7961002454969315	-0.6371574287252142	2026-01-30 01:09:23.007792
537	69	5	11	"a"	f	-0.40622473382740176	-0.2769637097211598	2026-01-30 01:07:45.308617
538	69	27	12	"a"	f	-0.49094978624844066	-0.30234113200478374	2026-01-30 01:07:46.495969
539	69	58	13	"c"	f	-0.5066264144676306	-0.47429750938876586	2026-01-30 01:07:47.639833
559	69	26	33	"a"	f	-0.8074260310326368	-0.7090765219686089	2026-01-30 01:09:31.110434
540	69	25	14	"c"	t	-0.5249973214996076	-0.6292797277283687	2026-01-30 01:08:01.031675
541	69	112	15	"c"	f	-0.5249973214996076	-0.6292797277283687	2026-01-30 01:08:06.419011
542	69	9	16	"c"	f	-0.5100234228754209	-0.4455535937904171	2026-01-30 01:08:08.115651
593	67	13	36	"a"	f	-0.3808796659452191	-0.20259636134698142	2026-01-30 01:18:35.427156
543	69	48	17	"Hypothesis testing (e.g., t-test)."	f	-0.5822822411274583	-0.5127356983653812	2026-01-30 01:08:10.475222
560	69	13	34	"a"	f	-0.8428589917033962	-0.7848864413925938	2026-01-30 01:09:35.187265
544	69	7	18	"Hypothesis testing (e.g., t-test)."	f	-0.5709039552344807	-0.5883850815314534	2026-01-30 01:08:25.892474
545	69	63	19	"Hypothesis testing (e.g., t-test)."	f	-0.6240594514055267	-0.5884338578156901	2026-01-30 01:08:34.079585
546	69	102	20	"a"	f	-0.6240594514055267	-0.5884338578156901	2026-01-30 01:08:37.081812
547	69	110	21	"a"	t	-0.6240594514055267	-0.5884338578156901	2026-01-30 01:08:47.663398
561	69	105	35	"a"	f	-0.8428589917033962	-0.7848864413925938	2026-01-30 01:09:37.195052
548	69	4	22	"a"	f	-0.6452542520004578	-0.7340127388611161	2026-01-30 01:08:50.09711
549	69	30	23	"a"	t	-0.686319417385632	-0.731020867927833	2026-01-30 01:08:52.155011
550	69	106	24	"a"	t	-0.686319417385632	-0.731020867927833	2026-01-30 01:08:59.902344
575	67	4	18	"b"	t	-0.46092274066140626	-0.3167413881334706	2026-01-30 01:17:12.669737
562	69	12	36	"a"	f	-0.8631786988495629	-0.7686055776750873	2026-01-30 01:09:38.697259
563	69	46	37	"a"	f	-0.8994554199635915	-0.7819970703106509	2026-01-30 01:09:40.761673
586	67	26	29	"b"	f	-0.34265813732668027	-0.26039668145902123	2026-01-30 01:18:01.196858
564	69	68	38	"a"	f	-0.9030093996409898	-0.871320881406612	2026-01-30 01:09:45.599275
565	69	100	39	"a"	t	-0.9030093996409898	-0.871320881406612	2026-01-30 01:14:28.705988
576	67	61	19	"b"	f	-0.40494025366974645	-0.296687868013535	2026-01-30 01:17:14.357389
566	69	282	40	"a"	f	-0.9189994853597819	-0.9243266684247676	2026-01-30 01:14:30.082937
567	69	55	41	"a"	f	-0.9627624655974276	-0.9876562705324669	2026-01-30 01:14:31.787749
568	69	31	42	"c"	t	-1.011983556118005	-0.9426213460767717	2026-01-30 01:14:36.072302
569	69	3	43	\N	\N	\N	\N	2026-01-30 01:15:07.360789
577	67	63	20	"c"	t	-0.41157697082700595	-0.3994047845698536	2026-01-30 01:17:17.095227
518	67	5	12	"a"	f	-0.4395215419793976	-0.43853806570703663	2026-01-30 00:59:12.319809
570	67	58	13	"b"	t	-0.5077190665837722	-0.44460309752672705	2026-01-30 01:16:54.310984
571	67	25	14	"b"	f	-0.4929955838929481	-0.3104022650996059	2026-01-30 01:17:06.172885
578	67	21	21	"c"	t	-0.40811679490779035	-0.33850505974951606	2026-01-30 01:17:27.712368
572	67	48	15	"b"	t	-0.5125427725295086	-0.44079831858763635	2026-01-30 01:17:08.262237
587	67	28	30	"a"	t	-0.34119597451018185	-0.338822996500987	2026-01-30 01:18:03.212526
579	67	57	22	"c"	f	-0.38753354487948827	-0.23912347974780604	2026-01-30 01:17:29.595106
580	67	366	23	"c"	f	-0.37264132342304634	-0.27830390835890767	2026-01-30 01:17:32.93353
598	70	15	2	"A"	t	0.4097501051939517	0.1852070723182594	2026-01-30 10:39:06.468945
581	67	38	24	"b"	t	-0.40275601415931583	-0.3247377854134427	2026-01-30 01:17:34.291282
588	67	30	31	"a"	t	-0.3332933665805014	-0.2363332606580859	2026-01-30 01:18:16.862703
582	67	44	25	"b"	t	-0.4012691982424275	-0.2486703617254164	2026-01-30 01:17:45.588982
583	67	152	26	"b"	f	-0.32079604804190653	-0.23718001974155944	2026-01-30 01:17:48.039911
584	67	100	27	"b"	f	-0.32079604804190653	-0.23718001974155944	2026-01-30 01:17:55.939405
589	67	110	32	"a"	t	-0.3332933665805014	-0.2363332606580859	2026-01-30 01:18:20.005378
590	67	102	33	"a"	f	-0.3332933665805014	-0.2363332606580859	2026-01-30 01:18:31.06951
594	67	16	37	"a"	f	-0.44504764692734144	-0.21623721960553802	2026-01-30 01:18:37.211877
591	67	12	34	"a"	f	-0.3344556925813512	-0.20620026735159316	2026-01-30 01:18:32.558288
592	67	101	35	"a"	t	-0.3344556925813512	-0.20620026735159316	2026-01-30 01:18:34.254562
600	70	36	4	"B"	t	0.788234609825408	0.8126138172742831	2026-01-30 10:39:09.673819
595	67	60	38	"b"	t	-0.4888075858931619	-0.21292119438220572	2026-01-30 01:18:38.957927
596	67	8	39	\N	\N	\N	\N	2026-01-30 01:18:46.86323
597	70	208	1	"B"	t	0	0	2026-01-30 10:39:02.100511
601	70	19	5	\N	\N	\N	\N	2026-01-30 10:39:57.808858
599	70	152	3	"A"	t	0.6255492903639978	0.2847981740491349	2026-01-30 10:39:08.634907
602	71	208	1	"C"	f	0	0	2026-01-30 10:52:09.706633
603	71	15	2	"A"	t	-0.37158342300721287	-0.17754352996861597	2026-01-30 10:52:14.119825
604	71	204	3	"B"	f	0.003448382843283717	-0.0037923039211082005	2026-01-30 10:52:15.427391
605	71	14	4	"A"	t	-0.35248773207900086	-0.18982380648261393	2026-01-30 10:52:19.683675
606	71	2	5	"C"	f	-0.11673667778893507	-0.05796963973513962	2026-01-30 10:52:21.242717
607	71	43	6	"A"	t	-0.2815497165137677	-0.16417464918019353	2026-01-30 10:52:23.094275
608	71	49	7	"A"	f	-0.1125004961055055	-0.03419065115846029	2026-01-30 10:52:24.979839
609	71	36	8	"A"	f	-0.2832742842777183	-0.12075945851983137	2026-01-30 10:52:26.406751
610	71	42	9	"A"	f	-0.3202104573005548	-0.4359702687665517	2026-01-30 10:52:27.284971
611	71	33	10	"A"	t	-0.4376102549039861	-0.43988550882436667	2026-01-30 10:52:28.043092
612	71	27	11	"A"	f	-0.39043848042988016	-0.2625296217225533	2026-01-30 10:52:28.916719
613	71	5	12	"A"	f	-0.43676451837179464	-0.45091347782807617	2026-01-30 10:52:29.752524
687	74	102	6	"C"	t	0.892397086090626	0.8295366348966209	2026-01-30 11:15:47.908308
614	71	58	13	"A"	f	-0.5245814160374366	-0.4650056259512222	2026-01-30 10:52:31.791613
615	71	112	14	"A"	f	-0.5245814160374366	-0.4650056259512222	2026-01-30 10:52:32.565871
653	72	7	22	"A"	f	-0.6896260226089698	0.2705960091883417	2026-01-30 10:58:22.394971
616	71	25	15	"A"	f	-0.5239645764414713	-0.6472859131074253	2026-01-30 10:52:34.637086
617	71	9	16	"A"	t	-0.5619786070490292	-0.7543411721792687	2026-01-30 10:52:36.147264
675	72	30	44	"A"	t	-0.9873252511614651	-0.21194480332198307	2026-01-30 10:59:07.589804
618	71	63	17	"A"	f	-0.4197538434736787	-0.7222495474357491	2026-01-30 10:52:37.782611
619	71	100	18	"A"	t	-0.4197538434736787	-0.7222495474357491	2026-01-30 10:52:39.194758
654	72	58	23	"A"	f	-0.7545179879749834	0.2840903444136126	2026-01-30 10:58:24.722497
620	71	7	19	"A"	f	-0.4511235202439415	-0.8701644751205354	2026-01-30 10:52:39.717601
655	72	61	24	"A"	t	-0.7913691955617164	0.11900655065104414	2026-01-30 10:58:26.044773
621	71	4	20	"A"	f	-0.5788083956215869	-0.8681154462188632	2026-01-30 10:52:41.245197
623	71	30	22	\N	\N	\N	\N	2026-01-30 10:52:42.430248
622	71	48	21	"A"	f	-0.5833856838473885	-0.9169854048600568	2026-01-30 10:52:41.880315
624	71	108	23	"A"	f	-0.5833856838473885	-0.9169854048600568	2026-01-30 10:52:42.970947
656	72	111	25	"A"	f	-0.7913691955617164	0.11900655065104414	2026-01-30 10:58:29.414601
625	71	44	24	"A"	f	-0.5598399833914206	-0.9659357889747343	2026-01-30 10:52:43.682555
626	71	109	25	\N	\N	\N	\N	2026-01-30 10:52:45.194198
627	72	208	1	"B"	t	0	0	2026-01-30 10:54:26.598871
629	73	208	1	"A"	f	0	0	2026-01-30 10:54:45.791488
630	73	15	2	"B"	f	-0.36753121792839305	-0.18284368228753878	2026-01-30 10:54:47.474844
628	72	15	2	"A"	t	0.4057505095120575	0.21938170181302166	2026-01-30 10:54:35.177475
657	72	48	26	"A"	f	-0.7635812412240137	0.1461093558539165	2026-01-30 10:58:30.889223
632	72	152	3	"A"	t	0.6128932341117853	0.29749299293496984	2026-01-30 10:54:55.381529
631	73	204	3	"B"	f	-0.580416492419973	-0.2850300889648732	2026-01-30 10:54:52.178877
634	73	107	4	\N	\N	\N	\N	2026-01-30 10:55:04.162873
658	72	104	27	"A"	f	-0.7635812412240137	0.1461093558539165	2026-01-30 10:58:32.745471
633	72	36	4	"B"	t	0.7614710070734502	0.8019162678650991	2026-01-30 10:54:58.563017
635	72	19	5	["A", "B"]	f	0.7829801010337533	0.908125018982643	2026-01-30 10:57:13.658213
676	72	13	45	"A"	f	-0.9506728015985607	-0.25215892305445575	2026-01-30 10:59:09.449964
636	72	369	6	["A", "C"]	f	0.7437667527104596	0.7492844506244536	2026-01-30 10:57:26.154006
637	72	109	7	"A"	f	0.7437667527104596	0.7492844506244536	2026-01-30 10:57:31.743708
659	72	4	28	"A"	f	-0.7751785750326639	0.04623012897146161	2026-01-30 10:58:33.637492
638	72	366	8	["B", "C"]	f	0.6842572656615559	0.5649611889891017	2026-01-30 10:57:38.905518
639	72	14	9	"C"	f	0.6645062856383831	0.44826618284990716	2026-01-30 10:57:45.801168
652	72	27	21	"A"	f	-0.8385883228939708	0.04030801797626986	2026-01-30 10:58:21.970783
640	72	57	10	["A", "B", "C"]	t	0.30246633429490727	0.33121812340771	2026-01-30 10:57:50.142453
641	72	43	11	"C"	f	0.33143005914155266	0.4550498292875504	2026-01-30 10:58:01.42772
642	72	9	12	"D"	f	0.13422484898828577	0.4372037963287669	2026-01-30 10:58:05.861384
643	72	110	13	"A"	t	0.13422484898828577	0.4372037963287669	2026-01-30 10:58:09.208488
644	72	2	14	"A"	f	-0.03290364878825097	0.41349010555664134	2026-01-30 10:58:16.662344
645	72	106	15	"A"	t	-0.03290364878825097	0.41349010555664134	2026-01-30 10:58:18.225857
660	72	33	29	"A"	t	-0.8379232721527472	-0.07892298860094933	2026-01-30 10:58:35.353104
646	72	204	16	"A"	f	-0.1606952096303206	0.3806534872360739	2026-01-30 10:58:18.32424
647	72	49	17	"A"	f	-0.3535330238705577	0.32529620610351284	2026-01-30 10:58:18.763302
662	72	100	31	"A"	t	-0.8379232721527472	-0.07892298860094933	2026-01-30 10:58:41.214009
677	72	12	46	"A"	f	-1.0174246678244303	-0.2169093915421874	2026-01-30 10:59:11.85913
649	72	101	19	"A"	t	-0.4775541041852178	0.32401584367459985	2026-01-30 10:58:19.860363
648	72	42	18	"A"	f	-0.5436197189953241	0.30943464521301134	2026-01-30 10:58:19.28949
663	72	25	32	"A"	f	-0.8519308699909043	-0.04129385905006402	2026-01-30 10:58:42.508515
650	72	5	20	"A"	f	-0.5547774489308701	0.322462108261766	2026-01-30 10:58:20.335655
651	72	5	20	"A"	f	-0.6382812392906152	0.27963983223349675	2026-01-30 10:58:20.345008
664	72	21	33	"C"	t	-0.8463727294444249	-0.1573113685952154	2026-01-30 10:58:44.23363
688	74	19	7	["A", "B", "D"]	t	0.9720772459195935	1.0957230570802603	2026-01-30 11:16:03.705772
665	72	63	34	"A"	f	-0.82267630989283	-0.09656670125118949	2026-01-30 10:58:49.730131
666	72	108	35	"A"	f	-0.82267630989283	-0.09656670125118949	2026-01-30 10:58:51.558389
678	72	55	47	"A"	f	-1.0308035020886772	-0.18669939071203118	2026-01-30 10:59:14.64172
667	72	38	36	"A"	f	-0.8576760511582809	-0.18256097314148662	2026-01-30 10:58:52.438777
668	72	44	37	"A"	f	-0.881481208379899	-0.27166383202029853	2026-01-30 10:58:55.264932
661	72	33	30	"A"	t	-0.8817891084059892	-0.2285420845372498	2026-01-30 10:58:36.635945
679	72	282	48	"A"	f	-1.0658096903045533	-0.20077470762445324	2026-01-30 10:59:16.419533
669	72	26	39	"A"	f	-0.8804790151107487	-0.1992818807348421	2026-01-30 10:58:58.727023
670	72	26	38	"A"	f	-0.9087533258983023	-0.2655534581612577	2026-01-30 10:58:57.511785
671	72	105	41	\N	\N	\N	\N	2026-01-30 10:59:00.649276
694	74	2	13	"B"	t	0.6916373672864693	1.3928004216197625	2026-01-30 11:16:54.356605
672	72	28	40	"A"	t	-0.9305842823405726	-0.326053820858506	2026-01-30 10:58:59.749441
680	72	60	49	"A"	f	-1.1337623986913994	-0.23285873302411922	2026-01-30 10:59:18.221908
673	72	16	42	"A"	f	-0.9275385502936325	-0.26183483386994655	2026-01-30 10:59:02.362864
674	72	112	43	"A"	f	-0.9275385502936325	-0.26183483386994655	2026-01-30 10:59:04.022388
689	74	223	8	"A"	f	0.9958688045443164	1.3242970359288366	2026-01-30 11:16:09.736417
681	72	23	50	"A"	f	-1.0996702244260985	-0.30307165990196383	2026-01-30 10:59:19.903471
682	74	208	1	"B"	t	0	0	2026-01-30 11:09:03.927761
683	74	14	2	"A"	t	0.4242312259004201	0.1934996271092957	2026-01-30 11:15:08.019131
684	74	152	3	"A"	t	0.576176154419141	0.272198427888307	2026-01-30 11:15:17.822208
690	74	326	9	"B"	t	0.8435182683944027	1.2671916656437157	2026-01-30 11:16:11.780413
685	74	15	4	"A"	t	0.7321804859913019	0.8093118792210808	2026-01-30 11:15:26.925991
686	74	369	5	["A", "D"]	t	0.892397086090626	0.8295366348966209	2026-01-30 11:15:34.219546
698	74	5	17	"A"	f	0.580317192592576	1.4222266776963859	2026-01-30 11:17:41.808573
691	74	43	10	"A"	t	0.8723689783553141	1.3532749303427438	2026-01-30 11:16:26.39325
695	74	7	14	"B"	t	0.7377229346120837	1.3875708666259958	2026-01-30 11:17:28.427088
692	74	9	11	"B"	f	0.904364563639674	1.3869422446606563	2026-01-30 11:16:28.527946
693	74	366	12	["B", "D"]	t	0.6769279830583965	1.3419940948216622	2026-01-30 11:16:31.722793
696	74	4	15	"A"	f	0.7861908011061127	1.4017417882207466	2026-01-30 11:17:34.81545
701	74	104	20	"A"	f	0.2646534493557258	1.3488086820554301	2026-01-30 11:17:46.332438
697	74	57	16	["A", "B", "C"]	t	0.5698179002231561	1.3538925558704011	2026-01-30 11:17:36.730178
699	74	42	18	"A"	f	0.4096906383385749	1.3475088353764733	2026-01-30 11:17:43.331879
700	74	49	19	"A"	f	0.2646534493557258	1.3488086820554301	2026-01-30 11:17:45.016543
702	74	204	21	"A"	f	0.12185680556869843	1.3210704029134483	2026-01-30 11:17:47.301786
703	74	44	22	"A"	f	-0.030284592397030394	1.2816420532060289	2026-01-30 11:17:48.671731
704	74	12	23	"A"	f	-0.09972793776529315	1.2522508800624832	2026-01-30 11:17:50.763168
705	74	8	24	"A"	f	-0.1592130810794956	1.2984528527848191	2026-01-30 11:17:52.445204
706	74	13	25	"A"	f	-0.21150034267633036	1.1898337096962632	2026-01-30 11:17:55.085347
707	74	282	26	"A"	f	-0.2520979078431899	1.2432087912618237	2026-01-30 11:17:56.860326
708	74	16	27	"A"	f	-0.31294954008040965	1.1749522040569416	2026-01-30 11:17:58.610608
709	74	101	28	"A"	t	-0.31294954008040965	1.1749522040569416	2026-01-30 11:18:00.527562
710	74	108	29	"A"	f	-0.31294954008040965	1.1749522040569416	2026-01-30 11:18:01.821307
711	74	28	30	"A"	t	-0.37691169288127446	1.2728046814614313	2026-01-30 11:18:03.132567
712	74	112	31	"A"	f	-0.37691169288127446	1.2728046814614313	2026-01-30 11:18:06.41494
713	74	10	32	"A"	f	-0.3623037150842955	1.2246822546773004	2026-01-30 11:18:16.895313
714	74	313	33	"A"	f	-0.4143516871556478	1.2311487996477413	2026-01-30 11:18:18.484806
715	74	100	34	"A"	t	-0.4143516871556478	1.2311487996477413	2026-01-30 11:18:20.050454
717	75	208	1	"a"	f	0	0	2026-01-30 11:22:03.124533
786	76	27	40	"D"	t	2.0567856411318712	1.7108953187540432	2026-01-30 11:29:54.126364
718	75	15	2	"a"	t	-0.3670845028207809	-0.17691944773235035	2026-01-30 11:22:20.518597
753	76	369	7	["A", "C"]	f	0.9745558896755679	1.1317810395051222	2026-01-30 11:25:33.107972
719	75	204	3	"a"	f	0.013347944834509217	-0.008091305310746826	2026-01-30 11:22:22.653251
720	75	14	4	"a"	t	-0.33072667281725604	-0.17183976550562396	2026-01-30 11:22:24.191576
754	76	102	8	"C"	t	0.9745558896755679	1.1317810395051222	2026-01-30 11:25:39.646475
721	75	2	5	"a"	f	-0.12386265865147311	-0.07336155800194012	2026-01-30 11:22:26.448291
722	75	111	6	"a"	f	-0.12386265865147311	-0.07336155800194012	2026-01-30 11:22:27.758016
723	75	36	7	"a"	f	-0.29452826115582065	-0.11406631355061826	2026-01-30 11:22:28.635734
774	76	21	28	"C"	t	1.685496683296086	1.6505043232411505	2026-01-30 11:28:22.701519
724	75	27	8	"a"	f	-0.34636065918759645	-0.4497469707633678	2026-01-30 11:22:29.628729
725	75	105	9	"a"	f	-0.34636065918759645	-0.4497469707633678	2026-01-30 11:22:49.478452
726	75	101	10	"a"	t	-0.34636065918759645	-0.4497469707633678	2026-01-30 11:22:50.250464
755	76	223	9	"D"	t	0.87387428249521	0.9264258369471587	2026-01-30 11:25:43.691203
727	75	33	11	"a"	t	-0.37705866619031225	-0.6644586516240101	2026-01-30 11:22:51.022423
728	75	25	12	"a"	f	-0.3315958289736191	-0.41892354909695845	2026-01-30 11:22:55.620734
729	75	58	13	"a"	f	-0.37691648853227444	-0.6218365059107905	2026-01-30 11:22:58.156408
756	76	366	10	["B", "D"]	t	1.1277931911419417	0.9915737085957966	2026-01-30 11:25:52.514419
730	75	49	14	"a"	f	-0.37273976588836755	-0.7121257161472851	2026-01-30 11:23:00.67591
731	75	42	15	\N	\N	\N	\N	2026-01-30 11:23:01.779207
716	74	372	35	["A"]	f	-0.38959040674344636	1.1701624913092674	2026-01-30 11:18:21.321442
732	74	3	36	"A"	f	-0.4048017158613677	1.0780514505225194	2026-01-30 11:23:42.86746
757	76	326	11	"B"	t	1.1589764168608339	1.0822444416094494	2026-01-30 11:26:05.364469
733	74	55	37	"A"	f	-0.4581355122763845	1.0918312600393119	2026-01-30 11:23:44.613306
734	74	61	38	"A"	t	-0.481043502007012	1.06441147319557	2026-01-30 11:23:46.71177
775	76	10	29	"C"	t	1.7035701842191684	1.5858046075079477	2026-01-30 11:28:35.718282
735	74	36	39	"A"	f	-0.5184947884218805	1.0843980782830518	2026-01-30 11:23:51.340086
758	76	9	12	"A"	t	1.1651934047462602	1.1797156008888163	2026-01-30 11:26:16.81706
736	74	27	40	"A"	f	-0.49598745096281743	0.9159366682250044	2026-01-30 11:23:53.365414
737	74	21	41	"A"	f	-0.5167823184667689	0.7429297865479546	2026-01-30 11:23:55.197231
759	76	104	13	"C"	t	1.1651934047462602	1.1797156008888163	2026-01-30 11:26:24.251255
738	74	58	42	"A"	f	-0.5454230058405076	0.6165199444280036	2026-01-30 11:24:03.897198
739	74	48	43	"C"	f	-0.5364171209312159	0.49060897162995465	2026-01-30 11:24:07.709981
740	74	38	44	"A"	f	-0.5450015998101341	0.37870658022412895	2026-01-30 11:24:11.86222
760	76	57	14	["A", "B", "C"]	t	1.224319774361368	1.1877635505726654	2026-01-30 11:26:31.488925
741	74	26	45	"A"	f	-0.5906213161647558	0.2906400439915141	2026-01-30 11:24:15.20367
743	74	25	47	\N	\N	\N	\N	2026-01-30 11:24:22.021249
761	76	28	15	"A"	t	1.2210588930519821	1.2335044473047654	2026-01-30 11:26:40.77351
742	74	33	46	"A"	t	-0.5552237018914636	0.23193321131875377	2026-01-30 11:24:17.054098
744	74	63	48	"A"	f	-0.5767186959605843	0.24527775298915871	2026-01-30 11:24:22.981374
776	76	36	30	"B"	t	1.7112182370562043	1.6618242547598647	2026-01-30 11:28:39.636196
745	74	23	49	"A"	f	-0.547608574614134	0.13549431402100143	2026-01-30 11:24:25.000641
762	76	313	16	"B"	t	1.257829101471634	1.244878458543103	2026-01-30 11:26:43.426339
746	74	60	50	"A"	f	-0.5647234614635666	0.0752960342347337	2026-01-30 11:24:26.872111
747	76	208	1	"B"	t	0	0	2026-01-30 11:24:35.601163
748	76	15	2	"A"	t	0.43317948267056255	0.21022838022622448	2026-01-30 11:24:38.750123
749	76	152	3	"A"	t	0.612797081185015	0.3294517750825829	2026-01-30 11:24:40.263404
750	76	108	4	"B"	t	0.612797081185015	0.3294517750825829	2026-01-30 11:25:07.963501
763	76	261	17	"D"	t	1.2868651064039838	1.3755159900390292	2026-01-30 11:26:54.457617
751	76	14	5	"A"	t	0.7667380889587615	0.8174530407196139	2026-01-30 11:25:20.391526
752	76	19	6	["A", "B", "D"]	t	0.8597405296247975	0.8152903446832821	2026-01-30 11:25:22.70201
787	76	29	41	"C"	t	2.0387119631907944	1.6945617484497804	2026-01-30 11:29:59.64161
764	76	43	18	"A"	t	1.3774059302882533	1.4105713026223012	2026-01-30 11:27:03.845911
777	76	209	31	"C"	t	1.7611931454141572	1.6046488974247484	2026-01-30 11:28:44.952424
765	76	372	19	["A", "D"]	t	1.421875803301919	1.3989520759331857	2026-01-30 11:27:06.668479
766	76	61	20	"A"	t	1.4128198408516737	1.4709968720095936	2026-01-30 11:27:27.826362
767	76	8	21	"B"	t	1.4474480219121222	1.4763226864451584	2026-01-30 11:27:31.721721
778	76	23	32	"B"	t	1.8597737784091517	1.7116284231982948	2026-01-30 11:28:55.300274
768	76	47	22	"A"	t	1.4735605579645035	1.4909031335089717	2026-01-30 11:27:35.185516
769	76	17	23	"C"	t	1.475936986459788	1.5034386877596	2026-01-30 11:27:44.418896
770	76	189	24	"D"	t	1.6401588729885144	1.5319976213128588	2026-01-30 11:27:48.11888
779	76	54	33	"A"	t	1.8554083493943816	1.7080826949410477	2026-01-30 11:28:59.172111
771	76	321	25	"B"	t	1.6513654998853293	1.5266243639844979	2026-01-30 11:27:58.996407
772	76	32	26	"A"	t	1.696968585673045	1.5381993687556432	2026-01-30 11:28:06.322197
788	76	48	42	"B"	t	2.0752146431346157	1.8115701624220224	2026-01-30 11:30:12.176662
773	76	38	27	"B"	t	1.7059910941806142	1.5712915134499597	2026-01-30 11:28:18.710322
780	76	254	34	"A"	t	1.8373322049968686	1.7548928907835144	2026-01-30 11:29:04.018986
781	76	26	35	"C"	t	2.0090678964532853	1.7332103118836328	2026-01-30 11:29:14.063212
794	76	268	48	"D"	t	2.286737769089729	1.9358656282556164	2026-01-30 11:30:58.426708
782	76	70	36	"B"	t	1.885561862273419	1.7420026646761362	2026-01-30 11:29:19.444158
789	76	37	43	"C"	t	2.1092617424795406	1.8869670232889346	2026-01-30 11:30:15.366591
783	76	41	37	"C"	t	2.1606609593951607	1.7991198831054946	2026-01-30 11:29:24.76996
784	76	65	38	"B"	t	2.002627470618444	1.798371145499951	2026-01-30 11:29:37.432367
785	76	53	39	"B"	t	2.104761143303045	1.7696983349368873	2026-01-30 11:29:50.189406
790	76	20	44	"B"	t	2.208212923804541	1.8746531244772418	2026-01-30 11:30:19.398227
795	76	56	49	"C"	t	2.255530605756764	1.9619866898442784	2026-01-30 11:31:09.72126
791	76	62	45	"C"	t	2.2809022423941565	1.8881970625552624	2026-01-30 11:30:30.506049
792	76	22	46	"D"	t	2.134074961269629	1.873709684971742	2026-01-30 11:30:40.88769
799	78	15	2	"A"	t	-0.3625720269817973	-0.1848328535480918	2026-01-30 13:49:30.261116
793	76	24	47	"B"	t	2.214672123312882	1.9248198575844842	2026-01-30 11:30:48.918318
796	76	52	50	"B"	t	2.189315415553187	1.9095624781285387	2026-01-30 11:31:15.25957
798	78	208	1	"A"	f	0	0	2026-01-30 13:49:28.215081
797	77	208	1	"B"	t	0	0	2026-01-30 13:49:23.385096
801	78	204	3	\N	\N	\N	\N	2026-01-30 13:57:16.03691
803	79	208	1	"A"	f	0	0	2026-01-30 13:57:32.944441
800	77	15	2	"C"	f	0.4309533055858173	0.21295512917911283	2026-01-30 13:54:51.842533
802	77	152	3	\N	\N	\N	\N	2026-01-30 13:57:19.52859
804	80	208	1	"A"	f	0	0	2026-01-30 13:57:35.649242
805	79	15	2	"A"	t	-0.36593421417715877	-0.1728141580176812	2026-01-30 13:57:38.388804
808	80	204	3	\N	\N	\N	\N	2026-01-30 14:09:16.646544
806	80	15	2	"C"	f	-0.3732274159584525	-0.20076352470934103	2026-01-30 13:57:40.469403
809	81	208	1	"A"	f	0	0	2026-01-30 14:09:28.788511
810	81	15	2	"A"	t	-0.3998499794518989	-0.2119282321167697	2026-01-30 14:09:30.659446
811	81	204	3	"A"	f	0.005914894395993698	-0.006729064409712104	2026-01-30 14:09:32.712246
807	79	204	3	"C"	t	-0.006335927035694673	-0.021416342742532516	2026-01-30 14:09:10.565939
813	79	14	4	"A"	t	0.1253289756127272	0.05279097426629256	2026-01-30 14:09:38.772137
812	81	14	4	"D"	f	-0.34908141244005897	-0.15910389546909542	2026-01-30 14:09:34.384396
815	81	2	5	"A"	f	-0.47073007882581186	-0.24663079772772625	2026-01-30 14:09:47.854807
816	81	109	6	"D"	t	-0.47073007882581186	-0.24663079772772625	2026-01-30 14:09:54.653872
819	81	110	9	"A"	t	-0.6088400418504086	-0.3131142974741167	2026-01-30 14:10:15.383573
814	79	43	5	"A"	t	0.27451253382645024	0.154177735585008	2026-01-30 14:09:40.831133
821	79	109	6	"A"	f	0.27451253382645024	0.154177735585008	2026-01-30 14:18:27.003506
820	81	27	10	"A"	f	-0.5550506605708291	0.045354597601994985	2026-01-30 14:18:24.755991
824	81	58	12	"B"	t	-0.5122503284313843	0.2156034638297012	2026-01-30 14:18:41.685436
822	79	152	7	"A"	t	0.398254263776541	0.19802145143945546	2026-01-30 14:18:30.960457
826	79	36	8	"B"	t	0.506947851740075	0.7017051837296984	2026-01-30 14:21:25.878178
825	81	366	13	["A"]	f	-0.4885511106033225	0.3182934884542006	2026-01-30 14:18:56.512406
828	81	49	14	"A"	f	-0.5041152297701872	0.19508352023523262	2026-01-30 14:21:34.412184
827	79	369	9	["A", "C"]	f	0.5218219335638392	0.7942068555474447	2026-01-30 14:21:30.948486
830	79	19	10	["B"]	f	0.4921619359216315	0.6511231734386226	2026-01-30 14:21:40.224533
829	81	42	15	"A"	f	-0.6744146404460821	0.13405646896058032	2026-01-30 14:21:36.153366
817	81	36	7	"B"	t	-0.6088400418504086	-0.3131142974741167	2026-01-30 14:10:02.750247
818	81	100	8	"A"	t	-0.6088400418504086	-0.3131142974741167	2026-01-30 14:10:14.560222
823	81	152	11	"A"	t	-0.5873362214750488	-0.22387706360996543	2026-01-30 14:18:33.207164
832	81	5	16	"A"	f	-0.7696704958032917	0.13195001138398726	2026-01-30 14:25:47.203129
831	79	112	11	"A"	f	0.4921619359216315	0.6511231734386226	2026-01-30 14:22:27.425673
869	83	63	14	"A"	f	-1.1633970922487982	-0.9058495498727062	2026-01-30 15:06:42.969133
834	79	366	12	["A"]	f	0.46710839327560705	0.527793196587219	2026-01-30 14:25:52.655386
833	81	57	17	["A", "B", "D"]	f	-0.8102527449662098	0.15393752692168047	2026-01-30 14:25:49.632142
836	81	61	18	"A"	t	-0.8414014642952089	0.04668306534447551	2026-01-30 14:29:05.165871
835	79	106	13	"A"	t	0.46710839327560705	0.527793196587219	2026-01-30 14:25:56.830904
870	83	48	15	"A"	f	-1.1725585684940578	-1.0394197292085485	2026-01-30 15:06:44.342402
837	81	48	19	"A"	f	-0.8167635285895617	0.16041546397996356	2026-01-30 14:29:08.392212
839	81	7	20	"A"	f	-0.8300586673522473	-0.027053417729149338	2026-01-30 14:38:06.319959
840	81	33	21	"A"	t	-0.8916133233616872	-0.034235361601619343	2026-01-30 14:38:07.341361
871	83	30	16	"A"	t	-1.1723049314398504	-1.0911667155910414	2026-01-30 15:06:46.032431
838	79	9	14	"B"	f	0.42272374132678425	0.3829216253341201	2026-01-30 14:29:15.085201
842	79	57	15	\N	\N	\N	\N	2026-01-30 14:56:05.226141
841	81	25	22	"A"	f	-0.9171212440747812	0.055998385831921	2026-01-30 14:38:11.815737
843	81	21	23	"A"	f	-0.9591959487228573	-0.1245601590357986	2026-01-30 14:57:31.449356
872	83	2	17	"A"	f	-1.2068739440704739	-0.9850104531426804	2026-01-30 15:07:46.854792
844	81	38	24	"A"	f	-0.928730585466477	-0.19668141306510387	2026-01-30 14:57:36.543948
845	81	63	25	"A"	f	-0.9338436165849296	-0.26642467919637247	2026-01-30 14:57:40.66331
846	81	4	26	"A"	f	-0.9450434853126912	-0.3738857731516155	2026-01-30 14:57:42.507597
873	83	5	18	"A"	f	-1.222927398252635	-0.9641254515093425	2026-01-30 15:07:49.102384
847	81	44	27	"A"	f	-1.0046824601434186	-0.3555996327367642	2026-01-30 14:57:44.450663
848	81	26	28	"A"	f	-1.0784170138323736	-0.38017099274458277	2026-01-30 14:57:45.821473
849	81	30	29	\N	\N	\N	\N	2026-01-30 14:57:47.178719
850	82	208	1	"A"	f	0	0	2026-01-30 15:05:35.372735
852	83	208	1	"A"	f	0	0	2026-01-30 15:05:40.08222
853	83	15	2	"D"	f	-0.38833589264662943	-0.17182088970870754	2026-01-30 15:05:46.593169
874	83	16	19	"A"	f	-1.2996948651707214	-1.0033612532827252	2026-01-30 15:07:51.21443
851	82	15	2	"A"	t	-0.3786727006663119	-0.18146055194665855	2026-01-30 15:05:37.437864
875	83	60	20	\N	\N	\N	\N	2026-01-30 15:07:55.09073
854	83	204	3	"A"	f	-0.5804277400945135	-0.2979369985329796	2026-01-30 15:05:48.757959
855	82	204	3	"C"	t	-0.00017504870543229344	0.0071768204403667175	2026-01-30 15:05:51.550441
856	83	105	4	"A"	f	-0.5804277400945135	-0.2979369985329796	2026-01-30 15:05:54.553195
857	82	14	4	"A"	t	0.1297486841101935	0.0836753630548224	2026-01-30 15:05:59.241739
858	83	49	5	"A"	f	-0.819609161413014	-0.42090570258209703	2026-01-30 15:06:02.814987
859	82	43	5	"A"	t	0.27673980236749174	0.12151596524515493	2026-01-30 15:06:05.956206
861	82	152	6	\N	\N	\N	\N	2026-01-30 15:06:15.032361
860	83	42	6	"A"	f	-0.9989366395686688	-0.4762645031641116	2026-01-30 15:06:10.334791
862	83	33	7	"A"	t	-1.0859002014993142	-0.5417278395749837	2026-01-30 15:06:21.01268
863	83	107	8	"A"	t	-1.0859002014993142	-0.5417278395749837	2026-01-30 15:06:31.904775
864	83	58	9	"A"	f	-1.0240237269223271	-0.28697444127749006	2026-01-30 15:06:35.988014
865	83	108	10	"A"	f	-1.0240237269223271	-0.28697444127749006	2026-01-30 15:06:37.183979
866	83	36	11	"A"	f	-1.075901916901535	-0.4955293458074897	2026-01-30 15:06:38.303212
867	83	27	12	"A"	f	-1.1202208887133727	-0.6683681556845903	2026-01-30 15:06:40.350916
868	83	25	13	"A"	f	-1.16435191324506	-0.8161510758967672	2026-01-30 15:06:41.845824
876	84	208	1	\N	\N	\N	\N	2026-02-06 15:06:33.716868
877	85	208	1	\N	\N	\N	\N	2026-02-06 15:08:14.541728
878	86	208	1	\N	\N	\N	\N	2026-02-06 15:21:24.445685
\.


--
-- Name: exam_sessions_session_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exam_sessions_session_id_seq', 86, true);


--
-- Name: responses_response_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.responses_response_id_seq', 878, true);


--
-- Name: exam_sessions exam_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exam_sessions
    ADD CONSTRAINT exam_sessions_pkey PRIMARY KEY (session_id);


--
-- Name: questions questions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.questions
    ADD CONSTRAINT questions_pkey PRIMARY KEY (unique_id);


--
-- Name: responses responses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.responses
    ADD CONSTRAINT responses_pkey PRIMARY KEY (response_id);


--
-- Name: idx_concept_tag; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_concept_tag ON public.questions USING btree (concept_tag);


--
-- Name: idx_domain; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_domain ON public.questions USING btree (domain);


--
-- Name: idx_question_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_question_type ON public.questions USING btree (question_type);


--
-- Name: idx_questions_calibration; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_questions_calibration ON public.questions USING btree (calibration_status);


--
-- Name: idx_questions_concept_tag; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_questions_concept_tag ON public.questions USING btree (concept_tag);


--
-- Name: idx_questions_domain; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_questions_domain ON public.questions USING btree (domain);


--
-- Name: idx_questions_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_questions_type ON public.questions USING btree (question_type);


--
-- Name: questions update_questions_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_questions_updated_at BEFORE UPDATE ON public.questions FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: responses responses_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.responses
    ADD CONSTRAINT responses_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.exam_sessions(session_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict DWdRjj1jwiNQZsmmhenCdcXrbuMlGI64iiJJbiDFS7bo8RgM93BGbgIGhcTgkIh

