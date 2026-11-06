# 중장기병 레이노스2 세가 새턴 한글패치

세가 새턴 일본판 **重装機兵レイノス2 (T-2501G)**용 비공식 한국어 패치입니다. **미션 대사 785줄 전체**를 한국어로 바꿨습니다. 그림으로 들어 있는 **스토리 화면, 미션 목표, 일시정지 도움말, 오프닝 연표, 디스크 선택·저장 메시지, 출격 전 세팅 화면 안내, 엔딩 뉴스와 엔딩곡 크레디트**도 한글로 다시 그렸습니다. 현재 배포판은 **v1.0 (2026-11-06)**입니다.

[패치 다운로드](https://github.com/snake759494/leynos2-saturn-korean-patch/releases/latest) · [기술 설명](docs/TECHNICAL.md) · [재빌드](docs/BUILD.md) · [변경 기록](CHANGELOG.md) · [권리 안내](RIGHTS.md)

릴리즈 첨부 파일은 한글패치 **Leynos2_SS_KO_v1.0.xdelta**뿐입니다. 저장소에는 제작 소스와 한국어 번역만 공개합니다. 원본·완성 디스크 이미지, 추출한 게임 파일, 일본어 원문, 글꼴 파일, 외부 실행 파일은 포함하지 않습니다. GitHub가 자동으로 만드는 Source code ZIP/TAR는 저장소 소스를 압축한 것이며 게임 파일이 아닙니다.

## 게임 소개 및 대상 버전

『중장기병 레이노스2』는 일본 컴퓨터 시스템(메사이어)이 1997년에 세가 새턴으로 낸 횡스크롤 로봇 액션 게임으로, 메가 드라이브 『중장기병 레이노스』의 속편입니다. 제네스 연방 특수부대 S.A.S.의 강습 장갑병 파일럿이 되어, 출격 전에 기체와 무기를 세팅하고 미션마다 무전 대사가 오가는 전장을 돌파합니다.

이 패치는 **세가 새턴 일본판 T-2501G V1.003의 BIN/CUE 이미지(트랙 14개: 데이터 MODE1/2352 + 음악 13트랙)**의 **트랙 01**에만 적용합니다. 음악 트랙 02~14는 바뀌지 않으므로 원본을 그대로 씁니다. 파일 이름보다 아래 표의 크기와 해시가 일치하는지가 중요합니다.

## 적용할 원본

| 항목 | 값 |
| --- | --- |
| 게임 ID | T-2501G V1.003 |
| 원본 형식 | 수정되지 않은 일본판 BIN/CUE (트랙 14개) |
| 원본 트랙 01 BIN 크기 | 109,462,080 바이트 |
| **원본 트랙 01 BIN MD5** | `6e2806a357258761c6ddbfbab0028dad` |
| 원본 트랙 01 BIN SHA-1 | `8fea17dcf623be8839accebadfe321f277eac08f` |
| 원본 트랙 01 BIN SHA-256 | `92b803ccbf509a913cb5de074b27cd1fb9cc380cfeb4650abc553d8f1203097e` |
| 음악 트랙 02~14 | 변경 없음(MD5는 `release_manifest.json`) |
| xdelta 파일 크기 | 1,018,107 바이트 |
| xdelta SHA-256 | `ac443e62b9b6b30e0c0fbb91df4983bb80eea67101c177249d298e7f59d4c8af` |
| 적용 결과 트랙 01 BIN 크기 | 109,462,080 바이트 (원본과 같음) |
| 적용 결과 트랙 01 BIN SHA-1 | `665d8535f194ec7384c19506d8e2549af688cbca` |
| 적용 결과 트랙 01 BIN SHA-256 | `e5222886edea308e80dc806c4b1718a62561a35c4fed75cad2d9134384987f31` |

원본 게임 파일은 사용자가 직접 준비해야 합니다.

## 패치 적용 방법

### Windows에서 원본 확인

```powershell
Get-FileHash -Algorithm MD5 -LiteralPath '.\Assault Suit Leynos 2 (Japan) (Track 01).bin'
```

위 표와 다르면 적용을 중단하세요. CHD, ECM, 압축 이미지에는 적용할 수 없습니다.

### xdelta UI 사용

1. 릴리즈에서 `Leynos2_SS_KO_v1.0.xdelta`를 받습니다.
2. xdelta3 패치를 지원하는 도구에서 **Apply Patch** 기능을 엽니다.
3. **Patch**에는 xdelta 파일을, **Source File**에는 해시가 일치하는 원본 **트랙 01** `.bin`을 선택합니다.
4. **Output File**에는 새 파일 이름을 지정합니다(예: `Assault Suit Leynos 2 (Korean) (Track 01).bin`).
5. 원본 `.cue`를 복사해 `Assault Suit Leynos 2 (Korean).cue`로 이름을 바꾸고, **첫 번째** `FILE "..."` 줄만 결과 파일 이름으로 고칩니다. 트랙 02~14 줄은 원본 음악 파일을 그대로 가리키게 두고, 결과 파일을 원본과 같은 폴더에 둡니다.

```
FILE "Assault Suit Leynos 2 (Korean) (Track 01).bin" BINARY
  TRACK 01 MODE1/2352
    INDEX 01 00:00:00
FILE "Assault Suit Leynos 2 (Japan) (Track 02).bin" BINARY
  TRACK 02 AUDIO
  ... (트랙 14까지 원본 그대로)
```

xdelta는 호환성을 위해 압축·2차 압축·파일 경로 헤더 없이 만들었습니다. xdelta 자체는 [공식 프로젝트](https://github.com/jmacd/xdelta)를 참고하세요.

### 명령줄 사용

```powershell
.\xdelta3.exe -d -s '.\Assault Suit Leynos 2 (Japan) (Track 01).bin' '.\Leynos2_SS_KO_v1.0.xdelta' '.\Assault Suit Leynos 2 (Korean) (Track 01).bin'
```

해시를 자동으로 검사하고 CUE까지 만들어 주는 도구도 있습니다(CUE는 원본 음악 트랙을 그대로 가리킵니다). Python 3과 xdelta3가 필요하며, 같은 이름의 출력 파일이 이미 있으면 덮어쓰지 않습니다.

```powershell
python tools/apply_release.py --xdelta '.\xdelta3.exe' --source '.\Assault Suit Leynos 2 (Japan) (Track 01).bin' --patch '.\Leynos2_SS_KO_v1.0.xdelta' --output '.\Assault Suit Leynos 2 (Korean) (Track 01).bin'
```

### 실행

에뮬레이터에서 결과 `.cue`를 여세요. 원본판의 세이브 스테이트는 불러오지 마세요(대사 데이터가 다릅니다). 내장 메모리·카트리지 세이브는 원본판과 같은 형식입니다.

## 작업 내용과 범위

| 구분 | 작업량 및 내용 |
| --- | --- |
| 미션 대사 | 20개 미션 팩의 무전 대사 785줄(갈무리11) |
| 스토리 화면 | 미션 사이 스토리 화면 7장, 95줄(나눔스퀘어 네오) |
| 미션 목표 | 미션 목표 화면 7줄 |
| 일시정지 도움말 | 압축된 화면 맵 18개와 글자 타일을 함께 다시 만듦 |
| 오프닝 연표 | A.D.2120~2124 연표 14줄 |
| 디스크·저장 | 「시작할 디스크를 선택하십시오」, 「데이터를 삭제합니다」, 저장·백업 메시지 28줄 |
| 세팅 화면 | 「사용할 기체를 선택해 주십시오」, 기동력·무기용 파워 설명, 장비 선택 안내 등 메시지 17종 |
| 엔딩 | 엔딩 뉴스 기사 16줄, 엔딩곡 제목과 작사·작곡·편곡·노래 표기 |

### 번역 원칙

- 기계 번역 없이 문맥을 보고 직접 번역했습니다(`docs/TRANSLATION_GUIDE.md`).
- 대사 줄은 원본 그림 폭(168픽셀)을 넘지 않게 다듬었고, 도움말과 세팅 메시지는 원래 자리에 맞게 일부 문장을 줄였습니다.
- 이름은 일본어 발음을 따라 조지·에디·카일·마리아, 제네스 연방·선랄·콜로니 등으로 적었습니다.

### 번역하지 않은 것

- 엔딩곡 가사(`END2.BG`): 노래 가사는 저작권 보호 대상이라 원본 그대로 두었습니다.
- 오프닝 등 동영상(`MOVIES/*.CPK`) 속 글자
- 결과·스태프·타이틀 화면 등의 영어 표기, 제작사 로고·저작권 표기

## 알려진 한계

- 부팅, 디스크 선택, 미션 대사, 스토리, 미션 목표, 일시정지 도움말은 에뮬레이터로 확인했습니다. **오프닝 연표, 출격 전 세팅 화면, 저장 메시지, 엔딩**은 미션을 진행해야 나오는 화면이라 그려 넣은 결과를 파일로만 확인했습니다.
- 모든 미션을 끝까지 플레이해 보지는 않았습니다. 빌드는 모든 문구가 칸에 들어가는지 검사합니다.
- 실기에서의 동작은 확인하지 못했습니다. 칸을 넘치거나 어긋난 문구가 있으면 이슈로 알려 주세요.

## 저장소 구성

| 경로 | 내용 |
| --- | --- |
| `tools/make.py`·`build.py` | 전체 빌드(단계: dialog, story, mission, help, backup, bkspr, setting, ending, demo, end1, setspr) |
| `tools/` | 빌드·분석 도구(Python). `cdimg.py` 디스크 이미지 직접 수정, `extract.py` 디스크 파일 추출, `lz.py` 허프만 LZ 압축, `dlg.py`·`render.py` 미션 대사, `story.py`·`storyk.py` 스토리 화면, `helpk.py`·`help.py` 일시정지 도움말, `bgk.py`·`bgtext.py`·`bgr.py` 배경 그림 글자, `bdf.py` 갈무리 BDF, `sjscan.py`·`sprv.py`·`v1sprites.py` 조사 도구, `apply_release.py` 해시 검사 후 적용, `emu.py`·`gverify.cpp` 에뮬레이터 테스트 조작 도구 |
| `tr/` | 한국어 번역(원문 없음) |
| `sheets/order.json` | 미션 대사 줄 그림 해시와 번역 줄 순서(원문 없음) |
| `fonts/` | (저장소에 없음) 갈무리 BDF를 두는 곳 |
| `docs/` | 기술 설명, 재빌드 방법, 글꼴 출처, 번역 지침 |

권리 관련 내용은 [RIGHTS.md](RIGHTS.md)를 참고하세요.
