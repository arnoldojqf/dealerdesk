# DealerDesk build. `make` is equivalent to: gcc -o dealerdesk *.c -lm
# Override the compiler with: make CC=clang
CC  = gcc
SRC = $(wildcard *.c)

.PHONY: all warn asan test test-selfcheck clean

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

# Proves the suite catches a regression and a hang (spec 002 R14).
test-selfcheck:
	CC=$(CC) python3 tests/golden.py --selfcheck

clean:
	rm -f dealerdesk dealerdesk-warn dealerdesk-asan
