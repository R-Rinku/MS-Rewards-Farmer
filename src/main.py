import argparse
import logging
import os
import sys

import log_utils
import accounts
import rewards_tasks
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException

HEADLESS = os.environ.get("REWARDS_HEADLESS", "").strip().lower() in ("1", "true", "yes")

logger = logging.getLogger(__name__)


def parse_args():
	"""Parse command-line arguments when invoked directly from the CLI.

	Uses parse_known_args() so external test runners like unittest do not fail on unknown flags.
	"""
	parser = argparse.ArgumentParser(
		description="Microsoft Rewards automated farmer (runs directly via src/main.py)"
	)
	parser.add_argument(
		"--headless",
		action="store_true",
		default=None,
		help="Run Edge in headless background mode (or set REWARDS_HEADLESS=1)"
	)
	parser.add_argument(
		"--source",
		choices=["trends", "llm"],
		default=None,
		help="Query source backend: 'trends' (default, keyless public feeds) or 'llm' (Ollama)"
	)
	parser.add_argument(
		"--accounts",
		type=str,
		default=None,
		help="Comma-separated profile names to run through (or set REWARDS_ACCOUNTS=...)"
	)
	known, _ = parser.parse_known_args()
	return known


def build_options(account: accounts.Account) -> webdriver.EdgeOptions:
	options = webdriver.EdgeOptions()

	options.add_experimental_option("excludeSwitches", ["enable-automation"])
	options.add_experimental_option("useAutomationExtension", False)
	options.add_argument("--disable-blink-features=AutomationControlled")
	options.add_argument(f"--user-data-dir={account.user_data_dir}")
	options.add_argument(f"--profile-directory={account.profile_name}")

	if HEADLESS:
		# A container has no display. The window size is set explicitly because
		# the pointer code works in viewport coordinates, and the default
		# headless window is small enough to put cards out of reach.
		options.add_argument("--headless=new")
		options.add_argument("--window-size=1920,1080")
		options.add_argument("--no-sandbox")
		options.add_argument("--disable-dev-shm-usage")

	return options


def run_account(account: accounts.Account) -> bool:
	"""Work one account. Returns whether the browser started."""
	try:
		driver = webdriver.Edge(options=build_options(account))
	except SessionNotCreatedException as exc:
		# Chromium allows one process per user data directory. When the profile
		# is already open the driver's copy exits during startup, and selenium
		# reports it as the browser crashing with a message that names neither
		# the profile nor the other window.
		logger.error("[FAIL] %s: could not start Edge with this profile.", account.name)
		logger.error("       profile directory: %s", account.user_data_dir)
		logger.error("       The usual cause is that this profile is already open in another")
		logger.error("       Edge window, including one left over from a previous run.")
		logger.error("       driver said: %s", log_utils.exception_summary(exc))

		return False

	try:
		rewards = rewards_tasks.RewardsTaskUtils(driver)
		rewards.complete_all_tasks()
	finally:
		try:
			driver.quit()
		except Exception as exc:
			# quit() raises when the browser is already gone. Letting it out
			# here would replace whatever actually went wrong with the tidy-up's
			# own error, and the process it is meant to end is dead anyway.
			logger.warning(
				"%s: the driver did not shut down cleanly: %s",
				account.name, log_utils.exception_summary(exc)
			)

	return True


def main() -> int:
	global HEADLESS
	log_utils.setup_logging()

	args = parse_args()
	if args.headless is not None:
		HEADLESS = args.headless
		os.environ["REWARDS_HEADLESS"] = "1" if args.headless else "0"
	if args.source:
		os.environ["QUERY_SOURCE"] = args.source
	if args.accounts:
		os.environ["REWARDS_ACCOUNTS"] = args.accounts

	try:
		configured = accounts.configured()
	except ValueError as exc:
		logger.error("[FAIL] %s", exc)

		return 2

	started = 0

	for account in configured:
		if len(configured) > 1:
			logger.info("=== account: %s ===", account.name)

		# One account must not be able to end the batch. complete_all_tasks
		# already contains a task that fails, and run_account names the profile
		# that is already open, but everything else - a driver that will not
		# start for some other reason, the browser dying mid-run, a page that
		# never loads - reached here and took the remaining accounts with it.
		# KeyboardInterrupt is deliberately not caught: Ctrl-C means stop.
		try:
			if run_account(account):
				started += 1
		except Exception as exc:
			logger.error(
				"[FAIL] %s: %s: %s",
				account.name, type(exc).__name__, log_utils.exception_summary(exc),
				exc_info=logger.isEnabledFor(logging.DEBUG)
			)

	if len(configured) > 1:
		logger.info("%s/%s accounts ran", started, len(configured))

	# Nothing is watching a container, and stdin is not a terminal there.
	if not HEADLESS and sys.stdin.isatty():
		try:
			input("Press Enter to exit...")
		except (EOFError, KeyboardInterrupt):
			pass

	return 0 if started else 1


if __name__ == "__main__":
	sys.exit(main())
