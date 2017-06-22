from __future__ import absolute_import, division, print_function, unicode_literals

import logging

from construct import *

log = logging.getLogger(__name__)


def ByteSwappedKnownSize(subcon, size):
    r"""
    WARNING: this is a hack for using ByteSwapped on ocf which is created by switch, better to avoid this when you can
    Swap the byte order within boundaries of the given subcon.
    
    :param subcon: the subcon on top of byte swapped bytes
    
    :param size: The size of returned item in Bytes
    
    Example::
    
        Int24ul <--> ByteSwapped(Int24ub)
    """
    return Restreamed(
        subcon,
        lambda s: s[::-1], size,
        lambda s: s[::-1], size,
        lambda n: n
    )


# ============================================================================
# COMMON
# ============================================================================
MacAddress = ExprAdapter(Byte[6],
                         encoder=lambda obj, ctx: [x for x in reversed([int(part, 16) for part in obj.split(":")])],
                         decoder=lambda obj, ctx: ":".join("%02x" % b for b in reversed(obj)),
                         )


# ============================================================================
# HCI COMMAND PACKET
# ============================================================================
ogf = Enum(BitsInteger(6),
           INFORMATIONAL_PARAMETERS=0x04,
           default=Pass
           )

ocf = Switch(
    this.ogf,
    {
        'INFORMATIONAL_PARAMETERS': Enum(BitsInteger(10), READ_BD_ADDRESS_COMMAND=0x0009, default=Pass)
    },
    default=BitsInteger(10)
)

OgfOcfPair = ByteSwappedKnownSize(
    BitStruct(
        "ogf" / ogf,
        "ocf" / ocf
    ),
    2
)

HciCommandPacket = "hci_command_packet" / Struct(
    Embedded(OgfOcfPair),
    "length" / Int8ul,
    "payload" / Array(this.length, Byte),
)


# ============================================================================
# ACL DATA PACKET
# ============================================================================
ATT_CID = 4

AttOpcode = Enum(
    Int8ul,
    ATT_OP_ERROR_RESPONSE=0x01,
    ATT_OP_MTU_REQUEST=0x02,
    ATT_OP_MTU_RESPONSE=0x03,
    ATT_OP_READ_BY_TYPE_REQUEST=0x08,
    ATT_OP_READ_BY_TYPE_RESPONSE=0x09,
    ATT_OP_READ_REQUEST=0x0A,
    ATT_OP_READ_RESPONSE=0x0B,
    ATT_OP_READ_BLOB_REQUEST=0x0C,
    ATT_OP_READ_BLOB_RESPONSE=0x0D,
    ATT_OP_READ_MULTIPLE_REQUEST=0x0E,
    ATT_OP_READ_MULTIPLE_RESPONSE=0x0F,
    ATT_OP_READ_BY_GROUP_REQUEST=0x010,
    ATT_OP_READ_BY_GROUP_RESPONSE=0x11,
    ATT_OP_HANDLE_NOTIFY=0x1B,
    ATT_OP_WRITE_REQUEST=0x12,
    ATT_OP_WRITE_RESPONSE=0x13,
    default=Pass
)

AttErrorCode = Enum(
    Int8ul,
    Invalid_Handle=0x01,
    Read_Not_Permitted=0x02,
    Write_Not_Permitted=0x03,
    Invalid_PDU=0x04,
    Insufficient_Authentication=0x05,
    Request_Not_Supported=0x06,
    Invalid_Offset=0x07,
    Insufficient_Authorization=0x08,
    Prepare_Queue_Full=0x09,
    Attribute_Not_Found=0x0A,
    Attribute_Not_Long=0x0B,
    Insufficient_Encryption_Key_Size=0x0C,
    Invalid_Attribute_Value_Length=0x0D,
    Unlikely_Error=0x0E,
    Insufficient_Encryption=0x0F,
    Unsupported_Group_Type=0x10,
    Insufficient_Resources=0x11
)

AttOpErrorResponse = "att_error_response_packet" / Struct(
    "request_opcode_in_error" / AttOpcode,
    "attribute_handle_in_error" / Int16ul,
    "error_code" / AttErrorCode
)

AttMtuRequestPacket = "att_mtu_request_packet" / Struct(
    "client_mtu" / Int16ul
)

AttMtuResponsePacket = "att_mtu_response_packet" / Struct(
    "server_mtu" / Int16ul
)

AttributeHandleValuePair = "attribute_handle_value_pair" / Struct(
    "handle" / Int16ul,
    "value" / Bytes(this._.length - 2)
)

AttReadByTypeRequest = "read_by_type_request" / Struct(
    "starting_handle" / Int16ul,
    "ending_handle" / Int16ul,
    "attribute_type" / Bytes(this._._.length - 5)
)

AttReadByTypeResponse = "read_by_type_response" / Struct(
    "length" / Int8ul,
    "attribute_data_list" / AttributeHandleValuePair[(this._._.length - 2) / this.length]
)

AttReadRequest = 'read_request' / Struct(
    "handle" / Int16ul
)

AttReadResponse = 'read_response' / Struct(
    "value" / BytesInteger(this._._.length - 1, swapped=True)
)

AttReadByGroupResponse = "read_by_group_response" / Struct(
    "length" / Int8ul,
    "attribute_data_list" / AttributeHandleValuePair[(this._._.length - 2) / this.length]
)

HandleValueNotification = "handle_value_notification" / Struct(
    "handle" / Int16ul,
    "data" / Bytes(this._._.length - 3)
)

AttWriteRequest = "att_write_request" / Struct(
    "handle" / Int16ul,
    "data" / BytesInteger(this._._.length - 3, swapped=True)
)

AttCommandPacket = "att_command_packet" / Struct(
    "opcode" / AttOpcode,
    "payload" / Switch(this.opcode, {
        "ATT_OP_ERROR_RESPONSE": AttOpErrorResponse,
        "ATT_OP_MTU_REQUEST": AttMtuRequestPacket,
        "ATT_OP_MTU_RESPONSE": AttMtuResponsePacket,
        "ATT_OP_READ_BY_TYPE_REQUEST": AttReadByTypeRequest,
        "ATT_OP_READ_BY_TYPE_RESPONSE": AttReadByTypeResponse,
        "ATT_OP_READ_REQUEST": AttReadRequest,
        "ATT_OP_READ_RESPONSE": AttReadResponse,
        "ATT_OP_READ_BY_GROUP_RESPONSE": AttReadByGroupResponse,
        "ATT_OP_HANDLE_NOTIFY": HandleValueNotification,
        "ATT_OP_WRITE_REQUEST": AttWriteRequest,
        "ATT_OP_WRITE_RESPONSE": Pass
    }, default=Array(this._.length - 1, Byte))
)

L2CapPacket = "l2cap_packet" / Struct(
    "length" / Int16ul,
    # "length" / Switch(this.cid, {
    #     ATT_CID: Rebuild(Int16ul, lambda x: AttCommandPacket.sizeof(x.payload))
    # }, default=Int16ul),
    "cid" / Int16ul,
    "payload" / Switch(this.cid, {
        ATT_CID: AttCommandPacket
    }, default=Array(this.length, Byte))
)

AclDataPacket = "hci_acl_data_packet" / Struct(
    Embedded(ByteSwapped(
        BitStruct(
            "flags" / BitsInteger(4),
            "handle" / BitsInteger(12)
        )
    )),
    "length" / Rebuild(Int16ul, this.payload.length + 4),
    "payload" / L2CapPacket
)


# ============================================================================
# HCI EVENT PACKET
# ============================================================================
CommandCompletedEvent = "command_complete_event" / Struct(
    "ncmd" / Int8ul,
    Embedded(OgfOcfPair),
    "status" / Int8ul,
    "payload" / Switch(
        this.ogf,
        {
            'INFORMATIONAL_PARAMETERS': Switch(this.ocf,
                                               {'READ_BD_ADDRESS_COMMAND': MacAddress},
                                               default=Array(this._.length - 4, Byte)
                                               ),
        },
        default=Array(this._.length - 4, Byte),
    )
)

DisconnectEvent = "hci_disconnect_event" / Struct(
    "status" / Int8ul,
    "handle" / Int16ul,
    "reason" / Int8ul
)

LeConnectionCompleteEvent = "connection_complete_event" / Struct(
    "status" / Int8ul,
    "handle" / Int16ul,
    "role" / Int8ul,
    "peer_bdaddr_type" / Int8ul,
    "peer_bdaddr" / MacAddress,
    "interval" / Int16ul,
    "latency" / Int16ul,
    "supervision_timeout" / Int16ul,
    "master_clock_accuracy" / Int8ul
)

LeConnectionUpdateCompleteEvent = "hci_evt_le_conn_update_complete" / Struct(
    "status" / Int8ul,
    "handle" / Int16ul,
    "interval" / Int16ul,
    "latency" / Int16ul,
    "supv_timeout" / Int16ul
)

LeMetaEvent = "hci_le_meta_event" / Struct(
    "subevent" / Enum(Int8ul,
                      LE_CONNECTION_COMPLETED=0x01,
                      LE_CONNECTION_UPDATE_COMPLETED=0x03,
                      default=Pass
                      ),
    "payload" / Switch(this.subevent,
                       {
                           "LE_CONNECTION_COMPLETED": LeConnectionCompleteEvent,
                           "LE_CONNECTION_UPDATE_COMPLETED": LeConnectionUpdateCompleteEvent
                       }, default=Array(this._.length - 1, Byte)
                       )
)

ErrorCode = Enum(
    Int8ul,
    SUCCESS=0x00,
    UNKNOWN_HCI_COMMAND=0x01,
    UNKNOWN_CONNECTION_IDENTIFIER=0x02,
    HARDWARE_FAILURE=0x03,
    PAGE_TIMEOUT=0x04,
    AUTHENTICATION_FAILURE=0x05,
    PIN_OR_KEY_MISSING=0x06,
    MEMORY_CAPACITY_EXCEEDED=0x07,
    CONNECTION_TIMEOUT=0x08,
    CONNECTION_LIMIT_EXCEEDED=0x09,
    SYNCHRONOUS_CONNECTION_LIMIT_TO_A_DEVICE_EXCEEDED=0x0A,
    CONNECTION_ALREADY_EXISTS=0x0B,
    COMMAND_DISALLOWED=0x0C,
    CONNECTION_REJECTED_DUE_TO_LIMITED_RESOURCES=0x0D,
    CONNECTION_REJECTED_DUE_TO_SECURITY_REASONS=0x0E,
    CONNECTION_REJECTED_DUE_TO_UNACCEPTABLE_BD_ADDR=0x0F,
    CONNECTION_ACCEPT_TIMEOUT_EXCEEDED=0x10,
    UNSUPPORTED_FEATURE_OR_PARAMETER_VALUE=0x11,
    INVALID_HCI_COMMAND_PARAMETERS=0x12,
    REMOTE_USER_TERMINATED_CONNECTION=0x13,
    REMOTE_DEVICE_TERMINATED_CONNECTION_DUE_TO_LOW_RESOURCES=0x14,
    REMOTE_DEVICE_TERMINATED_CONNECTION_DUE_TO_POWER_OFF=0x15,
    CONNECTION_TERMINATED_BY_LOCAL_HOST=0x16,
    REPEATED_ATTEMPTS=0x17,
    PAIRING_NOT_ALLOWED=0x18,
    UNKNOWN_LMP_PDU=0x19,
    UNSUPPORTED_REMOTE_OR_LMP_FEATURE=0x1A,
    SCO_OFFSET_REJECTED=0x1B,
    SCO_INTERVAL_REJECTED=0x1C,
    SCO_AIR_MODE_REJECTED=0x1D,
    INVALID_LMP_OR_LL_PARAMETERS=0x1E,
    UNSPECIFIED_ERROR=0x1F,
    UNSUPPORTED_LMP_OR_LL_PARAMETER_VALUE=0x20,
    ROLE_CHANGE_NOT_ALLOWED=0x21,
    LMP_OR_LL_RESPONSE_TIMEOUT=0x22,
    LMP_ERROR_TRANSACTION_COLLISION_OR_LL_PROCEDURE_COLLISION=0x23,
    LMP_PDU_NOT_ALLOWED=0x24,
    ENCRYPTION_MODE_NOT_ACCEPTABLE=0x25,
    LINK_KEY_CANNOT_BE_CHANGED=0x26,
    REQUESTED_QOS_NOT_SUPPORTED=0x27,
    INSTANT_PASSED=0x28,
    PAIRING_WITH_UNIT_KEY_NOT_SUPPORTED=0x29,
    DIFFERENT_TRANSACTION_COLLISION=0x2A,
    RESERVED_FOR_FUTURE_USE=0x2B,
    QOS_UNACCEPTABLE_PARAMETER=0x2C,
    QOS_REJECTED=0x2D,
    CHANNEL_CLASSIFICATION_NOT_SUPPORTED=0x2E,
    INSUFFICIENT_SECURITY=0x2F,
    PARAMETER_OUT_OF_MANDATORY_RANGE=0x30,
    ROLE_SWITCH_PENDING=0x32,
    RESERVED_SLOT_VIOLATION=0x34,
    ROLE_SWITCH_FAILED=0x35,
    EXTENDED_INQUIRY_RESPONSE_TOO_LARGE=0x36,
    SECURE_SIMPLE_PAIRING_NOT_SUPPORTED_BY_HOST=0x37,
    HOST_BUSY_PAIRING=0x38,
    CONNECTION_REJECTED_DUE_TO_NO_SUITABLE_CHANNEL_FOUND=0x39,
    CONTROLLER_BUSY=0x3A,
    UNACCEPTABLE_CONNECTION_PARAMETERS=0x3B,
    ADVERTISING_TIMEOUT=0x3C,
    CONNECTION_TERMINATED_DUE_TO_MIC_FAILURE=0x3D,
    CONNECTION_FAILED_TO_BE_ESTABLISHED=0x3E,
    MAC_CONNECTION_FAILED=0x3F,
    COARSE_CLOCK_ADJUSTMENT_REJECTED_BUT_WILL_TRY_TO_ADJUST_USING_CLOCK_DRAGGING=0x40,
    TYPE0_SUBMAP_NOT_DEFINED=0x41,
    UNKNOWN_ADVERTISING_IDENTIFIER=0x42,
    LIMIT_REACHED=0x43,
    OPERATION_CANCELLED_BY_HOST=0x44,
    default=Pass
)

CommandStatusEvent = "hci_command_status_event" / Struct(
    "status" / ErrorCode,
    "num_hci_command_packets" / Int8ul,
    "command_opcode" / Int16ul
)

NumberOfCompletedPacketsEvent = "hci_number_of_completed_packets_event" / Struct(
    "number_of_handles" / Rebuild(Int8ul, len_(this.connection_handles)),
    "connection_handles" / Array(this.number_of_handles, Int16ul),
    "number_of_completed_packets" / Array(this.number_of_handles, Int16ul)
)

HciEventPacket = "hci_event_packet" / Struct(
    "event" / Enum(Int8ul,
                   DISCONNECTION_COMPLETE=0x05,
                   COMMAND_COMPLETE=0x0E,
                   COMMAND_STATUS=0x0F,
                   NUMBER_OF_COMPLETED_PACKETS=0x13,
                   LE_META_EVENT=0x3E,
                   default=Pass
                   ),
    "length" / Switch(this.event,
                      {
                          "NUMBER_OF_COMPLETED_PACKETS": Rebuild(Int8ul, lambda x: NumberOfCompletedPacketsEvent.sizeof(x.payload)),
                          "LE_META_EVENT": Rebuild(Int8ul, lambda x: LeMetaEvent.sizeof(x.payload)),
                      }, default=Int8ul
                      ),
    "payload" / Switch(this.event,
                       {
                           "DISCONNECTION_COMPLETE": DisconnectEvent,
                           "COMMAND_COMPLETE": CommandCompletedEvent,
                           "COMMAND_STATUS": CommandStatusEvent,
                           "NUMBER_OF_COMPLETED_PACKETS": NumberOfCompletedPacketsEvent,
                           "LE_META_EVENT": LeMetaEvent
                       }, default=Array(this.length, Byte),
                       ),
)


# ============================================================================
# HCI SYNCHRONOUS DATA PACKET
# ============================================================================
HciSynchronousDataPacket = "hci_synchronous_data_packet" / Struct(
    Embedded(
        ByteSwapped(
            Struct(
                "connection_handle" / BytesInteger(12),
                "packet_status_flag" / BitsInteger(2),
                "RFU" / BitsInteger(2)
            )
        )
    ),
    "data_total_length" / Int8ul,
    "data" / Bytes(this.length)
)

# ============================================================================
# HCI PACKET
# ============================================================================
HciPacket = "hci_packet" / Struct(
    "type" / Enum(Int8ul,
                  COMMAND_PACKET=0x01,
                  ACL_DATA_PACKET=0x02,
                  SYNCHRONOUS_DATA_PACKET=0x03,
                  EVENT_PACKET=0x04,
                  default=Pass
                  ),
    "payload" / Switch(this.type,
                       {
                           "COMMAND_PACKET": HciCommandPacket,
                           "ACL_DATA_PACKET": AclDataPacket,
                           "EVENT_PACKET": HciEventPacket,
                           "SYNCHRONOUS_DATA_PACKET": HciSynchronousDataPacket
                       }, default=Pass
                       ),
)
