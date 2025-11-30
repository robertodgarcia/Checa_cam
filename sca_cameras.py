import os
import time
import requests

BASE_URL = "http://168.194.65.172:8602/Interface/Cameras/GetSnapshot"

# Pega usuário e senha de variáveis de ambiente (virão dos secrets do GitHub)
AUTH_USER = os.getenv("CAMERA_USER")
AUTH_PASS = os.getenv("CAMERA_PASS")

# Faixa de IDs para testar – ajuste conforme sua realidade
START_ID = int(os.getenv("CAMERA_ID_START", "1000"))
END_ID = int(os.getenv("CAMERA_ID_END", "1100"))  # inclusive

# Opcional: lista extra de nomes de câmera
EXTRA_CAMERAS = os.getenv("EXTRA_CAMERAS", "").split(",") if os.getenv("EXTRA_CAMERAS") else []

TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "3"))  # segundos
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
        print(f"[ERRO] Camera={camera_value} -> {e}")
        return False

    # Considera 200 como resposta válida. Você pode refinar pelo conteúdo se quiser.
    if resp.status_code == 200 and resp.content:
        # Para evitar vazar dados, não imprime o conteúdo, só status.
        print(f"[OK] Camera={camera_value} -> status={resp.status_code} ({len(resp.content)} bytes)")
        return True
    else:
        print(f"[FAIL] Camera={camera_value} -> status={resp.status_code}")
        return False


def main():
    if not AUTH_USER or not AUTH_PASS:
        print("ERRO: variáveis de ambiente CAMERA_USER e CAMERA_PASS não definidas.")
        raise SystemExit(1)

    found = []

    print(f"Iniciando varredura de câmeras em {BASE_URL}")
    print(f"Faixa numérica: {START_ID} a {END_ID}")
    if EXTRA_CAMERAS:
        print(f"Câmeras extras: {EXTRA_CAMERAS}")

    # 1) Testa IDs numéricos
    for cam_id in range(START_ID, END_ID + 1):
        cam_str = str(cam_id)
        if check_camera(cam_str):
            found.append(cam_str)
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
