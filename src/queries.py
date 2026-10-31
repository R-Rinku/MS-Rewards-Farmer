"""Where search queries come from.

Two backends:
- `trends` (default): Uses public feeds (Google Trends RSS, Bing Autosuggest,
  Wikipedia topics, and nouns.txt) with zero AI requirement, no model downloads,
  and no API keys.
- `llm` (optional): Uses a local Ollama model if installed and explicitly configured.

Run normally:
    python src/main.py

Or with an optional query source:
    QUERY_SOURCE=trends python src/main.py
"""

import logging
import os

import query_sources

logger = logging.getLogger(__name__)

TRENDS = "trends"
LLM = "llm"

DEFAULT_SOURCE = TRENDS

ENV_VAR = "QUERY_SOURCE"


def selected_source() -> str:
	"""Read on each call so a test or environment variable can change it without reimporting."""
	choice = os.environ.get(ENV_VAR, DEFAULT_SOURCE).strip().lower()

	return choice if choice in (LLM, TRENDS) else DEFAULT_SOURCE


def search_query_for_task(task_description: str) -> str:
	"""A query for one 'Search on Bing for X' card."""
	if selected_source() == TRENDS:
		query = query_sources.query_from_task_description(task_description)

		if query:
			return query

		logger.warning("No query source reachable, using the lowercased task description.")
		return task_description.lower()

	try:
		import llm_utils

		return llm_utils.get_search_query_from_task_description(task_description)
	except Exception as exc:
		logger.warning("LLM query generation failed (%s), falling back to trends.", exc)
		query = query_sources.query_from_task_description(task_description)
		return query if query else task_description.lower()


def related_queries(count: int):
	"""`count` queries for the daily search quota."""
	if selected_source() == TRENDS:
		queries = query_sources.related_queries(count)

		if queries:
			return queries

		logger.warning("No query source reachable, falling back to the wordlist.")
		return query_sources.wordlist_queries(count)

	try:
		import llm_utils

		return llm_utils.get_related_search_queries(llm_utils.get_random_noun(), num_queries=count)
	except Exception as exc:
		logger.warning("LLM query generation failed (%s), falling back to trends.", exc)
		queries = query_sources.related_queries(count)
		return queries if queries else query_sources.wordlist_queries(count)
