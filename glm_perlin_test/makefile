

.PHONY: all run clean docker_amd docker_arm docker_shell bin_amd bin_arm bins targets test_amd test_arm test

all: bins

# C++ compiler
# Use g++ for GNU C++ compiler if CPP is not defined
CPP ?= g++
CPP_FLAGS = -std=c++11 -O3

CPP_WARNS = -Wall -Wextra -Wpedantic
CPP_WARNS += -Wno-null-conversion -Wno-unused-variable

# uncomment to treat warnings as errors
CPP_WARNS += -Werror

GLM_LIB ?= ../include

PWD = $(shell pwd)

DOCKER_RUN_FLAGS = --rm -it
DOCKER_RUN_FLAGS += --mount type=bind,src=${PWD},dst=/glm_perlin_test

TEST_CMD = cd /cglm_src && rm -rf build && mkdir build && cd build && cmake .. -DCGLM_USE_TEST=ON -DCGLM_SHARED=ON && make && make check

test_amd: docker_amd
	docker run ${DOCKER_RUN_FLAGS} cglm_test_amd fish -c '${TEST_CMD}'

test_arm: docker_arm
	docker run ${DOCKER_RUN_FLAGS} cglm_test_arm fish -c '${TEST_CMD}'

test: test_amd test_arm

bin_amd: glm_perlin_test_amd
	docker run ${DOCKER_RUN_FLAGS} cglm_test_amd fish -c './glm_perlin_test_amd amd'

bin_arm: glm_perlin_test_arm
	docker run ${DOCKER_RUN_FLAGS} cglm_test_arm fish -c './glm_perlin_test_arm arm'

bins: bin_amd bin_arm

glm_perlin_test_amd: docker_amd glm_perlin_test.cpp
	docker run ${DOCKER_RUN_FLAGS} cglm_test_amd make out
	mv out glm_perlin_test_amd

glm_perlin_test_arm: docker_arm glm_perlin_test.cpp
	docker run ${DOCKER_RUN_FLAGS} cglm_test_arm make out
	mv out glm_perlin_test_arm

targets: glm_perlin_test_amd glm_perlin_test_arm

out: glm_perlin_test.cpp
	${CPP} \
	${CPP_FLAGS} \
	${CPP_WARNS} \
	-o $@ $< -I${GLM_LIB} \
	-I/usr/include

clean:
	rm -f glm_perlin_test_amd
	rm -f glm_perlin_test_arm
	rm -f out
	rm -f *.bin
	docker rmi -f cglm_test_amd 2>/dev/null || true
	docker rmi -f cglm_test_arm 2>/dev/null || true

docker_amd:
	cd ..; DOCKER_DEFAULT_PLATFORM=linux/amd64 docker build -t cglm_test_amd -f glm_perlin_test/Dockerfile .

docker_arm:
	cd ..; DOCKER_DEFAULT_PLATFORM=linux/arm64 docker build -t cglm_test_arm -f glm_perlin_test/Dockerfile .

docker_amd_shell: docker_amd
	docker run --rm -it cglm_test_amd fish

docker_arm_shell: docker_arm
	docker run --rm -it cglm_test_arm fish
