# 재빌드

## 준비물

빌드 스크립트는 저장소 폴더를 작업 폴더로 쓰고, **그 상위 폴더**에서 원본 디스크와 나눔스퀘어 네오 글꼴을 찾습니다(환경 변수 `LEYNOS2_ROOT`로 바꿀 수 있습니다).

```
<상위 폴더>/
  Assault Suit Leynos 2 (Japan) (Track 01).bin   ← README의 해시와 일치해야 함
  NanumSquareNeo-bRg.ttf  NanumSquareNeo-cBd.ttf
  <이 저장소>/
    fonts/Galmuri11.bdf  fonts/Galmuri11-Condensed.bdf  fonts/Galmuri9.bdf
```

- Python 3.13, `numpy`, `Pillow`
- 글꼴 출처는 `docs/FONT_CREDITS.md`
- xdelta3 (배포 파일을 만들 때만)

## 빌드

저장소 폴더에서 실행합니다.

```powershell
python tools/extract.py "../Assault Suit Leynos 2 (Japan) (Track 01).bin" disc   # 디스크 파일 → disc/, tree.bin 생성
python tools/make.py                                                              # → ../Assault Suit Leynos 2 (Korean) (Track 01).bin
```

`make.py`는 원본 BIN을 읽어 바뀐 파일만 같은 자리에 다시 써서 상위 폴더에 결과 BIN을 만듭니다(출력 경로는 환경 변수 `LEYNOS2_OUT`로 바꿀 수 있습니다). `python tools/make.py demo setspr`처럼 단계 이름을 주면 그 단계만 적용합니다. 결과 BIN의 SHA-256이 `release_manifest.json`의 `output_bin_sha256`과 같아야 합니다. 음악 트랙 02~14는 원본을 그대로 씁니다.

## 배포 파일

```powershell
xdelta3 -e -0 -S none -A -s "Assault Suit Leynos 2 (Japan) (Track 01).bin" "Assault Suit Leynos 2 (Korean) (Track 01).bin" Leynos2_SS_KO_v1.0.xdelta
```

## 번역 수정

1. `tr/` 아래 해당 파일을 고칩니다(`docs/TRANSLATION_GUIDE.md`).
2. `python tools/make.py`를 다시 실행합니다. 칸을 넘는 문구가 있으면 해당 단계에서 `AssertionError`나 `wide`·`too big` 오류로 멈춥니다.
