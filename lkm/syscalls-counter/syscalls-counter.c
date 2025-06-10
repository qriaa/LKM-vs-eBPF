#include <linux/module.h>
#include <linux/printk.h>
#include <linux/ptrace.h>
#include <linux/kprobes.h>
#include <linux/atomic.h>

// Defining multiple kprobes should delay syscall execution less
int count_execve(struct kprobe *p, struct pt_regs *regs);
int count_openat(struct kprobe *p, struct pt_regs *regs);
int count_read(struct kprobe *p, struct pt_regs *regs);
int count_write(struct kprobe *p, struct pt_regs *regs);

static atomic_t execve_count = ATOMIC_INIT(0);
int count_execve(struct kprobe *p, struct pt_regs *regs) {
    atomic_inc(&execve_count);
    return 0;
}

static atomic_t openat_count = ATOMIC_INIT(0);
int count_openat(struct kprobe *p, struct pt_regs *regs) {
    atomic_inc(&openat_count);
    return 0;
}

static atomic_t read_count = ATOMIC_INIT(0);
int count_read(struct kprobe *p, struct pt_regs *regs) {
    atomic_inc(&read_count);
    return 0;
}

static atomic_t write_count = ATOMIC_INIT(0);
int count_write(struct kprobe *p, struct pt_regs *regs) {
    atomic_inc(&write_count);
    return 0;
}

static struct kprobe kprobe_execve = {
    .symbol_name = "__x64_sys_execve",
    .pre_handler = count_execve,
};

static struct kprobe kprobe_openat = {
    .symbol_name = "__x64_sys_openat",
    .pre_handler = count_openat,
};

static struct kprobe kprobe_read = {
    .symbol_name = "__x64_sys_read",
    .pre_handler = count_read,
};

static struct kprobe kprobe_write = {
    .symbol_name = "__x64_sys_write",
    .pre_handler = count_write,
};

static struct kprobe *kprobes[] = {
    &kprobe_execve,
    &kprobe_openat,
    &kprobe_read,
    &kprobe_write,
};

static int __init syscalls_counter_init(void) {
    pr_info("Loading syscalls module...\n");
    int ret = register_kprobes(kprobes, sizeof(kprobes) / sizeof(kprobes[0]));
    if (ret) {
        pr_err("syscalls: failed to register kprobes: %d\n", ret);
        return ret;
    }
    pr_info("Syscalls loaded.\n");
    return 0;
}

static void __exit syscalls_counter_exit(void) {
    pr_info("Unloading syscalls module...\n");
    unregister_kprobes(kprobes, sizeof(kprobes) / sizeof(kprobes[0]));
    pr_info("Counted execve syscalls: %d\n", atomic_read(&execve_count));
    pr_info("Counted openat syscalls: %d\n", atomic_read(&openat_count));
    pr_info("Counted read syscalls: %d\n", atomic_read(&read_count));
    pr_info("Counted write syscalls: %d\n", atomic_read(&write_count));
    pr_info("Syscalls unloaded.\n");
}

module_init(syscalls_counter_init);
module_exit(syscalls_counter_exit);

MODULE_AUTHOR("Author Name urbaniak.g11@gmail.com");
MODULE_DESCRIPTION("This is a simple syscall counter for the LKM-vs-eBPF project");
MODULE_LICENSE("GPL");
