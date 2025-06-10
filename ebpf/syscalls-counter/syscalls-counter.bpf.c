#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_endian.h>
#include <bpf/bpf_core_read.h>

char LICENSE[] SEC("license") = "GPL";

static int execve_count = 0;
static int openat_count = 0;
static int read_count = 0;
static int write_count = 0;

SEC("kprobe/__x64_sys_execve")
int BPF_KPROBE(count_execve, const struct pt_regs *regs, unsigned int nr) {
    __sync_fetch_and_add(&execve_count, 1);
    return 0;
}

SEC("kprobe/__x64_sys_openat")
int BPF_KPROBE(count_openat, const struct pt_regs *regs, unsigned int nr) {
    __sync_fetch_and_add(&openat_count, 1);
    return 0;
}

SEC("kprobe/__x64_sys_read")
int BPF_KPROBE(count_read, const struct pt_regs *regs, unsigned int nr) {
    __sync_fetch_and_add(&read_count, 1);
    return 0;
}

SEC("kprobe/__x64_sys_write")
int BPF_KPROBE(count_write, const struct pt_regs *regs, unsigned int nr) {
    __sync_fetch_and_add(&write_count, 1);
    return 0;
}

