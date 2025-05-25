#include <linux/module.h>
#include <linux/printk.h>
#include <linux/netfilter.h>
#include <linux/netfilter_ipv4.h>
#include <linux/ip.h>
#include <linux/inet.h>

unsigned int udp_logger(void *priv,
                        struct sk_buff *skb,
                        const struct nf_hook_state *state);

static struct nf_hook_ops udp_logger_hook;

unsigned int udp_logger(void *priv,
                        struct sk_buff *skb,
                        const struct nf_hook_state *state) {
    struct iphdr *ip_header;

    if (!skb) {
        return NF_ACCEPT;
    }

    ip_header = ip_hdr(skb);

    if (ip_header->protocol != IPPROTO_UDP) {
        return NF_ACCEPT;
    }

    __be32 src_ip = ip_header->saddr;
    __be32 dest_ip = ip_header->daddr;

    pr_info("[PACKET] %pI4 -> %pI4\n", &src_ip, &dest_ip);
    return NF_ACCEPT;
}

static int __init udp_logger_init(void) {
    udp_logger_hook = (struct nf_hook_ops){
        .hook = udp_logger,
        .dev = NULL,
        .priv = NULL,
        .pf = NFPROTO_IPV4,
        .hook_ops_type = NF_HOOK_OP_NF_TABLES,
        .hooknum = NF_INET_PRE_ROUTING,
        .priority = NF_IP_PRI_FIRST
    };

    nf_register_net_hook(&init_net, &udp_logger_hook);
    pr_info("UDP logger loaded.\n");
    return 0;
}

static void __exit udp_logger_exit(void) {
    nf_unregister_net_hook(&init_net, &udp_logger_hook);
    pr_info("UDP logger unloaded.\n");
}

module_init(udp_logger_init);
module_exit(udp_logger_exit);

MODULE_AUTHOR("Author Name urbaniak.g11@gmail.com");
MODULE_DESCRIPTION("This module performs some sample operations using netfilter");
MODULE_LICENSE("GPL");
