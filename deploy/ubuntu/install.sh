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

for account in ctf-ai ctf-sigma ctf-pmm ctf-dolos; do
  create_service_user "${account}"
done

install -d -o root -g root -m 0755 "${APP_ROOT}"
install_tree "${REPO_ROOT}/AI-1" "${APP_ROOT}/ai-1" ctf-ai app.py requirements.txt templates static
install_tree "${REPO_ROOT}/Sigma-Tech" "${APP_ROOT}/sigma-tech" ctf-sigma app.py classifier.py requirements.txt templates static data
install_tree "${REPO_ROOT}/prompt_me_maybe" "${APP_ROOT}/prompt-me-maybe" ctf-pmm server.py requirements.txt public
install_tree "${REPO_ROOT}/Dolos-Lab" "${APP_ROOT}/dolos-lab" ctf-dolos server.py challenge.py providers.py public

setup_venv "${APP_ROOT}/ai-1"
setup_venv "${APP_ROOT}/sigma-tech"
setup_venv "${APP_ROOT}/prompt-me-maybe"

install -d -o root -g root -m 0755 /etc/ctf-challenges
if [[ ! -e /etc/ctf-challenges/ai-1.env ]]; then
  install -o root -g ctf-ai -m 0640 /dev/null /etc/ctf-challenges/ai-1.env
fi
if [[ ! -e /etc/ctf-challenges/prompt-me-maybe.env ]]; then
  install -o root -g ctf-pmm -m 0640 /dev/null /etc/ctf-challenges/prompt-me-maybe.env
fi

install -o root -g root -m 0644 "${REPO_ROOT}/AI-1/ai-1.service" /etc/systemd/system/ctf-ai.service
install -o root -g root -m 0644 "${REPO_ROOT}/Sigma-Tech/sigma-tech.service" /etc/systemd/system/sigma-tech.service
install -o root -g root -m 0644 "${REPO_ROOT}/prompt_me_maybe/prompt-me-maybe.service" /etc/systemd/system/prompt-me-maybe.service
install -o root -g root -m 0644 "${REPO_ROOT}/Dolos-Lab/dolos-lab.service" /etc/systemd/system/dolos-lab.service

install -d -o root -g root -m 0755 /var/www/ctf-portal
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
  /etc/systemd/system/dolos-lab.service
nginx -t
systemctl daemon-reload
systemctl enable --now ctf-ai sigma-tech prompt-me-maybe dolos-lab nginx

echo
echo "CTF challenge services are enabled and running."
echo "Open http://<VM-IP>/ for the challenge URL list."
echo "Allow inbound TCP ports 80, 5000, 5001, 8000, and 8100 in the VM firewall/network."
