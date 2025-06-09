#include <linux/module.h>
#include <linux/printk.h>
#include <linux/netfilter.h>
#include <linux/netfilter_ipv4.h>
#include <linux/ip.h>
#include <linux/inet.h>
#include <linux/array_size.h>
#include <linux/byteorder/generic.h>


static unsigned int firewall(void *priv,
                        struct sk_buff *skb,
                        const struct nf_hook_state *state);

static struct nf_hook_ops firewall_hook;

static __be32 blocked_ips[] = {
    htonl(0xC0A80065) //192.168.0.101
};

static int blocked_ips_size = ARRAY_SIZE(blocked_ips);

static unsigned int dropped_packets = 0;

static unsigned int firewall(void *priv,
                        struct sk_buff *skb,
                        const struct nf_hook_state *state) {
    struct iphdr *ip_header;

    if (!skb)
        return NF_ACCEPT;

    ip_header = ip_hdr(skb);

    if (ip_header->protocol != IPPROTO_UDP) {
        return NF_ACCEPT;
    }

    __be32 src_ip = ip_header->saddr;
    // __be32 dest_ip = ip_header->daddr;

    for(int i = 0; i < blocked_ips_size; i++) {
        if (src_ip == blocked_ips[i]) {
            dropped_packets += 1;
            // Unfortunately, iperf3 needs to send some UDP packets first
            // in order to try sending more.
            // This can be fixed by writing a custom packet spammer.
            // https://github.com/esnet/iperf/blob/master/src/iperf_udp.c#L273
            if(dropped_packets < 8)
                return NF_ACCEPT;

            return NF_DROP;
        }
    }

    // pr_info("[PACKET] %pI4 -> %pI4\n", &src_ip, &dest_ip);
    return NF_ACCEPT;
}

static int __init firewall_init(void) {
    firewall_hook = (struct nf_hook_ops){
        .hook = firewall,
        .dev = NULL,
        .priv = NULL,
        .pf = NFPROTO_IPV4,
        .hook_ops_type = NF_HOOK_OP_NF_TABLES,
        .hooknum = NF_INET_PRE_ROUTING,
        .priority = NF_IP_PRI_FIRST
    };

    nf_register_net_hook(&init_net, &firewall_hook);
    pr_info("Firewall loaded.\n");
    return 0;
}

static void __exit firewall_exit(void) {
    pr_info("Unloading firewall...\n");
    nf_unregister_net_hook(&init_net, &firewall_hook);
    pr_info("Firewall dropped packets: %d", dropped_packets);
    pr_info("Firewall unloaded.\n");
}

module_init(firewall_init);
module_exit(firewall_exit);

MODULE_AUTHOR("Author Name urbaniak.g11@gmail.com");
MODULE_DESCRIPTION("This is a simple firewall for the LKM-vs-eBPF project");
MODULE_LICENSE("GPL");
