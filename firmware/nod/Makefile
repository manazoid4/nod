.PHONY: test preview
CXX ?= g++
FLAGS = -std=c++11 -Wall -Wextra -Werror -O1
test: ; $(CXX) $(FLAGS) tests/test_nod.cpp -o /tmp/nod_test && /tmp/nod_test
preview: ; $(CXX) $(FLAGS) tools/gen_preview.cpp -o /tmp/nod_gen && /tmp/nod_gen > preview/layouts.js
