#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_endian.h>
#include <bpf/bpf_core_read.h>

#define NF_DROP 0
#define NF_ACCEPT 1
#define ETH_P_IP 0x0800
#define ETH_P_IPV6 0x86DD

char LICENSE[] SEC("license") = "GPL";

SEC("netfilter")
int nf_hook(struct bpf_nf_ctx *ctx) {
    struct __sk_buff *skb = (struct __sk_buff *)ctx->skb;

    if(bpf_ntohs(ctx->skb->protocol) != ETH_P_IP)
        return NF_ACCEPT;

    struct bpf_dynptr ptr;
    u8 iph_buf[20] = {};
    struct iphdr *ip_header;

    if (bpf_dynptr_from_skb(skb, 0, &ptr))
        return NF_DROP;

    ip_header = bpf_dynptr_slice(&ptr, 0, iph_buf, sizeof(iph_buf));

    if (!ip_header)
        return NF_ACCEPT;

    __u8 ip_proto;
    __u32 src_ip;
    __u32 dest_ip;
    bpf_core_read(&ip_proto, sizeof(ip_proto), &ip_header->protocol);
    bpf_core_read(&src_ip, sizeof(src_ip), &ip_header->saddr);
    bpf_core_read(&dest_ip, sizeof(dest_ip), &ip_header->daddr);

    if (ip_proto != IPPROTO_UDP)
        return NF_ACCEPT;

    bpf_printk("Packet: %pI4 -> %pI4\n", &src_ip, &dest_ip);

    return NF_ACCEPT;
}

