#!/usr/bin/env python
import sys

import viff.reactor
viff.reactor.install()
from twisted.internet import reactor

from viff.field import GF, GF256, FieldElement
from viff.edwards import *
import time

from viff.runtime import create_runtime
from viff.config import load_config
from viff.util import dprint



# the order of jubjub base field
q = 0x73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000001
Fq = GF(q)

dd = -(Fq(10240)/Fq(10241))

curve = TwistedEdwardsCurve(Fq(-1), dd)

p1 = Point(curve, 0,1)
p2 = Point(curve, 5, 6846412461894745224441235558443359243034138132682534265960483512729196124138)
p3 = Point(curve, 10, 9069365299349881324022309154395348339753339814197599672892180073931980134853)
p4 = Point(curve, 20, 19591689915777126424527574975649725331665833659101192930707046924393354292087)
p5 = Point(curve, 21, 7077199607858622853608570958787827897736274549921838431359778037825087697958)
p6 = Point(curve, 28, 6872713299796450981547816838430986612693130632041108310621050902354381807248)

def test(curve):
	p = Point(curve, Fq(0x18ea85ca00cb9d895cb7b8669baa263fd270848f90ebefabe95b38300e80bde1), Fq(0x255fa75b6ef4d4e1349876df94ca8c9c3ec97778f89c0c3b2e4ccf25fdf9f7c1))
	q = Point(curve, Fq(0x1624451837683b2c4d2694173df71c9174ffcc613788eef3a9c7a7d0011476fa), Fq(0x6f76dbfd7c62860d59f5937fa66d0571158ff68f28ccd83a4cd41b9918ee8fe2))
	t0 = time.time()
	for i in range(50000):
		p = p + q
	t1 = time.time()
	print curve, "time: ", t1 - t0

test(curve)
############################################################

class Protocol:

	def __init__(self, runtime):
		self.rt = runtime

	def function():
		pass
		

id, players = load_config(sys.argv[1])



pre_runtime = create_runtime(id, players, 1)
pre_runtime.addCallback(protocol)

reactor.run()
