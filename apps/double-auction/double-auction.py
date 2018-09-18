#!/usr/bin/env python

# Copyright 2007, 2008 VIFF Development Team.
#
# This file is part of VIFF, the Virtual Ideal Functionality Framework.
#
# VIFF is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# VIFF is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with VIFF. If not, see <http://www.gnu.org/licenses/>.

# Double auction test. The double auction is implemented as described
# in "Secure Integer Computation with Applications in Economics", a
# PhD Progrees Report by Tomas Toft.
#
# The double auction finds the market clearing price in an auction
# where sellers can specify how much they want to sell at a given unit
# price, and where buyers specify how much they want to buy. The sell
# bids increase (since you want to sell more if the price per item
# increases) whereas the buy bids are decreasing.
#
# TODO: This implementation cheats by not distributing the sell and
# buy bids. This was originally simpler to program it that way.
#
# TODO: Note also, that the players must be run with the same seed.
# This is necessary to obtain consistent shares. This restriction will
# be removed when the shares are distributed correctly as per the
# previous TODO item.

import time, random
from optparse import OptionParser

import viff.reactor
viff.reactor.install()
from twisted.internet import reactor

from viff import shamir
from viff.field import GF
from viff.runtime import Runtime, create_runtime, Share
from viff.config import load_config
from viff.util import find_prime

def output(x, format="output: %s"):
    print format % x
    return x

last_timestamp = time.time()
def timestamp():
    global last_timestamp
    now = time.time()
    print "Delta: %8.3f ms" % (1000*(now-last_timestamp))
    last_timestamp = now

parser = OptionParser()
parser.add_option("-m", "--modulus",
                  help="lower limit for modulus (can be an expression)")
parser.add_option("-c", "--count", type="int",
                  help="number of bids")
parser.add_option("-v", "--verbose", action="store_true",
                  help="verbose output after each iteration")
parser.add_option("-q", "--quiet", action="store_false",
                  help="little output after each iteration")

parser.set_defaults(modulus="30916444023318367583",
                    verbose=False, count=4000)

# Add standard VIFF options.
Runtime.add_options(parser)

(options, args) = parser.parse_args()

if len(args) == 0:
    parser.error("you must specify a config file")

Zp = GF(find_prime(options.modulus, blum=True))
id, players = load_config(args[0])

print "I am player %d" % id

l = options.bit_length
print "l: ", l
t = (len(players) -1)//2
n = len(players)

# Shares of seller and buyer bids. Assume that each bidder and seller
# has secret shared the bids and encrypted them for each player. These
# have then been read, decrypted and summed up...

random.seed(0)

# Generate random bids -- we could generate numbers up to 2**l, but
# restricting them to only two digits use less space in the output.
B = [random.randint(1, 2**l) for _ in range(options.count)]
S = [random.randint(1, 2**l) for _ in range(options.count)]
# print "B: ", B, "S: ", S

# Make the bids monotone.
B.sort(reverse=True)
S.sort()

# seller_bids = [Share(Zp(x), t, n)[id-1][1] for x in S]
# print type(seller_bids[])
# print "seller_bids length: ", len(seller_bids)
# print "seller_bids[0]: ", seller_bids[0]

# buyer_bids  = [Share(Zp(x), t, n)[id-1][1] for x in B]
# print "buyer_bids length: ", len(buyer_bids)

def auction(rt):
    seller_bids = [Share(rt, Zp(x), t, n)[id-1][1] for x in S]
    buyer_bids  = [Share(rt, Zp(x), t, n)[id-1][1] for x in B]


    def debug(low, mid, high):
        print "hi"
        string = ["  " for _ in range(high+1)]
        string[low] = " |"
        string[mid] = " ^"
        string[high] = " |"

        # print "B: " + " ".join(["%2d" % b for b in B])
        # print "S: " + " ".join(["%2d" % s for s in S])
        # print "   " + " ".join(["%2d" % x for x in range(len(B)+1)])
        # print "   " + " ".join(string)

    def branch(result, low, mid, high):
        print "low: %d, high: %d, last result: %s" % (low, high, result)
        timestamp()

        if result == 1:
            low = mid
        else:
            high = mid

        if low+1 < high:
            print " ENTER LINE 134..."
            mid = (low + high)//2
            print "mid: ", mid
            if options.verbose:
                debug(low, mid, high)
            print "resul = , before open"
            # print buyer_bids[mid]
            # print rt.open(buyer_bids[mid])
            # print "open: ", buyer_bids[mid]
            # print seller_bids[mid]
            print "comp: ", buyer_bids[mid] >= seller_bids[mid]
            # print type(Share(rt, buyer_bids[mid]))
            result = rt.open(buyer_bids[mid] >= seller_bids[mid])
            print "result = ", result
            result.addCallback(output, "%s >= %s: %%s" % (B[mid], S[mid]))
            result.addCallback(branch, low, mid, high)
            print "." * 10, " branch end ", "." * 10
            return result
        else:
            print " ENTER LINE 145..."
            if options.verbose:
                debug(low, mid, high)
            print "." * 10, " branch end ", "." * 10
            return low

    def check_result(result):
        print "." * 10, "enter check_result", "." * 10
        expected = max([i for i, (b, s) in enumerate(zip(B, S)) if b > s])
        if result == expected:
            print "Result: %d (correct)" % result
        else:
            print "Result: %d (incorrect, expected %d)" % (result, expected)

    result = branch(0, 0, len(seller_bids), 0)
    result.addCallback(check_result)
    result.addCallback(lambda _: reactor.stop())

pre_runtime = create_runtime(id, players, t, options)
print "." * 10, "on the way", "." * 10
pre_runtime.addCallback(auction)

reactor.run()
