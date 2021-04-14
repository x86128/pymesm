TESTS=00_aax_aox_aex.asm  02_ati_ita.asm  04_utc_wtc.asm  \
	  06_vlm.asm  08_sti.asm 01_addr0.asm 03_uza_uia.asm  \
	  05_vjm.asm      07_its.asm  09_asn_asx.asm 10_add_sub_rsub.asm

RUN=$(TESTS:.asm=.oct)

%.oct :
	cd test && python3 ../pymesm.py -i $@ -c 12000

%.asm :
	cd test && python3 ../asm/asm.py -i $@

all: build_tests run_tests

build_tests: $(TESTS)

run_tests: $(RUN)

clean:
	rm tests/*.oct

