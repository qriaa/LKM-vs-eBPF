#include <linux/module.h>
#include <linux/printk.h>
#include <linux/netfilter.h>
#include <linux/netfilter_ipv4.h>
#include <linux/ip.h>
#include <linux/tcp.h>
#include <linux/inet.h>

unsigned int tcp_logger(void *priv,
                        struct sk_buff *skb,
                        const struct nf_hook_state *state);

static struct nf_hook_ops tcp_logger_hook;

unsigned int tcp_logger(void *priv,
                        struct sk_buff *skb,
                        const struct nf_hook_state *state) {
    struct iphdr *ip_header;

    if (!skb) {
        return NF_ACCEPT;
    }

    ip_header = ip_hdr(skb);

    __be32 src_ip = ip_header->saddr;
    __be32 dest_ip = ip_header->daddr;

    pr_info("Packet: %pI4 -> %pI4\n", &src_ip, &dest_ip);
    return NF_ACCEPT;
}

static int __init tcp_logger_init(void) {
    tcp_logger_hook = (struct nf_hook_ops){
        .hook = tcp_logger,
        .dev = NULL,
        .priv = NULL,
        .pf = NFPROTO_IPV4,
        .hook_ops_type = NF_HOOK_OP_NF_TABLES,
        .hooknum = NF_INET_PRE_ROUTING,
        .priority = NF_IP_PRI_FIRST
    };

    nf_register_net_hook(&init_net, &tcp_logger_hook);
    pr_info("TCP logger loaded.\n");
    return 0;
}

static void __exit tcp_logger_exit(void) {
    nf_unregister_net_hook(&init_net, &tcp_logger_hook);
    pr_info("TCP logger unloaded.\n");
}

module_init(tcp_logger_init);
module_exit(tcp_logger_exit);

MODULE_AUTHOR("Author Name urbaniak.g11@gmail.com");
MODULE_DESCRIPTION("This module performs some sample operations using netfilter");
MODULE_LICENSE("GPL");
