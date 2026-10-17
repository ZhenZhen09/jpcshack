# Ubuntu CTF VM deployment

This deploys the four standalone challenges as separate services on one Ubuntu VM. A small Nginx portal on port 80 lists URLs using the VM's current hostname/IP, so DHCP address changes do not require editing the challenge list.

| Challenge | URL | Service |
| --- | --- | --- |
| Portal | `http://<VM-IP>/` | Nginx |
| Ancient Bedrock Guardian (AI-1) | `http://<VM-IP>:5000/` | `ctf-ai.service` |
| Sigma Tech | `http://<VM-IP>:5001/` | `sigma-tech.service` |
| Prompt Me Maybe | `http://<VM-IP>:8000/` | `prompt-me-maybe.service` |
| Dolos Lab | `http://<VM-IP>:8100/` | `dolos-lab.service` |

The challenge processes run as separate unprivileged users and start automatically at boot. They bind their own ports directly, avoiding fragile path-prefix rewrites of their APIs and static assets. The portal requires JavaScript only to substitute the VM hostname into each link; direct port URLs are also listed above.

## Install on a fresh Ubuntu VM

Use a fresh Ubuntu Server 24.04 LTS VM. Copy or extract the complete website project into the VM, preserving its top-level `AI-1`, `Sigma-Tech`, `prompt_me_maybe`, `Dolos-Lab`, and `deploy/ubuntu` folders. Then run from the project root:

```sh
sudo bash deploy/ubuntu/install.sh
```

The installer installs Nginx and Python build/runtime packages, creates isolated service accounts and Python virtual environments, installs Python requirements, installs systemd units, and starts all services. It needs outbound internet access during installation to download OS and Python packages. It copies only runtime files into `/opt/ctf-challenges`; source virtual environments, tests, author solutions, `.env` files, and repository metadata are excluded.

After install, check status and logs:

```sh
systemctl --no-pager --full status ctf-ai sigma-tech prompt-me-maybe dolos-lab nginx
sudo journalctl -u ctf-ai -u sigma-tech -u prompt-me-maybe -u dolos-lab -n 100 --no-pager
```

From a separate machine, open `http://<VM-IP>/`. The guest firewall and any cloud/hypervisor firewall must allow inbound TCP ports `80`, `5000`, `5001`, `8000`, and `8100`. Keep SSH access restricted to the VM administrator. In VirtualBox/VMware, use bridged networking for LAN access, or configure host port forwarding for each required port when using NAT. Do not expose this challenge VM on an untrusted network without isolating it from sensitive hosts and services.

## Optional AI-1 providers

AI-1's puzzle routes run without provider keys, but ordinary conversation will show its offline reply until a provider is configured. Provider keys are not copied from the project. Configure only the keys you intend to pay for in `/etc/ctf-challenges/ai-1.env`, then restart `ctf-ai`:

```sh
sudoedit /etc/ctf-challenges/ai-1.env
sudo systemctl restart ctf-ai
```

AI-1 chat logging to the project's Google Sheets endpoint is disabled by default. Keep `GSHEET_LOGGING_ENABLED=false` for a competition; enabling it sends participant messages and replies to that external endpoint. With provider keys configured, participant messages are sent to the selected provider, so account for consent, provider terms, quotas, and outbound firewall rules.

## Prepare and export an OVA

1. Install and configure the VM, then verify the portal and each challenge from a second machine using the URL table.
2. Reboot the guest and verify all five systemd units are active and the same URLs still work.
3. Set the final VM memory/disk/network settings. Remove any temporary source archive, unused provider keys, SSH keys, shell history containing secrets, and personal accounts. Preserve the installed `/opt/ctf-challenges` runtime and the deployment portal.
4. Shut the guest down cleanly (`sudo poweroff`) and export the powered-off VM as an OVA from VirtualBox/VMware.
5. Import the exported OVA on a clean test machine, connect it to the intended isolated lab network, determine its DHCP address, and repeat the URL and reboot checks before distributing it.

The OVA is not built by the Windows installer or by this source tree. This folder supplies Ubuntu deployment configuration and the installer; the OVA export and clean-import verification must be performed by the VM hypervisor. Never distribute an OVA containing live provider credentials.

## Service operations

```sh
sudo systemctl restart ctf-ai sigma-tech prompt-me-maybe dolos-lab nginx
sudo systemctl stop ctf-ai sigma-tech prompt-me-maybe dolos-lab nginx
sudo systemctl enable ctf-ai sigma-tech prompt-me-maybe dolos-lab nginx
```

All challenge state is in memory and resets when its service restarts. Sigma Tech's generated model and baseline are included as runtime data. Dolos Lab uses its deterministic simulated mode by default and does not need Rebuff/OpenAI keys.
