# HCI Protocol
This is a Python package for parsing and building HCI packets.

HCI (Host Controller Interface) is the protocol used for communications between a BT/BLE controller (i.e. USB dongle) and a host computer such as a RPi.
Currently **only part of the protocol is implemented in this package** 

## Usage Examples
1. Hci Sniffer (Linux only): `python -m hci_protocol.hci_sniffer --hci 0`
2. Building a packet:
    ```python
    from hci_protocol import hci_functions
    hci_functions.create_le_connection_comlete_packet(peer_address='AA:BB:CC:DD:EE:FF', connection_handle=70)
    # ==> '\x04>\x13\x01\x00F\x00\x00\x01\xff\xee\xdd\xcc\xbb\xaa8\x00\x00\x00*\x00\x00'
    ```
    
3. Parsing a packet:
    ```python
    from hci_protocol.hci_protocol import HciPacket
    print HciPacket.parse('\x04>\x13\x01\x00F\x00\x00\x01\xff\xee\xdd\xcc\xbb\xaa8\x00\x00\x00*\x00\x00')
    # ==>
    #  Container:
    #      type = EVENT_PACKET (total 12)
    #      payload = Container:
    #          event = LE_META_EVENT (total 13)
    #          length = 19
    #          payload = Container:
    #              subevent = LE_CONNECTION_COMPLETED (total 23)
    #              payload = Container:
    #                  status = 0
    #                  handle = 70
    #                  role = 0
    #                  peer_bdaddr_type = 1
    #                  peer_bdaddr = aa:bb:cc:dd:ee:ff (total 17)
    #                  interval = 56
    #                  latency = 0
    #                  supervision_timeout = 42
    #                  master_clock_accuracy = 0
    ```
    
## Contribute
This package is in a preliminary stage and there is still a lot of work to do. Feel free to fork and submit your pull requests.

For more information about the HCI protocol, check out the [Blutooth Core Specifications](https://www.bluetooth.org/DocMan/handlers/DownloadDoc.ashx?doc_id=421043&_ga=2.29692863.121228451.1498147116-1432843607.1484151012)
