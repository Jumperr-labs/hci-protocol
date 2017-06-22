from __future__ import absolute_import, division, print_function, unicode_literals

from .hci_protocol import *
import struct


def create_le_connection_comlete_packet(peer_address, connection_handle):
    return HciPacket.build(
        dict(
            type='EVENT_PACKET',
            payload=dict(
                event='LE_META_EVENT',
                payload=dict(
                    subevent='LE_CONNECTION_COMPLETED',
                    payload=dict(
                        status=0,
                        handle=connection_handle,
                        role=0,
                        peer_bdaddr_type=1,
                        peer_bdaddr=peer_address,
                        interval=56,
                        latency=0,
                        supervision_timeout=42,
                        master_clock_accuracy=0
                    )
                )
            )
        )
    )

#
# def create_read_by_type_response_packet(connection_handle, gatt_handle, value, format):
#
#     packet = '02 46 20 1B 00 17 00 04 00 09 07 02 00 0A 03 00 00 2A 04 00'.replace(' ', '').decode("hex")
#
    # return HciPacket.build(
    #     dict(
    #         type='ACL_DATA_PACKET',
    #         payload=dict(
    #             flags=2,
    #             handle=connection_handle,
    #             length=value_size_in_bytes + 8,
    #             payload=dict(
    #                 length=value_size_in_bytes + 4,
    #                 cid=ATT_CID,
    #                 payload=dict(
    #                     opcode='ATT_OP_READ_BY_TYPE_RESPONSE',
    #                     length=value_size_in_bytes + 2,
    #                     attribute_data_list=[dict(handle=gatt_handle, value=value)]
    #                 )
    #             )
    #         )
    #     )
    # )
