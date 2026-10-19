# Ubuntu CTF VM deployment

This deploys the four original challenges as separate services, plus one shared backend for the 27 self-contained browser challenges. Nginx serves their public pages and challenge artifacts and proxies API requests to the backend on localhost. The backend keeps each browser session's progress in SQLite. The portal uses the VM's current hostname/IP for service links, so DHCP address changes do not require editing the challenge list.

| Challenge | URL | Service |
| --- | --- | --- |
| Portal | `http://<VM-IP>/` | Nginx |
| Ancient Bedrock Guardian (AI-1) | `http://<VM-IP>:5000/` | `ctf-ai.service` |
| Sigma Tech | `http://<VM-IP>:5001/` | `sigma-tech.service` |
| Prompt Me Maybe | `http://<VM-IP>:8000/` | `prompt-me-maybe.service` |
| Dolos Lab | `http://<VM-IP>:8100/` | `dolos-lab.service` |
| Sekur Julius | `http://<VM-IP>/challenges/sekur-julius/` | Nginx + `ctf-mini-challenges.service` API |
| Base64 Cascade | `http://<VM-IP>/challenges/base64-cascade/` | Nginx + `ctf-mini-challenges.service` API |
| Sugar Free Candies | `http://<VM-IP>/challenges/sugar-free-candies/` | Nginx + `ctf-mini-challenges.service` API |
| Lots of Passwords | `http://<VM-IP>/challenges/lots-of-passwords/` | Nginx + `ctf-mini-challenges.service` API |
| Redacted RSA | `http://<VM-IP>/challenges/redacted-rsa/` | Nginx + `ctf-mini-challenges.service` API |
| Ghost Binary | `http://<VM-IP>/challenges/ghost-binary/` | Nginx + `ctf-mini-challenges.service` API |
| TFTP: The Last Block | `http://<VM-IP>/challenges/tftp-last-block/` | Nginx capture download + `ctf-mini-challenges.service` API |
| DNS Breadcrumbs | `http://<VM-IP>/challenges/dns-breadcrumbs/` | Nginx + `ctf-mini-challenges.service` API |
| USB Typist | `http://<VM-IP>/challenges/usb-typist/` | Nginx + `ctf-mini-challenges.service` API |
| Mailbox in Transit | `http://<VM-IP>/challenges/mailbox-in-transit/` | Nginx + `ctf-mini-challenges.service` API |
| Logbook at 03:17 | `http://<VM-IP>/challenges/logbook-0317/` | Nginx + `ctf-mini-challenges.service` API |
| Metadata Mosaic | `http://<VM-IP>/challenges/metadata-mosaic/` | Nginx + `ctf-mini-challenges.service` API |
| Git Aftermath | `http://<VM-IP>/challenges/git-aftermath/` | Nginx + `ctf-mini-challenges.service` API |
| File Carver | `http://<VM-IP>/challenges/file-carver/` | Nginx + `ctf-mini-challenges.service` API |
| Browser Cache Reconstruction | `http://<VM-IP>/challenges/browser-cache-reconstruction/` | Nginx + `ctf-mini-challenges.service` API |
| Firmware Footnote | `http://<VM-IP>/challenges/firmware-footnote/` | Nginx + `ctf-mini-challenges.service` API |
| Packet Split | `http://<VM-IP>/challenges/packet-split/` | Nginx + `ctf-mini-challenges.service` API |
| Header Hunt | `http://<VM-IP>/challenges/header-hunt/` | Nginx + `ctf-mini-challenges.service` API |
| Cookie Crumbs | `http://<VM-IP>/challenges/cookie-crumbs/` | Nginx + `ctf-mini-challenges.service` API |
| Mock IDOR Maze | `http://<VM-IP>/challenges/mock-idor-maze/` | Nginx + `ctf-mini-challenges.service` API |
| SQL Query Room | `http://<VM-IP>/challenges/sql-query-room/` | Nginx + `ctf-mini-challenges.service` API |
| Redirect Relay | `http://<VM-IP>/challenges/redirect-relay/` | Nginx + `ctf-mini-challenges.service` API |
| API Contract Trap | `http://<VM-IP>/challenges/api-contract-trap/` | Nginx + `ctf-mini-challenges.service` API |
| Tiny VM | `http://<VM-IP>/challenges/tiny-vm/` | Nginx + `ctf-mini-challenges.service` API |
| ELF Gatekeeper | `http://<VM-IP>/challenges/elf-gatekeeper/` | Nginx + `ctf-mini-challenges.service` API |
| Policy Diff | `http://<VM-IP>/challenges/policy-diff/` | Nginx + `ctf-mini-challenges.service` API |
| Timeline Drift | `http://<VM-IP>/challenges/timeline-drift/` | Nginx + `ctf-mini-challenges.service` API |

The four original challenge processes and the shared mini-challenge backend run as separate unprivileged services and start at boot. The shared backend binds only to `127.0.0.1:8200`; Nginx exposes its API through the normal port 80 site. Puzzle data and solved status are stored per browser cookie. Each self-contained challenge has one fixed correct flag shared by all teams; the TFTP capture is fixed as well. The SQLite state survives reconnects and service restarts, and inactive sessions expire after 48 hours. The service code and Python validators are installed under `/opt/ctf-challenges/self-contained-challenges`; Nginx receives only public challenge pages and artifacts. Browser cookies identify browser sessions; sharing progress across a whole team requires team identity integration with the event platform.

## Install on a fresh Ubuntu VM

Use a fresh Ubuntu Server 24.04 LTS VM. Copy or extract the complete website project into the VM, preserving its top-level `AI-1`, `Sigma-Tech`, `prompt_me_maybe`, `Dolos-Lab`, `challenges`, and `deploy/ubuntu` folders. Then run from the project root:

```sh
sudo bash deploy/ubuntu/install.sh
```

The installer installs Nginx and Python build/runtime packages, creates isolated service accounts and Python virtual environments, installs Python requirements, installs systemd units, and starts all services. It needs outbound internet access during installation to download OS and Python packages. It installs only the runtime server and challenge handlers under `/opt/ctf-challenges/self-contained-challenges`; public web folders contain only `index.html`, `app.js`, `style.css`, and the shared `common.js`. Repository metadata and `.env` files are excluded.

After install, check status and logs:

```sh
systemctl --no-pager --full status ctf-ai sigma-tech prompt-me-maybe dolos-lab ctf-mini-challenges nginx
sudo journalctl -u ctf-ai -u sigma-tech -u prompt-me-maybe -u dolos-lab -u ctf-mini-challenges -n 100 --no-pager
```

From a separate machine, open `http://<VM-IP>/`. The guest firewall and any cloud/hypervisor firewall must allow inbound TCP ports `80`, `5000`, `5001`, `8000`, and `8100`. The 27 self-contained challenge APIs use port 80 through Nginx; port 8200 stays private to the VM. Keep SSH access restricted to the VM administrator. In VirtualBox/VMware, use bridged networking for LAN access, or configure host port forwarding for each required port when using NAT. Do not expose this challenge VM on an untrusted network without isolating it from sensitive hosts and services.

## Shared AI provider configuration

AI-1, Prompt Me Maybe, and Dolos Lab read the same provider settings. On the Ubuntu VM, edit `/etc/ctf-challenges/ai-providers.env`; it is created with restricted permissions for the three challenge service accounts. Add only providers you intend to use, then restart the three services:

```sh
sudoedit /etc/ctf-challenges/ai-providers.env
sudo systemctl restart ctf-ai prompt-me-maybe dolos-lab
```

For local development, copy the project-root `ai-providers.env.example` to `ai-providers.env` and fill in the values there. This private file is ignored by Git. Existing process environment variables take precedence over file values.

AI-1 chat logging to the project's Google Sheets endpoint is disabled by default. Keep `GSHEET_LOGGING_ENABLED=false` for a competition; enabling it sends participant messages and replies to that external endpoint. With provider keys configured, participant messages are sent to the selected provider, so account for consent, provider terms, quotas, and outbound firewall rules.

AI-1, Prompt Me Maybe, and Dolos Lab use the Groq, Gemini, Cloudflare Workers AI, then OpenAI fallback chain. Dolos uses OpenAI for the simulated diagnostic tool call; the other providers can supply conversational replies and fall through on failure. The chat challenges continue with deterministic local guidance when providers are absent or unavailable.

## Prepare and export an OVA

1. Install and configure the VM, then verify the portal and each challenge from a second machine using the URL table.
2. Reboot the guest and verify all six systemd units are active and the same URLs still work.
3. Set the final VM memory/disk/network settings. Remove any temporary source archive, unused provider keys, SSH keys, shell history containing secrets, and personal accounts. Preserve the installed `/opt/ctf-challenges` runtime and the deployment portal.
4. Shut the guest down cleanly (`sudo poweroff`) and export the powered-off VM as an OVA from VirtualBox/VMware.
5. Import the exported OVA on a clean test machine, connect it to the intended isolated lab network, determine its DHCP address, and repeat the URL and reboot checks before distributing it.

The OVA is not built by the Windows installer or by this source tree. This folder supplies Ubuntu deployment configuration and the installer; the OVA export and clean-import verification must be performed by the VM hypervisor. Never distribute an OVA containing live provider credentials.

## Service operations

```sh
sudo systemctl restart ctf-ai sigma-tech prompt-me-maybe dolos-lab ctf-mini-challenges nginx
sudo systemctl stop ctf-ai sigma-tech prompt-me-maybe dolos-lab ctf-mini-challenges nginx
sudo systemctl enable ctf-ai sigma-tech prompt-me-maybe dolos-lab ctf-mini-challenges nginx
```

The self-contained challenge sessions are stored in `/var/lib/ctf-challenges/sessions.sqlite3`, owned by the `ctf-mini-challenges` service account. Restarting that service preserves active browser sessions. The TFTP challenge uses one shared capture and flag across all teams. Sigma Tech's generated model and baseline are included as runtime data. Dolos Lab uses its deterministic simulated mode by default and does not need Rebuff/OpenAI keys.
