# Copyright 2008 VIFF Development Team.
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

"""Equality protocol. The mixin class defined here provide an
:meth:`equal` method to the :class:`Runtime <viff.runtime.Runtime>` it
is mixed with.
"""

class DeterministicEqualityMixin:
    """This class implements probabilistic constant-round secure
    equality-testing of secret shared numbers."""

    def equal(self, share_x, share_y):
        """Equality testing with secret shared result.

        TODO: Make it work for any prime-modulo, the b's should be in
        {y,1} where y is a non-square modulo p.

        TODO: Make the final "and"ing of the x's more efficient as
        described in the paper.
        """

        Zp = share_x.field

        a = share_x - share_y # We will check if a == 0
        k = self.options.security_parameter

        def gen_test_bit():
            r = self.prss_share_random(Zp)

            # If b_i == 1 c_i will always be a square modulo p if a is
            # zero and with probability 1/2 otherwise (except if rp == 0).
            # If b_i == -1 it will be non-square.
            c = self.open(a + r)
            return self.schedule_callback(c, finish, r)

        def finish(cj, rj):
            if cj == 1:
                xj = rj
            elif cj == 0:
                xj = Zp(1) - rj
            else:
                # Start over.
                xj = gen_test_bit()
            return xj

        x = [gen_test_bit() for _ in range(k)]

        # Take the product (this is here the same as the "and") of all
        # the x'es
        while len(x) > 1:
            x.append(x.pop(0) * x.pop(0))

        return x[0]

