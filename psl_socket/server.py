import binascii
import socket
import threading
import time
import pymysql.cursors
import datetime




# MySQL数据库配置
MYSQL_HOST = '47.97.118.247'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'sober123456'
MYSQL_DATABASE = 'psl'


# 服务端配置
HOST = '0.0.0.0'  # 服务端 IP 地址
PORT = 9999        # 服务端端口

def read_img_cmd(device_serial_number=b'00000001',channel_number=b'\x00'):
    frame_header = b'\x55'
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

def  calculate_crc32(data,size):
    CRC_TABLE = [
        0x0000, 0x8005, 0x1800f, 0x1000a, 0x3801b, 0x3001e, 0x20014, 0x28011, 0x78033, 0x70036,
        0x6003c, 0x68039, 0x40028, 0x4802d, 0x58027, 0x50022, 0xf8063, 0xf0066, 0xe006c, 0xe8069,
        0xc0078, 0xc807d, 0xd8077, 0xd0072, 0x80050, 0x88055, 0x9805f, 0x9005a, 0xb804b, 0xb004e,
        0xa0044, 0xa8041, 0x1f80c3, 0x1f00c6, 0x1e00cc, 0x1e80c9, 0x1c00d8, 0x1c80dd, 0x1d80d7, 0x1d00d2,
        0x1800f0, 0x1880f5, 0x1980ff, 0x1900fa, 0x1b80eb, 0x1b00ee, 0x1a00e4, 0x1a80e1, 0x1000a0, 0x1080a5,
        0x1180af, 0x1100aa, 0x1380bb, 0x1300be, 0x1200b4, 0x1280b1, 0x178093, 0x170096, 0x16009c, 0x168099,
        0x140088, 0x14808d, 0x158087, 0x150082, 0x3f8183, 0x3f0186, 0x3e018c, 0x3e8189, 0x3c0198, 0x3c819d,
        0x3d8197, 0x3d0192, 0x3801b0, 0x3881b5, 0x3981bf, 0x3901ba, 0x3b81ab, 0x3b01ae, 0x3a01a4, 0x3a81a1,
        0x3001e0, 0x3081e5, 0x3181ef, 0x3101ea, 0x3381fb, 0x3301fe, 0x3201f4, 0x3281f1, 0x3781d3, 0x3701d6,
        0x3601dc, 0x3681d9, 0x3401c8, 0x3481cd, 0x3581c7, 0x3501c2, 0x200140, 0x208145, 0x21814f, 0x21014a,
        0x23815b, 0x23015e, 0x220154, 0x228151, 0x278173, 0x270176, 0x26017c, 0x268179, 0x240168, 0x24816d,
        0x258167, 0x250162, 0x2f8123, 0x2f0126, 0x2e012c, 0x2e8129, 0x2c0138, 0x2c813d, 0x2d8137, 0x2d0132,
        0x280110, 0x288115, 0x29811f, 0x29011a, 0x2b810b, 0x2b010e, 0x2a0104, 0x2a8101, 0x7f8303, 0x7f0306,
        0x7e030c, 0x7e8309, 0x7c0318, 0x7c831d, 0x7d8317, 0x7d0312, 0x780330, 0x788335, 0x79833f, 0x79033a,
        0x7b832b, 0x7b032e, 0x7a0324, 0x7a8321, 0x700360, 0x708365, 0x71836f, 0x71036a, 0x73837b, 0x73037e,
        0x720374, 0x728371, 0x778353, 0x770356, 0x76035c, 0x768359, 0x740348, 0x74834d, 0x758347, 0x750342,
        0x6003c0, 0x6083c5, 0x6183cf, 0x6103ca, 0x6383db, 0x6303de, 0x6203d4, 0x6283d1, 0x6783f3, 0x6703f6,
        0x6603fc, 0x6683f9, 0x6403e8, 0x6483ed, 0x6583e7, 0x6503e2, 0x6f83a3, 0x6f03a6, 0x6e03ac, 0x6e83a9,
        0x6c03b8, 0x6c83bd, 0x6d83b7, 0x6d03b2, 0x680390, 0x688395, 0x69839f, 0x69039a, 0x6b838b, 0x6b038e,
        0x6a0384, 0x6a8381, 0x400280, 0x408285, 0x41828f, 0x41028a, 0x43829b, 0x43029e, 0x420294, 0x428291,
        0x4782b3, 0x4702b6, 0x4602bc, 0x4682b9, 0x4402a8, 0x4482ad, 0x4582a7, 0x4502a2, 0x4f82e3, 0x4f02e6,
        0x4e02ec, 0x4e82e9, 0x4c02f8, 0x4c82fd, 0x4d82f7, 0x4d02f2, 0x4802d0, 0x4882d5, 0x4982df, 0x4902da,
        0x4b82cb, 0x4b02ce, 0x4a02c4, 0x4a82c1, 0x5f8243, 0x5f0246, 0x5e024c, 0x5e8249, 0x5c0258, 0x5c825d,
        0x5d8257, 0x5d0252, 0x580270, 0x588275, 0x59827f, 0x59027a, 0x5b826b, 0x5b026e, 0x5a0264, 0x5a8261,
        0x500220, 0x508225, 0x51822f, 0x51022a, 0x53823b, 0x53023e, 0x520234, 0x528231, 0x578213, 0x570216,
        0x56021c, 0x568219, 0x540208, 0x54820d, 0x558207, 0x550202
    ]

    
    crc = 0xfefdeaeb
    for i in range(size):
        da = crc >> 8
        crc = (crc << 8) & 0xFFFFFFFF
        crc ^= CRC_TABLE[(da ^ data[i]) & 0xFF]
    return crc

# 注意：crc_init_val 应设置为 0xfefdeaeb
# crc_init_val = 0xfefdeaeb



def handle_client(conn, addr, connection):
    """
    处理客户端连接的函数
    Args:
        conn (_type_): 连接对象
        addr (_type_): 连接设备地址
        connection: 数据库连接
    """
    print(f'客户端 {addr} 已连接.')
    
    packet_data = b''  # 初始化 packet_data 变量
    packet_size = -1    # 初始化包的大小
    img_data = b''      # 初始化图片

    # conn.send(read_img_cmd())
    # 定时发送控制命令的函数
    def send_command_interval(interval):
        while True:
            conn.send(read_img_cmd())
            time.sleep(interval)

    # 创建发送命令的线程
    send_thread = threading.Thread(target=send_command_interval, args=(20,))
    send_thread.daemon = True  # 设置为守护线程，程序退出时自动结束
    send_thread.start()

    # def handle_image_data(packet_id, image_data):
    #     # 处理图像数据并存入数据库
    #     with connection.cursor() as cursor:
    #         query = "INSERT INTO info (data, create_time) VALUES (%s, %s)"
    #         cursor.execute(query, (binascii.hexlify(image_data), datetime.datetime.today()))
    #         connection.commit()
    flag = 1
    try:
        while True:
            chunk = conn.recv(1)  # 逐字节接收数据
            if not chunk:
                print(f'客户端 {addr} 断开连接.')
                break
            if flag:
                flag = 0
                continue
            packet_data += chunk
            if len(packet_data) == 17:
                packet_size  = int.from_bytes(packet_data[15:17], byteorder='big') + 17 + 4
            if  len(packet_data)== packet_size:
                calculated_crc = calculate_crc32(packet_data[:-4], packet_size-4)
                received_crc = (packet_data[-4] << 24) | (packet_data[-3] << 16) | (packet_data[-2] << 8) | packet_data[-1]
                print(received_crc == calculated_crc)
                if calculated_crc == received_crc:
                    img_data += packet_data[17:-4]
                    print(int.from_bytes(packet_data[13:15], byteorder='big'))                

                    if int.from_bytes(packet_data[11:13], byteorder='big') == int.from_bytes(packet_data[13:15], byteorder='big'):
                        print(int.from_bytes(packet_data[11:13], byteorder='big'))

                        with connection.cursor() as cursor:
                            query = "INSERT INTO info (data,create_time) VALUES (%s,%s)"
                            cached_img_data = img_data
                            cursor.execute(query, (binascii.hexlify(cached_img_data),datetime.datetime.today()))
                            connection.commit()
                            img_data = b''
                packet_size = -1
                packet_data = b''
        # 关闭连接
        conn.close()
    except Exception as e:
        conn.close()
        print(str(e))




# 创建 TCP socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # 绑定地址和端口
    s.bind((HOST, PORT))
    # 开始监听连接
    s.listen()

    print(f'服务端正在监听端口 {PORT}...')

    # 连接到 MySQL 数据库
    connection = pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        cursorclass=pymysql.cursors.DictCursor
    )

    while True:
        # 接受客户端连接
        conn, addr = s.accept()
        # 创建一个新的线程来处理客户端连接
        thread = threading.Thread(target=handle_client, args=(conn, addr,connection))
        thread.start()


    