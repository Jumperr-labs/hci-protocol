from __future__ import absolute_import, division, print_function, unicode_literals

import socket
import select
import struct
import logging
import argparse

from construct import RawCopy
from .hci_protocol import HciPacket

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class HciSniffer(object):
    def __init__(self, hci_device_number=0):
        self._hci_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_RAW, socket.BTPROTO_HCI)
        self._hci_socket.setsockopt(socket.SOL_HCI, socket.HCI_DATA_DIR, 1)
        self._hci_socket.setsockopt(socket.SOL_HCI, socket.HCI_TIME_STAMP, 1)
        self._hci_socket.setsockopt(
            socket.SOL_HCI, socket.HCI_FILTER, struct.pack("IIIH2x", 0xffffffffL, 0xffffffffL, 0xffffffffL, 0)
        )
        self._hci_socket.bind((hci_device_number,))
        self._hci_device_number = hci_device_number

    def run(self):
        while True:
            readable, _, _ = select.select([self._hci_socket], [], [])
            if readable is not None:
                packet = self._hci_socket.recv(4096)
                log.info('SOCKET: %s', RawCopy(HciPacket).parse(packet))


def main():
    logging.basicConfig(level=logging.WARNING)
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument('--hci', type=int, default=0, help='The number of HCI device to connect to')
    parser.add_argument('--log-file', type=str, default=None, help='Dumps log to file')
    args = parser.parse_args()
    if args.log_file is not None:
        log.addHandler(logging.FileHandler(args.log_file))
    hci_sniffer = HciSniffer(args.hci)
    try:
        hci_sniffer.run()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
