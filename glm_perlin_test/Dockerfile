FROM ubuntu:22.04
WORKDIR /

# # Install dependencies
RUN apt-get update -y
RUN apt-get install -y clang-15 make cmake
ENV CPP=/usr/bin/clang++-15

# RUN apt-get install -y fish wget unzip vim
RUN apt-get install -y fish wget unzip

# Cleanup
RUN apt-get clean

WORKDIR /usr/include
# WORKDIR /usr/include/glm

RUN wget https://github.com/g-truc/glm/releases/download/1.0.1/glm-1.0.1-light.zip
RUN unzip glm-1.0.1-light.zip
RUN rm glm-1.0.1-light.zip
# COPY ./glm .

# Copy source code
WORKDIR /usr/include/cglm/
COPY ./include/cglm .

WORKDIR /cglm_src
COPY . .
RUN rm -rf build

WORKDIR /glm_perlin_test
COPY ./glm_perlin_test/glm_perlin_test.cpp .
COPY ./glm_perlin_test/makefile .

CMD ["fish"]
