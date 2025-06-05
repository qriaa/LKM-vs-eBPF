#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <net/if.h>
#include <bpf/bpf.h>
#include <bpf/libbpf.h>
#include <linux/if_link.h>
#include "xdp-firewall.skel.h"

static int ifindex;
static volatile bool interrupted = false;

static void sig_handler(int sig) {
    interrupted = true;
}

int main(int argc, char **argv) {
    struct xdp_firewall_bpf *skel;
    bool is_attached = false;
    const char *ifname;
    int err;

    if (argc != 2) {
        fprintf(stderr, "Usage: %s <interface_name>\n", argv[0]);
        return 1;
    }
    ifname = argv[1];

    ifindex = if_nametoindex(ifname);
    if (!ifindex) {
        perror("if_nametoindex");
        return 1;
    }

    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);


    skel = xdp_firewall_bpf__open();
    if (!skel) {
        fprintf(stderr, "Failed to open BPF skeleton: %s\n", strerror(errno));
        return 1;
    }

    err = xdp_firewall_bpf__load(skel);
    if (!skel) {
        fprintf(stderr, "Failed to load BPF skeleton: %s\n", strerror(-err));
        return 1;
    }


    printf("Attaching in DRV mode...\n");
    int xdp_flags = XDP_FLAGS_DRV_MODE;
    err = bpf_xdp_attach(ifindex, bpf_program__fd(skel->progs.xdp_firewall), xdp_flags, NULL);

    if (err == -EOPNOTSUPP) {
            fprintf(stderr, "Driver mode not supported!\n");
            printf("Attaching in SKB mode...\n");
            xdp_flags = XDP_FLAGS_SKB_MODE;
            err = bpf_xdp_attach(ifindex, bpf_program__fd(skel->progs.xdp_firewall), xdp_flags, NULL);
    }
    if (err) {
        fprintf(stderr, "Failed to attach BPF program: %s\n", strerror(-err));
        goto cleanup;
    }
    is_attached = true;

    printf("Succesfully loaded XDP program\n");

    while (!interrupted) {
        sleep(1);
    }

    printf("\nDetaching XDP program...\n");

cleanup:

    if (is_attached)
        bpf_xdp_detach(ifindex, xdp_flags, NULL);

    if (skel)
        xdp_firewall_bpf__destroy(skel);

    return err;
}
