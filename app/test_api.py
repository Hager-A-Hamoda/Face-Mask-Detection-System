"""
test_api.py – Face Mask Detection API tests
Usage: python test_api.py [--url http://localhost:8000] [--image path/to/face.jpg]
"""

import argparse
import io
import sys
import requests
from PIL import Image

BASE_URL = "http://localhost:8000"
PASSED, FAILED = 0, 0


def test(name, fn):
    global PASSED, FAILED
    try:
        fn()
        print(f"  PASS  {name}")
        PASSED += 1
    except Exception as e:
        print(f"  FAIL  {name}  →  {e}")
        FAILED += 1


def predict(img: Image.Image) -> dict:
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    r = requests.post(f"{BASE_URL}/predict", files={"file": ("test.jpg", buf, "image/jpeg")}, timeout=15)
    r.raise_for_status()
    return r.json()


def blank(w=224, h=224) -> Image.Image:
    return Image.new("RGB", (w, h), color=(180, 140, 110))


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_health():
    r = requests.get(f"{BASE_URL}/health", timeout=10)
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["model_loaded"] is True

def test_required_fields():
    data = predict(blank())
    for field in ("class", "status", "confidence", "action", "all_probabilities"):
        assert field in data, f"missing: {field}"

def test_valid_class():
    assert predict(blank())["class"] in ("WithMask", "WithoutMask")

def test_confidence_range():
    c = predict(blank())["confidence"]
    assert 0.0 <= c <= 1.0

def test_probabilities_sum():
    total = sum(predict(blank())["all_probabilities"].values())
    assert abs(total - 1.0) < 0.01, f"probs sum to {total}"

def test_status_action_consistent():
    data = predict(blank())
    expected = {"mask_on": "Allow entry", "mask_off": "Deny entry"}
    assert data["action"] == expected[data["status"]]

def test_small_image():
    assert predict(blank(32, 32))["class"] in ("WithMask", "WithoutMask")

def test_large_image():
    assert predict(blank(1920, 1080))["class"] in ("WithMask", "WithoutMask")

def test_no_file_returns_422():
    assert requests.post(f"{BASE_URL}/predict", timeout=10).status_code == 422

def test_bad_type_returns_415():
    r = requests.post(f"{BASE_URL}/predict",
                      files={"file": ("x.txt", b"not an image", "text/plain")},
                      timeout=10)
    assert r.status_code == 415

def test_real_image(path: str):
    data = predict(Image.open(path).convert("RGB"))
    assert data["class"] in ("WithMask", "WithoutMask")
    print(f"         → {data['class']} ({data['confidence']:.1%})  {data['action']}")


# ── Runner ────────────────────────────────────────────────────────────────────

def main():
    global BASE_URL
    parser = argparse.ArgumentParser()
    parser.add_argument("--url",   default=BASE_URL)
    parser.add_argument("--image", default=None, help="Optional real image to test")
    args = parser.parse_args()
    BASE_URL = args.url.rstrip("/")

    print(f"\nFace Mask Detection — API Tests  ({BASE_URL})\n")

    test("GET  /health",                 test_health)
    test("POST /predict – fields",       test_required_fields)
    test("POST /predict – valid class",  test_valid_class)
    test("POST /predict – confidence",   test_confidence_range)
    test("POST /predict – probs sum",    test_probabilities_sum)
    test("POST /predict – consistency",  test_status_action_consistent)
    test("POST /predict – small image",  test_small_image)
    test("POST /predict – large image",  test_large_image)
    test("POST /predict – no file 422",  test_no_file_returns_422)
    test("POST /predict – bad type 415", test_bad_type_returns_415)

    if args.image:
        test(f"POST /predict – {args.image}", lambda: test_real_image(args.image))

    total = PASSED + FAILED
    print(f"\n{PASSED}/{total} passed", "✅" if FAILED == 0 else "❌")
    if FAILED:
        sys.exit(1)


if __name__ == "__main__":
    main()
