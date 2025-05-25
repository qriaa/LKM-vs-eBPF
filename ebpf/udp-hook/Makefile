# Adjust if your clang/llvm tools are not in the default path or have version suffixes
CLANG ?= clang
LLVM_STRIP ?= llvm-strip
BPFTOOL ?= bpftool

# Adjust if your libbpf headers/libraries are in a non-standard location
# CFLAGS for userspace program
USER_CFLAGS := -g -Wall
# LDFLAGS for userspace program
USER_LDFLAGS := -lbpf

VMLINUX := vmlinux.h
BPF_SRC := udp-hook.bpf.c
BPF_OBJ := udp-hook.bpf.o
BPF_SKEL := udp-hook.skel.h
USER_SRC := udp-hook-user.c
USER_PROG := udp-hook

all: $(USER_PROG)

vmlinux.h:
	$(BPFTOOL) btf dump file /sys/kernel/btf/vmlinux format c > vmlinux.h || rm vmlinux.h

$(BPF_OBJ): $(BPF_SRC) $(VMLINUX)
	$(CLANG) \
		-g -O2 -target bpf \
		-D__TARGET_ARCH_x86 \
		-c $< -o $@

$(BPF_SKEL): $(BPF_OBJ)
	$(BPFTOOL) gen skeleton $< > $@

$(USER_PROG): $(USER_SRC) $(BPF_SKEL)
	$(CC) $(USER_CFLAGS) $< -o $@ $(USER_LDFLAGS)

clean:
	rm -f $(BPF_OBJ) $(BPF_SKEL) $(USER_PROG) $(VMLINUX)
	rm -rf .tmp_vmlinux*

.PHONY: all clean

