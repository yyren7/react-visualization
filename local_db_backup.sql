--
-- PostgreSQL database dump
--

-- Dumped from database version 14.15 (Ubuntu 14.15-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.15 (Ubuntu 14.15-0ubuntu0.22.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: chat_histories; Type: TABLE; Schema: public; Owner: otocolobus
--

CREATE TABLE public.chat_histories (
    chat_history_id uuid NOT NULL,
    user_id uuid,
    action_time timestamp with time zone,
    action_type character varying(255),
    action_description text
);


ALTER TABLE public.chat_histories OWNER TO otocolobus;

--
-- Name: chats; Type: TABLE; Schema: public; Owner: otocolobus
--

CREATE TABLE public.chats (
    chat_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid,
    start_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    end_time timestamp with time zone,
    session_status character varying(50) DEFAULT 'ongoing'::character varying,
    chat_history_id uuid
);


ALTER TABLE public.chats OWNER TO otocolobus;

--
-- Name: edges; Type: TABLE; Schema: public; Owner: otocolobus
--

CREATE TABLE public.edges (
    edge_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    flowchart_id uuid NOT NULL,
    source_node_id uuid NOT NULL,
    target_node_id uuid NOT NULL,
    edge_type character varying(50) DEFAULT 'sequential'::character varying,
    description text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    edge_label character varying(255)
);


ALTER TABLE public.edges OWNER TO otocolobus;

--
-- Name: flowchart_histories; Type: TABLE; Schema: public; Owner: otocolobus
--

CREATE TABLE public.flowchart_histories (
    history_id uuid NOT NULL,
    history_name character varying(255),
    history_description text
);


ALTER TABLE public.flowchart_histories OWNER TO otocolobus;

--
-- Name: flowcharts; Type: TABLE; Schema: public; Owner: otocolobus
--

CREATE TABLE public.flowcharts (
    flowchart_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    flowchart_name character varying(255) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    global_parameters jsonb,
    flowchat_history_id uuid
);


ALTER TABLE public.flowcharts OWNER TO otocolobus;

--
-- Name: messages; Type: TABLE; Schema: public; Owner: otocolobus
--

CREATE TABLE public.messages (
    message_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    chat_id uuid NOT NULL,
    message_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    message_role character varying(50) NOT NULL,
    message_content text NOT NULL
);


ALTER TABLE public.messages OWNER TO otocolobus;

--
-- Name: nodes; Type: TABLE; Schema: public; Owner: otocolobus
--

CREATE TABLE public.nodes (
    node_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    flowchart_id uuid NOT NULL,
    node_type character varying(50) NOT NULL,
    api_name character varying(100) NOT NULL,
    parameters jsonb,
    description text,
    position_x integer DEFAULT 0,
    position_y integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.nodes OWNER TO otocolobus;

--
-- Data for Name: chat_histories; Type: TABLE DATA; Schema: public; Owner: otocolobus
--

COPY public.chat_histories (chat_history_id, user_id, action_time, action_type, action_description) FROM stdin;
\.


--
-- Data for Name: chats; Type: TABLE DATA; Schema: public; Owner: otocolobus
--

COPY public.chats (chat_id, user_id, start_time, end_time, session_status, chat_history_id) FROM stdin;
\.


--
-- Data for Name: edges; Type: TABLE DATA; Schema: public; Owner: otocolobus
--

COPY public.edges (edge_id, flowchart_id, source_node_id, target_node_id, edge_type, description, created_at, updated_at, edge_label) FROM stdin;
\.


--
-- Data for Name: flowchart_histories; Type: TABLE DATA; Schema: public; Owner: otocolobus
--

COPY public.flowchart_histories (history_id, history_name, history_description) FROM stdin;
\.


--
-- Data for Name: flowcharts; Type: TABLE DATA; Schema: public; Owner: otocolobus
--

COPY public.flowcharts (flowchart_id, flowchart_name, description, created_at, updated_at, global_parameters, flowchat_history_id) FROM stdin;
63c2c932-212a-43a6-90f2-4904793346d3	Initial Flowchart	A basic example flowchart	2025-02-06 13:46:43.702748+09	2025-02-06 13:46:43.702748+09	\N	\N
\.


--
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: otocolobus
--

COPY public.messages (message_id, chat_id, message_time, message_role, message_content) FROM stdin;
\.


--
-- Data for Name: nodes; Type: TABLE DATA; Schema: public; Owner: otocolobus
--

COPY public.nodes (node_id, flowchart_id, node_type, api_name, parameters, description, position_x, position_y, created_at, updated_at) FROM stdin;
\.


--
-- Name: messages dialogue_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: otocolobus
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT dialogue_messages_pkey PRIMARY KEY (message_id);


--
-- Name: chats dialogue_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: otocolobus
--

ALTER TABLE ONLY public.chats
    ADD CONSTRAINT dialogue_sessions_pkey PRIMARY KEY (chat_id);


--
-- Name: edges edges_pkey; Type: CONSTRAINT; Schema: public; Owner: otocolobus
--

ALTER TABLE ONLY public.edges
    ADD CONSTRAINT edges_pkey PRIMARY KEY (edge_id);


--
-- Name: flowchart_histories flowchart_histories_pkey; Type: CONSTRAINT; Schema: public; Owner: otocolobus
--

ALTER TABLE ONLY public.flowchart_histories
    ADD CONSTRAINT flowchart_histories_pkey PRIMARY KEY (history_id);


--
-- Name: flowcharts flowcharts_pkey; Type: CONSTRAINT; Schema: public; Owner: otocolobus
--

ALTER TABLE ONLY public.flowcharts
    ADD CONSTRAINT flowcharts_pkey PRIMARY KEY (flowchart_id);


--
-- Name: nodes nodes_pkey; Type: CONSTRAINT; Schema: public; Owner: otocolobus
--

ALTER TABLE ONLY public.nodes
    ADD CONSTRAINT nodes_pkey PRIMARY KEY (node_id);


--
-- Name: chat_histories user_actions_pkey; Type: CONSTRAINT; Schema: public; Owner: otocolobus
--

ALTER TABLE ONLY public.chat_histories
    ADD CONSTRAINT user_actions_pkey PRIMARY KEY (chat_history_id);


--
-- Name: chats chats_chat_history_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: otocolobus
--

ALTER TABLE ONLY public.chats
    ADD CONSTRAINT chats_chat_history_id_fkey FOREIGN KEY (chat_history_id) REFERENCES public.chat_histories(chat_history_id);


--
-- Name: edges edges_flowchart_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: otocolobus
--

ALTER TABLE ONLY public.edges
    ADD CONSTRAINT edges_flowchart_id_fkey FOREIGN KEY (flowchart_id) REFERENCES public.flowcharts(flowchart_id) ON DELETE CASCADE;


--
-- Name: edges edges_source_node_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: otocolobus
--

ALTER TABLE ONLY public.edges
    ADD CONSTRAINT edges_source_node_id_fkey FOREIGN KEY (source_node_id) REFERENCES public.nodes(node_id) ON DELETE CASCADE;


--
-- Name: edges edges_target_node_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: otocolobus
--

ALTER TABLE ONLY public.edges
    ADD CONSTRAINT edges_target_node_id_fkey FOREIGN KEY (target_node_id) REFERENCES public.nodes(node_id) ON DELETE CASCADE;


--
-- Name: flowcharts flowcharts_history_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: otocolobus
--

ALTER TABLE ONLY public.flowcharts
    ADD CONSTRAINT flowcharts_history_id_fkey FOREIGN KEY (flowchat_history_id) REFERENCES public.flowchart_histories(history_id);


--
-- Name: messages messages_chat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: otocolobus
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_chat_id_fkey FOREIGN KEY (chat_id) REFERENCES public.chats(chat_id);


--
-- Name: nodes nodes_flowchart_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: otocolobus
--

ALTER TABLE ONLY public.nodes
    ADD CONSTRAINT nodes_flowchart_id_fkey FOREIGN KEY (flowchart_id) REFERENCES public.flowcharts(flowchart_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

