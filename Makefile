TESTS=00_aax_aox_aex.asm 01_addr0.asm 02_ati_ita.asm 03_uza_uia.asm \
      04_utc_wtc.asm 05_vjm.asm 06_vlm.asm 07_its.asm 08_sti.asm \
	  09_asn_asx.asm 10_add_sub_rsub.asm 11_amx.asm 12_div.asm 13_mul.asm \
	  14_arx.asm 15_e+n_e-n_e+x_e-x.asm 16_acx_anx.asm 17_rte_ntr_xtr.asm \
	  18_apx_aux.asm

EXAMPLES=arr.asm binop.asm err.asm hello.asm indx.asm leds.asm

OCTS=$(TESTS:.asm=.oct)

%.oct :
	python3 pymesm.py -i test/$@ -c 12000

%.asm :
	python3 asm/asm.py -i test/$@

all: build run

build: $(TESTS)

run: $(OCTS)

clean:
	rm test/*.oct

