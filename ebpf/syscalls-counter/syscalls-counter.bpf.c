#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_endian.h>
#include <bpf/bpf_core_read.h>

char LICENSE[] SEC("license") = "GPL";

static unsigned int syscall_count = 0;

SEC("kprobe/x64_sys_call")
int BPF_KPROBE(count_syscalls, const struct pt_regs *regs, unsigned int nr) {
    syscall_count +=1;
    // bpf_printk("Syscall count: %d\n", syscall_count);
    return 0;
}

