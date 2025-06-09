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
BPF_SRC := syscalls-counter.bpf.c
BPF_OBJ := syscalls-counter.bpf.o
BPF_SKEL := syscalls-counter.skel.h
USER_SRC := syscalls-counter-user.c
USER_PROG := syscalls-counter

all: $(USER_PROG)

vmlinux.h:
	$(BPFTOOL) btf dump file /sys/kernel/btf/vmlinux format c > $(VMLINUX) || rm $(VMLINUX)

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

