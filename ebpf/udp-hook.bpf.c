#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

char LICENSE[] SEC("license") = "GPL";

SEC("kprobe/ip_rcv_core")
int bpf_ip_rcv(struct pt_regs *ctx) {
    struct sk_buff *skb;

    skb = (struct sk_buff *)PT_REGS_PARM1(ctx);

    if (!skb)
        return BPF_OK;

    void *head = NULL;
    bpf_core_read(&head, sizeof(head), &skb->head);

    u16 network_off = 0;
    bpf_core_read(&network_off, sizeof(network_off), &skb->network_header);

    struct iphdr *ip_header = head + network_off;

    // sudo bpftool prog loadall prog.bpf.o /sys/fs/bpf/testprog
    if (!ip_header)
        return BPF_OK;

    __u8 ip_proto;
    __u32 src_ip;
    __u32 dest_ip;
    bpf_core_read(&ip_proto, sizeof(ip_proto), &ip_header->protocol);
    bpf_core_read(&src_ip, sizeof(src_ip), &ip_header->saddr);
    bpf_core_read(&dest_ip, sizeof(dest_ip), &ip_header->daddr);

    if (ip_proto != IPPROTO_UDP)
        return BPF_OK;

    bpf_printk("Packet: %pI4 -> %pI4\n", &src_ip, &dest_ip);

    return BPF_OK;
}
