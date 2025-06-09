#include <linux/module.h>
#include <linux/printk.h>
#include <linux/ptrace.h>
#include <linux/kprobes.h>

int count_syscalls(struct kprobe *p, struct pt_regs *regs);

static unsigned int syscall_count = 0;

int count_syscalls(struct kprobe *p, struct pt_regs *regs) {
    syscall_count += 1;
    return 0;
}

static struct kprobe syscall_kprobe = {
    // Ran on every syscall
    // arch/x86/entry/common.c#L83
    // Other symbols such as do_syscall_64 are in the kprobe blacklist
    .symbol_name = "x64_sys_call",
    .pre_handler = count_syscalls,
};

static int __init syscalls_counter_init(void) {
    pr_info("Loading syscalls module...\n");
    int ret = register_kprobe(&syscall_kprobe);
    if (ret) {
        pr_err("syscalls: failed to register kprobe: %d\n", ret);
        return ret;
    }
    pr_info("Syscalls loaded.\n");
    return 0;
}

static void __exit syscalls_counter_exit(void) {
    pr_info("Unloading syscalls module...\n");
    unregister_kprobe(&syscall_kprobe);
    pr_info("Counted syscalls: %d\n", syscall_count);
    pr_info("Syscalls unloaded.\n");
}

module_init(syscalls_counter_init);
module_exit(syscalls_counter_exit);

MODULE_AUTHOR("Author Name urbaniak.g11@gmail.com");
MODULE_DESCRIPTION("This is a simple syscall counter for the LKM-vs-eBPF project");
MODULE_LICENSE("GPL");
