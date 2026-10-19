#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run this installer with sudo: sudo bash deploy/ubuntu/install.sh" >&2
  exit 1
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"
APP_ROOT=/opt/ctf-challenges

if [[ ! -f "${REPO_ROOT}/AI-1/app.py" || ! -f "${REPO_ROOT}/Dolos-Lab/server.py" ]]; then
  echo "Run this from a complete extracted CTF website project." >&2
  exit 1
fi

if [[ ! -f "${REPO_ROOT}/challenges/server.py" ]]; then
  echo "Missing shared challenge service: challenges/server.py" >&2
  exit 1
fi

for challenge in base64-cascade ghost-binary lots-of-passwords redacted-rsa sekur-julius sugar-free-candies tftp-last-block dns-breadcrumbs usb-typist mailbox-in-transit logbook-0317 metadata-mosaic git-aftermath file-carver browser-cache-reconstruction firmware-footnote packet-split header-hunt cookie-crumbs mock-idor-maze sql-query-room redirect-relay api-contract-trap tiny-vm elf-gatekeeper policy-diff timeline-drift; do
  if [[ ! -f "${REPO_ROOT}/challenges/${challenge}/index.html" ]]; then
    echo "Missing challenge page: challenges/${challenge}/index.html" >&2
    exit 1
  fi
  if [[ ! -f "${REPO_ROOT}/challenges/${challenge}/challenge.py" ]]; then
    echo "Missing server handler: challenges/${challenge}/challenge.py" >&2
    exit 1
  fi
done

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y \
  build-essential nginx python3 python3-dev python3-pip python3-venv

create_service_user() {
  local account="$1"
  if ! getent group "${account}" >/dev/null; then
    groupadd --system "${account}"
  fi
  if ! id "${account}" >/dev/null 2>&1; then
    useradd --system --no-create-home --home-dir /nonexistent \
      --shell /usr/sbin/nologin --gid "${account}" "${account}"
  fi
}

install_tree() {
  local source="$1" destination="$2" account="$3"
  shift 3
  install -d -o root -g "${account}" -m 0750 "${destination}"
  local entry
  for entry in "$@"; do
    cp -a "${source}/${entry}" "${destination}/"
    chown -R root:"${account}" "${destination}/${entry}"
    find "${destination}/${entry}" -type d -exec chmod 0750 {} +
    find "${destination}/${entry}" -type f -exec chmod 0640 {} +
  done
}

setup_venv() {
  local directory="$1"
  python3 -m venv "${directory}/.venv"
  "${directory}/.venv/bin/pip" install --disable-pip-version-check -r "${directory}/requirements.txt"
}

for account in ctf-ai ctf-sigma ctf-pmm ctf-dolos ctf-mini-challenges; do
  create_service_user "${account}"
done

if ! getent group ctf-ai-providers >/dev/null; then
  groupadd --system ctf-ai-providers
fi
for account in ctf-ai ctf-pmm ctf-dolos; do
  usermod -a -G ctf-ai-providers "${account}"
done

install -d -o root -g root -m 0755 "${APP_ROOT}"
install_tree "${REPO_ROOT}/AI-1" "${APP_ROOT}/ai-1" ctf-ai app.py requirements.txt templates static
install_tree "${REPO_ROOT}/Sigma-Tech" "${APP_ROOT}/sigma-tech" ctf-sigma app.py classifier.py requirements.txt templates static data
install_tree "${REPO_ROOT}/prompt_me_maybe" "${APP_ROOT}/prompt-me-maybe" ctf-pmm server.py requirements.txt public
install_tree "${REPO_ROOT}/Dolos-Lab" "${APP_ROOT}/dolos-lab" ctf-dolos server.py challenge.py providers.py public
install_tree "${REPO_ROOT}/challenges" "${APP_ROOT}/self-contained-challenges" ctf-mini-challenges \
  server.py sekur-julius base64-cascade sugar-free-candies lots-of-passwords redacted-rsa ghost-binary tftp-last-block \
  dns-breadcrumbs usb-typist mailbox-in-transit logbook-0317 metadata-mosaic git-aftermath file-carver \
  browser-cache-reconstruction firmware-footnote packet-split header-hunt cookie-crumbs mock-idor-maze \
  sql-query-room redirect-relay api-contract-trap tiny-vm elf-gatekeeper policy-diff timeline-drift

setup_venv "${APP_ROOT}/ai-1"
setup_venv "${APP_ROOT}/sigma-tech"
setup_venv "${APP_ROOT}/prompt-me-maybe"

install -d -o root -g root -m 0755 /etc/ctf-challenges
if [[ ! -e /etc/ctf-challenges/ai-providers.env ]]; then
  install -o root -g ctf-ai-providers -m 0640 /dev/null /etc/ctf-challenges/ai-providers.env
fi

install -o root -g root -m 0644 "${REPO_ROOT}/AI-1/ai-1.service" /etc/systemd/system/ctf-ai.service
install -o root -g root -m 0644 "${REPO_ROOT}/Sigma-Tech/sigma-tech.service" /etc/systemd/system/sigma-tech.service
install -o root -g root -m 0644 "${REPO_ROOT}/prompt_me_maybe/prompt-me-maybe.service" /etc/systemd/system/prompt-me-maybe.service
install -o root -g root -m 0644 "${REPO_ROOT}/Dolos-Lab/dolos-lab.service" /etc/systemd/system/dolos-lab.service
install -o root -g root -m 0644 "${REPO_ROOT}/challenges/ctf-mini-challenges.service" /etc/systemd/system/ctf-mini-challenges.service

install -d -o root -g root -m 0755 /var/www/ctf-portal
install -d -o root -g root -m 0755 /var/www/ctf-portal/challenges
for challenge in base64-cascade ghost-binary lots-of-passwords redacted-rsa sekur-julius sugar-free-candies tftp-last-block dns-breadcrumbs usb-typist mailbox-in-transit logbook-0317 metadata-mosaic git-aftermath file-carver browser-cache-reconstruction firmware-footnote packet-split header-hunt cookie-crumbs mock-idor-maze sql-query-room redirect-relay api-contract-trap tiny-vm elf-gatekeeper policy-diff timeline-drift; do
  install -d -o root -g root -m 0755 "/var/www/ctf-portal/challenges/${challenge}"
  for asset in index.html app.js style.css; do
    install -o root -g root -m 0644 \
      "${REPO_ROOT}/challenges/${challenge}/${asset}" \
      "/var/www/ctf-portal/challenges/${challenge}/${asset}"
  done
  if [[ -f "${REPO_ROOT}/challenges/${challenge}/capture.pcap" ]]; then
    install -o root -g root -m 0644 \
      "${REPO_ROOT}/challenges/${challenge}/capture.pcap" \
      "/var/www/ctf-portal/challenges/${challenge}/capture.pcap"
  fi
done
install -o root -g root -m 0644 "${REPO_ROOT}/challenges/common.js" /var/www/ctf-portal/challenges/common.js
# Remove source files or old solution notes left by an earlier static deployment.
find /var/www/ctf-portal/challenges -type f \( -name '*.py' -o -name 'README.md' \) -delete
chown -R root:root /var/www/ctf-portal/challenges
find /var/www/ctf-portal/challenges -type d -exec chmod 0755 {} +
find /var/www/ctf-portal/challenges -type f -exec chmod 0644 {} +
install -o root -g root -m 0644 "${SCRIPT_DIR}/index.html" /var/www/ctf-portal/index.html
install -o root -g root -m 0644 "${SCRIPT_DIR}/portal.css" /var/www/ctf-portal/portal.css
install -o root -g root -m 0644 "${SCRIPT_DIR}/portal.js" /var/www/ctf-portal/portal.js
install -o root -g root -m 0644 "${SCRIPT_DIR}/ctf-portal.nginx" /etc/nginx/sites-available/ctf-portal
ln -sfn /etc/nginx/sites-available/ctf-portal /etc/nginx/sites-enabled/ctf-portal
if [[ -L /etc/nginx/sites-enabled/default ]]; then
  rm /etc/nginx/sites-enabled/default
fi

systemd-analyze verify \
  /etc/systemd/system/ctf-ai.service \
  /etc/systemd/system/sigma-tech.service \
  /etc/systemd/system/prompt-me-maybe.service \
  /etc/systemd/system/dolos-lab.service \
  /etc/systemd/system/ctf-mini-challenges.service
nginx -t
systemctl daemon-reload
systemctl enable --now ctf-ai sigma-tech prompt-me-maybe dolos-lab ctf-mini-challenges nginx

echo
echo "CTF challenge services are enabled and running."
echo "Open http://<VM-IP>/ for the challenge URL list."
echo "The 27 self-contained web challenges use the shared backend through port 80; its service listens privately on 127.0.0.1:8200."
echo "Allow inbound TCP ports 80, 5000, 5001, 8000, and 8100 in the VM firewall/network."
