#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <signal.h>
#include <string.h>
#include <errno.h>
#include <sys/resource.h>
#include <bpf/libbpf.h>
#include "nf-hook.skel.h"

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
    struct nf_hook_bpf *skel;
    int err;

    libbpf_set_print(libbpf_print_fn);

    struct rlimit r = {RLIM_INFINITY, RLIM_INFINITY};
    if (setrlimit(RLIMIT_MEMLOCK, &r)) {
        perror("setrlimit(RLIMIT_MEMLOCK)");
        return 1;
    }

    skel = nf_hook_bpf__open_and_load();
    if (!skel) {
        fprintf(stderr, "Failed to open and load BPF skeleton: %s\n", strerror(errno));
        return 1;
    }

    struct bpf_program *prog_to_attach = skel->progs.nf_hook;

    struct bpf_netfilter_opts nf_opts = {};
    nf_opts.sz = sizeof(nf_opts);
    nf_opts.pf = NFPROTO_IPV4;
    nf_opts.hooknum = NF_INET_PRE_ROUTING;
    nf_opts.priority = -100;

    struct bpf_link *link = bpf_program__attach_netfilter(prog_to_attach, &nf_opts);

    if (!link) {
        fprintf(stderr, "Failed to attach BPF skeleton: %s\n", strerror(errno));
        err = 1;
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
        nf_hook_bpf__destroy(skel);
    }
    return -err;
}
