# DealerDesk build. `make` is equivalent to: gcc -o dealerdesk *.c -lm
# Override the compiler with: make CC=clang
CC  = gcc
SRC = $(wildcard *.c)

.PHONY: all warn asan test clean

all:
	$(CC) -o dealerdesk $(SRC) -lm

# Warnings are shown but do not fail the build (not yet -Werror).
warn:
	$(CC) -Wall -Wextra -o dealerdesk-warn $(SRC) -lm

asan:
	$(CC) -fsanitize=address,undefined -g -o dealerdesk-asan $(SRC) -lm

# Placeholder until spec 002 adds the golden-master tests.
test:
	@echo "no tests yet (see specs/002)"

clean:
	rm -f dealerdesk dealerdesk-warn dealerdesk-asan
