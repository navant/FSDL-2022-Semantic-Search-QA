#!/bin/sh

jina flow --uses src/semantic_search_qa/server/server.yml &

streamlit run src/semantic_search_qa/ui/01_main.py --server.port=8501 --server.address=0.0.0.0