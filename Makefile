# DealerDesk build. `make` is equivalent to: gcc -o dealerdesk *.c -lm
# Override the compiler with: make CC=clang
CC  = gcc
SRC = $(wildcard *.c)

.PHONY: all warn asan test test-asan test-selfcheck check-agent demo clean

all:
	$(CC) -o dealerdesk $(SRC) -lm

# Warnings are shown but do not fail the build (not yet -Werror).
warn:
	$(CC) -Wall -Wextra -o dealerdesk-warn $(SRC) -lm

asan:
	$(CC) -fsanitize=address,undefined -g -o dealerdesk-asan $(SRC) -lm

# Golden-master tests (spec 002).
test: all
	python3 tests/golden.py

# Same scenarios against the sanitizer build; any stderr output is a failure.
test-asan: asan
	ASAN_OPTIONS=detect_leaks=1 python3 tests/golden.py --bin ./dealerdesk-asan --fail-on-stderr

# Proves the suite catches a regression and a hang (spec 002 R14).
test-selfcheck:
	CC=$(CC) python3 tests/golden.py --selfcheck

# Checks the committed agent setup is well formed (spec 003).
check-agent:
	python3 scripts/check-agent-setup.py

# Shows the fleet discount on a temp copy of the fixtures (decision D13).
demo: all
	python3 scripts/demo.py

clean:
	rm -f dealerdesk dealerdesk-warn dealerdesk-asan
