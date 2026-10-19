"""Build the fixed educational TFTP packet capture using Python's stdlib."""

from __future__ import annotations

import ipaddress
import os
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CLIENT_IP = "10.10.10.10"
SERVER_IP = "10.10.10.20"
CLIENT_MAC = bytes.fromhex("020000000010")
SERVER_MAC = bytes.fromhex("020000000020")
BASE_TIMESTAMP = 1_792_000_000


def rot13(text: str) -> str:
    output = []
    for char in text:
        if "a" <= char <= "z":
            output.append(chr((ord(char) - ord("a") + 13) % 26 + ord("a")))
        elif "A" <= char <= "Z":
            output.append(chr((ord(char) - ord("A") + 13) % 26 + ord("A")))
        else:
            output.append(char)
    return "".join(output)


def internet_checksum(data: bytes) -> int:
    if len(data) % 2:
        data += b"\0"
    total = sum(struct.unpack(f"!{len(data) // 2}H", data))
    total = (total & 0xFFFF) + (total >> 16)
    total = (total & 0xFFFF) + (total >> 16)
    return (~total) & 0xFFFF


def ethernet_ipv4_udp(src_ip: str, dst_ip: str, src_port: int, dst_port: int,
                      payload: bytes, packet_id: int, from_client: bool) -> bytes:
    udp_length = 8 + len(payload)
    udp_header = struct.pack("!HHHH", src_port, dst_port, udp_length, 0)
    source = ipaddress.IPv4Address(src_ip).packed
    destination = ipaddress.IPv4Address(dst_ip).packed
    ip_header = struct.pack(
        "!BBHHHBBH4s4s", 0x45, 0, 20 + udp_length, packet_id,
        0x4000, 64, 17, 0, source, destination,
    )
    checksum = internet_checksum(ip_header)
    ip_header = struct.pack(
        "!BBHHHBBH4s4s", 0x45, 0, 20 + udp_length, packet_id,
        0x4000, 64, 17, checksum, source, destination,
    )
    source_mac, destination_mac = (CLIENT_MAC, SERVER_MAC) if from_client else (SERVER_MAC, CLIENT_MAC)
    frame = destination_mac + source_mac + b"\x08\x00" + ip_header + udp_header + payload
    return frame + (b"\0" * max(0, 60 - len(frame)))


def make_capture(flag: str) -> bytes:
    key = b"CROW"
    encrypted_flag = bytes(value ^ key[index % len(key)] for index, value in enumerate(flag.encode("ascii")))
    files = [
        ("welcome.txt", b"Router archive mirror. Backup window: 02:00 UTC.\n"),
        ("status.log", b"TFTP service healthy. No failed requests recorded.\n"),
        (
            "incident.txt",
            (rot13("The fieldguide is the next clue. ROT13 it, then follow its instructions.") + "\n").encode("ascii"),
        ),
        (
            "fieldguide.txt",
            (rot13("The payload is policy.bin. XOR it with the repeating key CROW.") + "\n").encode("ascii"),
        ),
        ("policy.bin", encrypted_flag),
    ]

    packets: list[bytes] = []
    packet_id = 1
    for transfer, (filename, contents) in enumerate(files):
        client_port = 41000 + transfer
        server_tid = 52000 + transfer
        request = b"\x00\x01" + filename.encode("ascii") + b"\x00octet\x00"
        packets.append(ethernet_ipv4_udp(CLIENT_IP, SERVER_IP, client_port, 69, request, packet_id, True))
        packet_id += 1

        chunks = [contents[offset:offset + 512] for offset in range(0, len(contents), 512)] or [b""]
        for block, chunk in enumerate(chunks, start=1):
            data = b"\x00\x03" + struct.pack("!H", block) + chunk
            packets.append(ethernet_ipv4_udp(SERVER_IP, CLIENT_IP, server_tid, client_port, data, packet_id, False))
            packet_id += 1
            ack = b"\x00\x04" + struct.pack("!H", block)
            packets.append(ethernet_ipv4_udp(CLIENT_IP, SERVER_IP, client_port, server_tid, ack, packet_id, True))
            packet_id += 1

    capture = bytearray(struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1))
    for index, packet in enumerate(packets):
        seconds = BASE_TIMESTAMP + index // 1000
        microseconds = (index % 1000) * 1000
        capture.extend(struct.pack("<IIII", seconds, microseconds, len(packet), len(packet)))
        capture.extend(packet)
    return bytes(capture)


def main() -> None:
    flag = os.environ.get("TFTP_CHALLENGE_FLAG", "").strip()
    if not flag:
        raise SystemExit("Set TFTP_CHALLENGE_FLAG to the fixed answer before generating the capture.")
    destination = ROOT / "capture.pcap"
    destination.write_bytes(make_capture(flag))
    print(f"Wrote {destination.name} ({destination.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
