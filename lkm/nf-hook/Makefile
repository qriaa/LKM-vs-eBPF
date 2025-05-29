obj-m += nf-hook.o
PWD := $(CURDIR)
ccflags-y += -g -O1 -fno-inline-small-functions -fno-inline-functions-called-once -fno-inline-functions -fno-split-paths
all:
	$(MAKE) -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules
clean:
	$(MAKE) -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
