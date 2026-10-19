# TFTP: The Last Block

An intermediate packet-forensics challenge. Players inspect `capture.pcap`, export the TFTP objects, follow a two-note ROT13 clue chain, and XOR `policy.bin` with the repeating key revealed by the clues.

All teams use the same capture and the same correct flag. Browser sessions only keep each player's step progress; they do not generate team-specific answers.

Open the page from the Challenge Index. Wireshark can export the transferred files from **File → Export Objects → TFTP**. With TShark, use:

```sh
tshark -r capture.pcap --export-objects tftp,out_dir
```

The private validator is `challenge.py`. To rebuild the fixed capture, set `TFTP_CHALLENGE_FLAG` to the same value as the validator and run `python build_capture.py`.
