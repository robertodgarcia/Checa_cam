import os
import time
import requests

BASE_URL = "http://168.194.65.172:8602/Interface/Cameras/GetSnapshot"

# Usuário e senha vêm dos secrets do GitHub
AUTH_USER = os.getenv("CAMERA_USER")
AUTH_PASS = os.getenv("CAMERA_PASS")

# Prefixo fixo da câmera (pode mudar via variável de ambiente, se quiser)
CAMERA_PREFIX = os.getenv("CAMERA_PREFIX", "1070 - MALIBU HOME - ")

# Faixa do sufixo numérico (00 até 1000, por padrão)
SUFFIX_START = int(os.getenv("CAMERA_SUFFIX_START", "0"))
SUFFIX_END = int(os.getenv("CAMERA_SUFFIX_END", "1000"))  # inclusive

# Opcional: lista extra de nomes de câmera, separados por vírgula
EXTRA_CAMERAS = os.getenv("EXTRA_CAMERAS", "").split(",") if os.getenv("EXTRA_CAMERAS") else []

TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "3"))      # segundos
SLEEP_BETWEEN = float(os.getenv("REQUEST_SLEEP", "0.2"))  # pausa entre requisições


def check_camera(camera_value: str) -> bool:
    """Retorna True se a câmera existe / responde OK."""
    params = {
        "Camera": camera_value,
        "Width": "1280",
        "Height": "720",
        "Quality": "100",
        "ResponseFormat": "jsonL",
        "AuthUser": AUTH_USER,
        "AuthPass": AUTH_PASS,
    }

    try:
        resp = requests.get(BASE_URL, params=params, timeout=TIMEOUT)
    except requests.RequestException as e:
        print(f"[ERRO] Camera='{camera_value}' -> {e}")
        return False

    if resp.status_code == 200 and resp.content:
        print(f"[OK] Camera='{camera_value}' -> status={resp.status_code} ({len(resp.content)} bytes)")
        return True
    else:
        print(f"[FAIL] Camera='{camera_value}' -> status={resp.status_code}")
        return False


def main():
    if not AUTH_USER or not AUTH_PASS:
        print("ERRO: variáveis de ambiente CAMERA_USER e CAMERA_PASS não definidas.")
        raise SystemExit(1)

    found = []

    print(f"Iniciando varredura em {BASE_URL}")
    print(f"Prefixo fixo: '{CAMERA_PREFIX}'")
    print(f"Sufixos: {SUFFIX_START} até {SUFFIX_END}")
    if EXTRA_CAMERAS:
        print(f"Câmeras extras: {EXTRA_CAMERAS}")

    # 1) Testa prefixo fixo + sufixos numéricos
    for i in range(SUFFIX_START, SUFFIX_END + 1):
        # 0–99 fica 00, 01, 02... 99; 100 vira 100; 1000 vira 1000
        suffix = f"{i:02d}"
        cam_name = f"{CAMERA_PREFIX}{suffix}"
        if check_camera(cam_name):
            found.append(cam_name)
        time.sleep(SLEEP_BETWEEN)

    # 2) Testa nomes adicionais, se houver
    for cam_name in EXTRA_CAMERAS:
        cam_name = cam_name.strip()
        if not cam_name:
            continue
        if check_camera(cam_name):
            found.append(cam_name)
        time.sleep(SLEEP_BETWEEN)

    print("\n===== RESUMO =====")
    if found:
        print("Câmeras encontradas/responsivas:")
        for c in found:
            print(f" - {c}")
    else:
        print("Nenhuma câmera adicional encontrada na faixa configurada.")


if __name__ == "__main__":
    main()
