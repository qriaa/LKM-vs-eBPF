obj-m += syscalls-counter.o
PWD := $(CURDIR)
#ccflags-y += -g
all:
	$(MAKE) -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules
clean:
	$(MAKE) -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
