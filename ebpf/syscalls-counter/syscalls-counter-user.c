#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <signal.h>
#include <string.h>
#include <errno.h>
#include <sys/resource.h>
#include <bpf/libbpf.h>
#include "syscalls-counter.skel.h"

#include <linux/in.h>
#include <linux/netfilter.h>

static volatile sig_atomic_t stop = 0;

static void sig_int(int signo) {
    stop = 1;
}

static int libbpf_print_fn(enum libbpf_print_level level, const char *format, va_list args) {
    if (level == LIBBPF_WARN && !getenv("LIBBPF_STRICT_MODE")) {
        return 0;
    }
    return vfprintf(stderr, format, args);
}

int main(int argc, char **argv) {
    struct syscalls_counter_bpf *skel;
    int err;

    libbpf_set_print(libbpf_print_fn);

    struct rlimit r = {RLIM_INFINITY, RLIM_INFINITY};
    if (setrlimit(RLIMIT_MEMLOCK, &r)) {
        perror("setrlimit(RLIMIT_MEMLOCK)");
        return 1;
    }

    skel = syscalls_counter_bpf__open_and_load();
    if (!skel) {
        fprintf(stderr, "Failed to open and load BPF skeleton: %s\n", strerror(errno));
        return 1;
    }

    err = syscalls_counter_bpf__attach(skel);
    if (err) {
        fprintf(stderr, "Failed to attach BPF skeleton\n");
        goto cleanup;
    }

    if (signal(SIGINT, sig_int) == SIG_ERR) {
        fprintf(stderr, "Can't set signal handler: %s\n", strerror(errno));
        err = 1;
        goto cleanup;
    }

    printf("Loaded succesfully!\n");

    while (!stop) {
        sleep(1);
    }

    printf("\nExiting...\n");

cleanup:
    if (skel) {
        syscalls_counter_bpf__destroy(skel);
    }
    return -err;
}
