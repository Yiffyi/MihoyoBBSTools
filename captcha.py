import httpx
import time
import os

INFERENCE_URL = os.environ.get('CAPTCHA_INFERENCE_URL')
STOP_URL = os.environ.get('CAPTCHA_SERVER_STOP_URL')
TEST_URL = os.environ.get('CAPTCHA_SERVER_TEST_URL')

GITHUB_TOKEN = os.environ.get('CAPTCHA_GITHUB_TOKEN')
REPO = os.environ.get('CAPTCHA_GITHUB_REPO')
BRANCH = os.environ.get('CAPTCHA_GITHUB_BRANCH')

# get it at https://api.github.com/repos/{REPO}/actions/workflows
WORKFLOW_ID = os.environ.get('CAPTCHA_GITHUB_WORKFLOW_ID')


def stop_inference_server():
    try:
        httpx.get(STOP_URL, timeout=5)
    except Exception:
        pass
    return


def bring_up_inference_server():
    resp = httpx.get(f'https://api.github.com/repos/{REPO}/actions/workflows/{WORKFLOW_ID}/runs')

    if resp.status_code == 200:
        data = resp.json()
    else:
        print(resp.status_code, resp.text)
        print(f"[CAPTCHA] could not access GitHub workflow {WORKFLOW_ID} for {REPO}")
        return

    if data['workflow_runs'][0]['status'] != "in_progress":
        # Bring it up
        header = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {GITHUB_TOKEN}',
            'X-GitHub-Api-Version': '2022-11-28'
        }

        resp = httpx.post(f'https://api.github.com/repos/{REPO}/actions/workflows/{WORKFLOW_ID}/dispatches',
                          headers=header,
                          json={'ref': BRANCH})

        if resp.status_code == 204:
            print("Inference server should start now")
        else:
            print(resp.status_code, resp.text)
            print("Inference server could not be started")
    else:
        print("Inference server is already running")

    for retry in range(20):
        time.sleep(6)
        print(f"Ping inference server at {retry * 6}s")
        try:
            resp = httpx.get(TEST_URL, timeout=1)
            if resp.text == "OK":
                print("[CAPTCHA] Success: inference server is online")
                return
        except Exception:
            pass

    print("[CAPTCHA] Fail: inference server is not started")
    return


def game_captcha(gt: str, challenge: str):
    print(f"gt: {gt}, challenge: {challenge}")
    try:
        resp = httpx.get(INFERENCE_URL, params={'gt': gt, 'challenge': challenge}, timeout=10)
        data = resp.json()['data']
        if data['result'] == 'success':
            return data['validate']
    except:
        pass
    return None

def bbs_captcha(gt: str, challenge: str):
    return game_captcha(gt, challenge)