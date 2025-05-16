# Adjust if your clang/llvm tools are not in the default path or have version suffixes
CLANG ?= clang
LLVM_STRIP ?= llvm-strip
BPFTOOL ?= bpftool

# Adjust if your libbpf headers/libraries are in a non-standard location
# CFLAGS for userspace program
USER_CFLAGS := -g -Wall
# LDFLAGS for userspace program
USER_LDFLAGS := -lbpf

BPF_OBJ := hello_kern.bpf.o
BPF_SKEL := hello_kern.skel.h
USER_PROG := hello_kern_user

all: $(USER_PROG)

$(BPF_OBJ): hello_kern.bpf.c
	$(CLANG) \
		-g -O2 -target bpf \
		-D__TARGET_ARCH_x86 \
		-c $< -o $@

$(BPF_SKEL): $(BPF_OBJ)
	$(BPFTOOL) gen skeleton $< > $@

$(USER_PROG): hello_kern_user.c $(BPF_SKEL)
	$(CC) $(USER_CFLAGS) $< -o $@ $(USER_LDFLAGS)

clean:
	rm -f $(BPF_OBJ) $(BPF_SKEL) $(USER_PROG)
	rm -rf .tmp_vmlinux*

.PHONY: all clean

