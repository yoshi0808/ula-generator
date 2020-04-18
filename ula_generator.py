#!/usr/bin/env python3
'''
IPv6 Unique Local Address Generator (RFC4193)
https://github.com/yoshi0808/Utils
Copyright (c) 2020 Yoshi0808(Yoshinobu Abe)

Released under the MIT license.
see https://opensource.org/licenses/MIT

usage: python3 ula_generator.py
        [input]xx:xx:xx:xx:xx:xx(Enter)    <-your mac address
        [output]ULA Prefix-> fdxx:xxxx:xxxx::/48
                First Subnet-> fdxx:xxxx:xxxx::/64
                Last Subnet-> fdxx:xxxx:xxxx:ffff::/64
                First IPv6 Address-> fdxx:xxxx:xxxx::1/64
 '''

import re
import hashlib
import time
from datetime import datetime, date, timezone


def input_mac_address():
    mac_address = input('Input MAC address:\n')
    result = re.match('^[0-9a-f]{2}([:-][0-9a-f]{2}){5}$', mac_address, re.I)
    if result:
        return mac_address
    else:
        return result


def gen_eui64(mac_address):
    # RFC4291 Appenix A: Generate 'Modified EUI-64'
    eui64 = re.sub(r'[:-]', '', mac_address).lower()
    eui64 = eui64[0:6] + 'fffe' + eui64[6:12]
    rev = int(eui64[0:2], 16) ^ 0b00000010  # Invert the 7th bit.
    eui64 = str(format(rev, 'x')) + eui64[2:16]
    return eui64


def get_ntp64time_string():
    dt = datetime.now(timezone.utc)

    tm = dt.timestamp()
    NTP_EPOCH = date(1900, 1, 1)
    SYSTEM_EPOCH = date(*time.gmtime(0)[0:3])
    NTP_DELTA = (SYSTEM_EPOCH - NTP_EPOCH).days * 24 * 3600
    tm += NTP_DELTA
    # RFC4330
    # The integer part of NTP (32 bits) field will overflow some time in
    #  2036(second 4,294,967,296), but it will work.
    tm_upper = int(tm)
    tm_lower_str = ('{0:.10f}'.format(tm - tm_upper))[2:12]
    tm_upper_str = format(tm_upper & 0xffffffff, 'x')
    # Create a 64bit string
    tm_x64 = tm_upper_str.zfill(8) + str(
        format(int(tm_lower_str), 'x').ljust(8, '0'))[0:8]
    return tm_x64


def main():
    mac_address = input_mac_address()
    if not mac_address:
        print('Bad Mac Address')
    else:
        h = hashlib.sha1()
        # Make sha1 digest
        h.update((get_ntp64time_string() + gen_eui64(mac_address)).encode())
        # Use the lower 40 bits of the 160 bits(sha1 digest) as a global ID.
        global_id = h.hexdigest()[30:40]
        prefix = ':'.join(
            ('fd' + global_id[0:2], format(int(global_id[2:6], 16), 'x'),
             format(int(global_id[6:10], 16), 'x')))
        print('ULA Prefix        -> ' + prefix + '::/48')
        print('First Subnet      -> ' + prefix + '::/64')
        print('Last Subnet       -> ' + prefix + ':ffff::/64')
        print('First IPv6 Address-> ' + prefix + '::1/64')


if __name__ == "__main__":
    main()
