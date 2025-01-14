#include <stdio.h>
#include <string>

#include <fcntl.h> /* open */
#include <unistd.h> /* ftruncate */
#include <sys/mman.h> /* mmap */

// GLM
#include <glm/gtc/noise.hpp>
#include <glm/vec4.hpp> // glm::vec4

// CGLM
// #include "cglm/call/perlin.h"
#include "cglm/cglm.h"

#ifndef float32_t
#define float32_t float
#endif

// XYZ dimensions
#define L 101
#define M 101
#define N 101

#define FOR_LMN(...) \
    for (int i = 0; i < L; i++) { \
        for (int j = 0; j < M; j++) { \
            for (int k = 0; k < N; k++) { \
                __VA_ARGS__ \
            } \
        } \
    }


#define D 10 // scale, higher is finer features

int lmn2lin(int l, int m, int n) {
    return l * M * N + m * N + n;
}

struct context {
    int fd;
    float32_t * data;
    size_t offset;
    clock_t start;
    clock_t end;
    unsigned int points;
    char * filename;
} ctx;

context
new_context(int points, char * filename) {
    ctx.points = points;
    ctx.filename = filename;
    return ctx;
}

void
pre(context &ctx) {
    printf("Generating %d points for '%s'\n", ctx.points, ctx.filename);
    ctx.fd = open(ctx.filename, O_RDWR | O_CREAT, S_IRUSR | S_IWUSR);
    size_t size = ctx.points * sizeof(float32_t) + 3 * sizeof(u_int32_t);
    ftruncate(ctx.fd, size);
    ctx.data = (float32_t*)mmap(NULL, size, PROT_WRITE, MAP_SHARED, ctx.fd, 0);
    // write metadata: L, M, N
    u_int32_t *metadata = (u_int32_t*)ctx.data;
    metadata[0] = L;
    metadata[1] = M;
    metadata[2] = N;
    ctx.offset = 3;
    ctx.start = clock();
}

clock_t
post(context &ctx) {
    ctx.end = clock();
    size_t size = ctx.points * sizeof(float32_t) + 3 * sizeof(u_int32_t);
    munmap(ctx.data, size);
    close(ctx.fd);
    clock_t elapsed =  ctx.end - ctx.start;
    printf("Done generating points for '%s' in %.0f ms\n", ctx.filename, (float)elapsed / CLOCKS_PER_SEC * 1000);
    return elapsed;
}

void
write(context &ctx, int i, int j, int k, float32_t value) {
    ctx.data[lmn2lin(i, j, k)+ctx.offset] = value;
}

int main(int argc, char *argv[]) {

    // parse the --suffix argument
    char *suffix = (char*)("perlin");
    if (argc > 1) {
        suffix = argv[1];
    }

    unsigned int points = L * M * N;
    float32_t memory = points * sizeof(float32_t) / 1024.0 / 1024.0;
    printf("Generating %d points for 4D noise\n", points);
    printf("Memory: %.2f MB\n", memory);

    // char * glm_vec4_filename = (char*)("glm_vec4_perlin.bin");
    // char * cglm_vec4_filename = (char*)("cglm_vec4_perlin.bin");
    // char * glm_vec3_filename = (char*)("glm_vec3_perlin.bin");
    // char * cglm_vec3_filename = (char*)("cglm_vec3_perlin.bin");
    // char * glm_vec2_filename = (char*)("glm_vec2_perlin.bin");
    // char * cglm_vec2_filename = (char*)("cglm_vec2_perlin.bin");
    
    char * glm_vec4_filename = (char*)malloc(100);
    char * cglm_vec4_filename = (char*)malloc(100);
    char * glm_vec3_filename = (char*)malloc(100);
    char * cglm_vec3_filename = (char*)malloc(100);
    char * glm_vec2_filename = (char*)malloc(100);
    char * cglm_vec2_filename = (char*)malloc(100);
    snprintf(glm_vec4_filename, 100, "glm_vec4_%s.bin", suffix);
    snprintf(cglm_vec4_filename, 100, "cglm_vec4_%s.bin", suffix);
    snprintf(glm_vec3_filename, 100, "glm_vec3_%s.bin", suffix);
    snprintf(cglm_vec3_filename, 100, "cglm_vec3_%s.bin", suffix);
    snprintf(glm_vec2_filename, 100, "glm_vec2_%s.bin", suffix);
    snprintf(cglm_vec2_filename, 100, "cglm_vec2_%s.bin", suffix);

    // 4D noise
    
    context ctx = new_context(points, glm_vec4_filename);
    pre(ctx);

    FOR_LMN(
        glm::vec<4, float32_t, glm::packed_lowp> p = glm::vec4(float32_t(i)/L*D, float32_t(j)/M*D, float32_t(k)/N*D, 3.1415f);
        write(ctx, i, j, k, glm::perlin(p));
    );
    clock_t glm_vec4_elapsed = post(ctx);

    ctx = new_context(points, cglm_vec4_filename);
    pre(ctx);

    FOR_LMN(
        vec4 p = {float32_t(i)/L*D, float32_t(j)/M*D, float32_t(k)/N*D, 3.1415f};
        write(ctx, i, j, k, glm_perlin_vec4(p));
    );

    clock_t cglm_vec4_elapsed = post(ctx);

    // 3D noise

    ctx = new_context(points, glm_vec3_filename);
    pre(ctx);

    FOR_LMN(
        glm::vec<3, float32_t, glm::packed_lowp> p = glm::vec3(float32_t(i)/L*D, float32_t(j)/M*D, float32_t(k)/N*D);
        write(ctx, i, j, k, glm::perlin(p));
    );

    clock_t glm_vec3_elapsed = post(ctx);

    ctx = new_context(points, cglm_vec3_filename);
    pre(ctx);

    FOR_LMN(
        vec3 p = {float32_t(i)/L*D, float32_t(j)/M*D, float32_t(k)/N*D};
        write(ctx, i, j, k, glm_perlin_vec3(p));
    );

    clock_t cglm_vec3_elapsed = post(ctx);


    // 2D noise

    // float32_t *glm_vec2_perlin = (float32_t*)malloc(points * sizeof(float32_t));

    // clock_t glm_vec2_start = clock();

    // for (int i = 0; i < L; i++) {
    //     for (int j = 0; j < M; j++) {
    //         for (int k = 0; k < N; k++) {
    //             glm::vec<2, float32_t, glm::packed_lowp> p = glm::vec2(float32_t(i)/L*D, float32_t(j)/M*D + float32_t(k)/N*D);
    //             glm_vec2_perlin[lmn2lin(i, j, k)] = glm::perlin(p);
    //         }
    //     }
    // }

    // clock_t glm_vec2_end = clock();

    // float32_t *cglm_vec2_perlin = (float32_t*)malloc(points * sizeof(float32_t));

    // clock_t cglm_vec2_start = clock();

    // for (int i = 0; i < L; i++) {
    //     for (int j = 0; j < M; j++) {
    //         for (int k = 0; k < N; k++) {
    //             vec2 p = {float32_t(i)/L*D, float32_t(j)/M*D + float32_t(k)/N*D};
    //             cglm_vec2_perlin[lmn2lin(i, j, k)] = glm_perlin_vec2(p);
    //         }
    //     }
    // }

    // clock_t cglm_vec2_end = clock();

    ctx = new_context(points, glm_vec2_filename);
    pre(ctx);

    FOR_LMN(
        glm::vec<2, float32_t, glm::packed_lowp> p = glm::vec2(float32_t(i)/L*D, float32_t(j)/M*D + float32_t(k)/N*D);
        write(ctx, i, j, k, glm::perlin(p));
    );

    clock_t glm_vec2_elapsed = post(ctx);

    ctx = new_context(points, cglm_vec2_filename);
    pre(ctx);

    FOR_LMN(
        vec2 p = {float32_t(i)/L*D, float32_t(j)/M*D + float32_t(k)/N*D};
        write(ctx, i, j, k, glm_perlin_vec2(p));
    );

    clock_t cglm_vec2_elapsed = post(ctx);

    // glm::vec4 p = {0.1f, 0.2, 0.3f, 0.4f};
    // for (int i = 0; i < 10; i++) {
    //     float32_t glm_v = glm::perlin(p);
    //     printf("glm::perlin(%f, %f, %f, %f) = %.16f\n", p[0], p[1], p[2], p[3], glm_v);
    //     p += 0.1f;
    // }

    // glm::vec3 p = {0.1f, 0.2, 0.3f};
    // for (int i = 0; i < 10; i++) {
    //     float32_t glm_v = glm::perlin(p);
    //     printf("glm::perlin(%f, %f, %f) = %.16f\n", p[0], p[1], p[2], glm_v);
    //     p += 0.1f;
    // }

    // glm::vec2 p = {0.1f, 0.2};
    // for (int i = 0; i < 10; i++) {
    //     float32_t glm_v = glm::perlin(p);
    //     printf("glm::perlin(%f, %f) = %.16f\n", p[0], p[1], glm_v);
    //     p += 0.1f;
    // }    

    float32_t vec4_speedup = (float32_t)glm_vec4_elapsed / (float32_t)cglm_vec4_elapsed;
    float32_t vec3_speedup = (float32_t)glm_vec3_elapsed / (float32_t)cglm_vec3_elapsed;
    float32_t vec2_speedup = (float32_t)glm_vec2_elapsed / (float32_t)cglm_vec2_elapsed;

    printf("Timing (in clock ticks)\n");
    printf("GLM vec4:  %ld\n", glm_vec4_elapsed);
    printf("CGLM vec4: %ld (x%.2f speedup)\n", cglm_vec4_elapsed, vec4_speedup);
    printf("GLM vec3:  %ld\n", glm_vec3_elapsed);
    printf("CGLM vec3: %ld (x%.2f speedup)\n", cglm_vec3_elapsed, vec3_speedup);
    printf("GLM vec2:  %ld\n", glm_vec2_elapsed);
    printf("CGLM vec2: %ld (x%.2f speedup)\n", cglm_vec2_elapsed, vec2_speedup);

    return 0;
}