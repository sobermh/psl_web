# 平台下发控制类命令
from psl_socket.crc32 import calculate_crc32

# 0x00:主模块通道

# 控制命令号
# 0x00:
# 0x01:
# 0x02:
def control_cmd(device_serial_number=b'00000001',command_content=b'\x01'):
    frame_header = b'\x55\xAA'
    device_serial_number = device_serial_number  # 8 bytes ASCII
    channel_number = b'\x00'
    command_type = b'\x00'
    data_length = b'\x02\x02'
    command_content = command_content

    # Combine all parts to form the data packet (excluding CRC32 for now)
    data_packet = frame_header + device_serial_number + channel_number + command_type + data_length + command_content


    # Calculate CRC32
    crc32 = calculate_crc32(data_packet,len(data_packet))
    crc32_bytes = crc32.to_bytes(4, byteorder='big')  # Convert to 4 bytes

    # Form the final data packet with CRC32
    final_packet = data_packet + crc32_bytes

    # # Convert to hex string with '0x' prefix for each byte
    # final_packet_hex = ''.join(f'0x{byte:02X}' for byte in final_packet)
    return final_packet


# 0x00:主模块通道
# 0x01:从模块通道

# 读取命令号
# 0x00:
# 0x01:
# 0x02:
def read_cmd(device_serial_number=b'00000001',channel_number=b'\x00',command_content=b'\x01'):
    frame_header = b'\x55\xAA'
    device_serial_number = device_serial_number  # 8 bytes ASCII
    channel_number = channel_number
    command_type = b'\x01'
    data_length = b'\x02\x02'
    command_content = command_content

    # Combine all parts to form the data packet (excluding CRC32 for now)
    data_packet = frame_header + device_serial_number + channel_number + command_type + data_length + command_content


    # Calculate CRC32
    crc32 = calculate_crc32(data_packet,len(data_packet))
    crc32_bytes = crc32.to_bytes(4, byteorder='big')  # Convert to 4 bytes

    # Form the final data packet with CRC32
    final_packet = data_packet + crc32_bytes

    return final_packet



# 0x00:主模块通道
# 0x01:从模块通道
def read_img_cmd(device_serial_number=b'00000001',channel_number=b'\x00'):
    frame_header = b'\x55\xAA'
    device_serial_number = device_serial_number  # 8 bytes ASCII
    channel_number = channel_number
    command_type = b'\x02'

    # Combine all parts to form the data packet (excluding CRC32 for now)
    data_packet = frame_header + device_serial_number + channel_number + command_type


    # Calculate CRC32
    crc32 = calculate_crc32(data_packet,len(data_packet))
    crc32_bytes = crc32.to_bytes(4, byteorder='big')  # Convert to 4 bytes

    # Form the final data packet with CRC32
    final_packet = data_packet + crc32_bytes

    return final_packet
