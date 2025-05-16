#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>

char LICENSE[] SEC("license") = "GPL";

SEC("kprobe/__x64_sys_clone")
int bpf_prog_hello(struct pt_regs *ctx) {
    bpf_printk("Hello, World from BPF! sys_clone called.\n");
    return 0;
}
