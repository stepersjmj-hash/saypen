# saypen — 세이펜 PIN 음원 추출기

세이펜 북 파일(.pin)에서 MP3 음원을 잘라내 미리 듣고, 이름을 바꿔 ZIP으로 저장하는
단일 HTML 웹앱. 빌드·서버·외부 라이브러리 없음. 모든 처리는 브라우저 안에서만.

## 구성
- `index.html` — 화면·스타일·스크립트 전부 (IIFE 하나 + `<head>` 의 테마 초기화 스크립트)
- `README.md` — 사용자용 안내
- `manifest.webmanifest` + `icons/icon-180·192·512.png` — 홈 화면·앱 바로가기 아이콘
  (아이폰 "홈 화면에 추가"·네이버 앱 바로가기는 favicon 이 아니라 `apple-touch-icon`·매니페스트 아이콘을 찾고,
  없으면 첫 글자 아이콘으로 대신함). 탭 favicon 은 `<head>` 의 SVG data URI 그대로.
  - 아이콘은 favicon 과 같은 모양(파란 배경 + 막대 3개, 3번째 초록)을 모서리까지 꽉 채운 정사각형 —
    둥근 모서리는 기기가 깎음. 내용이 가운데 80% 안에 있어 maskable 로도 씀
  - 로고를 바꾸면 `tools/mkicon.py` 로 다시 생성: `python tools/mkicon.py icons` (Pillow 필요)
  - `<head>` 의 `og:image` 는 Pages 절대 주소 — 카카오톡 등 링크 미리보기용

## 화면 구조
- `body.loaded` 유무로 두 상태를 전환. 없으면 `#intro`(드롭 영역·진행바·설명), 있으면 `.app`(워크벤치) + `#pbar`
- `.top` 상단바: `.brand`(로고: `.logo` 안 `<i>` 3개 = 막대, 3번째는 초록) · `.chip`(파일명·용량) · `#theme` · `#reset` · `#dl`
  - `.chip`·`#reset`·`#dl` 은 `body:not(.loaded)` 에서 숨김
- `aside`: `.filter[data-v]`(all/unnamed/named/deleted) + 개수(`#cAll` `#cUn` `#cNamed` `#cDel`) · 길이로 선택(`#durMax` `#durSel` `#durHint`) · 파일 정보(`#iDur` `#iSize` `#iTable` `#iMode`) · `.keys`
- `.main`: `.toolbar`(`#play` `#undo` `#selall` `#status2` `#selbar`) · `.thead` · `#list` · `#nores`
- `#pbar` 하단 플레이어: `#prev` `#pp` `#next` · `#nowtxt` `#nowren` `#nowsub` · `#track`/`#fill` · `#tcur` `#tdur` · `#nowclose`.
  `<audio id="player">` 는 숨김 — 컨트롤은 전부 직접 그림
- 그리드 열은 `.cols`(40px 70px 1fr 80px 80px 40px) — `.thead` 와 `.item` 이 공유
- 아이콘(재생·이전·다음·체크)은 CSS 도형. ⏮⏭ 같은 기호 문자는 기기에 따라 이모지로 그려져 흐려지므로 쓰지 않는다

## 테마
- CSS 변수: `:root` = 라이트, `[data-theme=dark]` = 다크. 색은 반드시 변수로 (`--bg --card --ink --muted --accent --accentText --accent2 --line --line2 --ok --okbg --warn --danger --dangerLine --dangerBg --check --player --track --pmuted`)
- `--accent` 는 버튼 배경용(두 테마 동일 #2f6fed), 글자색은 `--accentText`(다크에서 #7da2ff 로 밝힘)
- `<head>` 스크립트가 `localStorage['saypen-theme']` → 없으면 `prefers-color-scheme` 로 `html[data-theme]` 설정 (깜빡임 방지).
  `#theme` 클릭 시 저장. 저장값이 없을 때만 시스템 설정 변경을 따라감
- 로고·플레이어 바는 두 테마 모두 고정색

## 동작 구조 (index.html 스크립트)
- `handle(file)` — .pin 을 읽어 ID3 헤더(`"ID3"`+버전2~4) 위치를 찾음. 512바이트 정렬된
  헤더가 있으면 그것만 쓰고, 없으면 전체 매치를 씀. 각 구간 끝의 0 패딩 제거 → `segs[]`.
  시작 시 `reset(false)` 로 `.loaded` 를 떼고 끝나면 붙인다. `document` 의 drop 도 `handle` 로 연결(작업 중 파일 교체)
- `mp3Duration(u8)` — ID3v2 를 건너뛰고 MPEG 프레임 헤더를 끝까지 세어 재생 시간 계산 → `durs[]`.
  MPEG2(22.05kHz 등) Layer III 는 프레임당 576샘플 — 세계지도 파일에 섞여 있음. 실제 584개를 ffmpeg 디코딩과
  비교해 오차 1프레임(0.026초) 이내 확인. ffprobe 의 format duration 은 비트레이트 추정이라 비교 기준으로 쓰면 안 됨
- `names[]` — 각 음원의 파일명(확장자 제외). 기본값 `0001` 형식. `isNamed(i)` = 기본값과 다른지.
  `.num` 더블클릭·F2 → `startRename(i, sp)` 인라인 입력 (Enter/포커스 이탈 = 저장, Esc = 취소, 빈칸 = 번호로 복귀).
  `sp` = 입력창과 바꿔 끼울 요소 — 기본은 목록 `.num`, 플레이어에선 `#nowtxt`(더블클릭·`#nowren` ✎).
  열린 입력창은 `.edit` 에 `_finish` 가 붙어 있어 ZIP 저장·삭제·닫기 때 `document.querySelectorAll('.edit')` 로 확정/취소.
  저장 후 `updateInfo()` 로 필터 개수 갱신
- `view` + `visible(i)` + `applyView()` — 보기 필터. 행은 지우지 않고 `style.display` 만 바꾼다
  (`list.children[i]` ↔ 인덱스 대응 유지). `setView(v)` 는 선택을 비운다.
  `deleted` 보기 = 삭제 항목만, 나머지 보기 = 삭제 안 된 것 중 조건에 맞는 것
- `deleted[]`·`delStack` — × 로 삭제하면 `deleted[i]=true` + `paintDel(i)`(`.deleted` 클래스, 버튼 × ↔ ↺).
  `alive()` 가 남은 인덱스, ZIP·`updateInfo`·`play()`(삭제 항목 건너뜀)가 이를 따른다. 재생 중인 항목을 지우면 재생 정지.
  `delStack` 의 한 칸 = 한 번에 지운 인덱스 배열 → 되돌리기도 묶음 단위. 단일 × 도 `removeItems([i])`.
  `restoreOne(i)`(↺) 는 해당 인덱스를 모든 묶음에서 빼고 빈 묶음은 제거
- `sel`(Set)·`anchor` — `onItemClick`: 클릭 = 재생+선택 해제+기준점, Shift+클릭 = 기준점~여기 범위(삭제·안 보이는 항목 제외),
  Ctrl/⌘+클릭·`.ck` 클릭 = 토글. 삭제 항목 클릭은 `play(i,1,true)`(강제 재생, 미리 듣기만).
  Delete 키 = 선택 삭제, Esc = 해제 (입력창 포커스 중엔 무시). `.item` 은 user-select:none.
  전체 선택(`#selall`·`#ckall`·Ctrl/⌘+A) = 지금 보기에서 보이는 항목만. `#selbar` 가 보이면 `#status2` 는 숨김
- 길이로 선택 — `selectByDur()`: `parseDur`(`10`·`10초` = 초, `1:30` = 분:초)로 읽어, 지금 보기에 보이는 남은 항목 중
  `Math.round(durs[i]) <= v` 인 것으로 선택을 **바꿈**(추가 아님). 표에 보이는 값(반올림)과 같게 비교 — 0:10 으로 보이면 10 이하에 포함.
  선택되면 입력창 blur — 포커스가 입력창에 남으면 전역 keydown 이 INPUT 을 무시해 Delete 가 안 먹음. 삭제됨 보기에선 막음
- 재생 — `play(i, dir=1, force=false)`: `nextAlive(i,dir)` 로 삭제 항목을 건너뜀. `cont` = 연속 재생 상태
  (`#play` 로 켜고 `#nowclose` 로 끔, 일시정지로는 꺼지지 않음). `ended` → `cont` 면 다음 음원.
  `#prev` 는 2초 넘게 재생했으면 처음으로, 아니면 이전 음원. `#track` 클릭 = 탐색.
  `player.duration` 이 없으면 `durs[cur]` 사용. `revealRow(i)` 가 `#list` 스크롤을 직접 계산(scrollIntoView 안 씀)
- Space = `togglePlay()` — 버튼에 포커스가 있어도 기본 동작을 막고 재생/정지 (안 막으면 방금 누른 "연속 재생"·×·되돌리기가 다시 눌림).
  F2 = 재생 중 음원 또는 기준점 이름 바꾸기 — 그 행이 지금 보기에서 숨어 있으면 플레이어(`#nowtxt`)에서 바꿈
- `cleanName` — `\ / : * ? " < > |`·제어문자 제거, 끝 `.mp3`·점·공백 제거
- `zipNames()` — ZIP 안 이름 중복 시 ` (2)` 붙임 (대소문자 무시)
- `buildZip` — 무압축(STORE) ZIP 직접 생성, UTF-8 파일명 플래그(0x0800)
- `applyView()` 는 보기에서 빠진 항목을 `sel` 에서도 뺀다 (이름 없음 보기에서 이름을 붙여 숨은 행이 Delete 로 지워지는 것 방지)
- `closePlayer(save)` — 재생 중 항목을 삭제할 때도 이걸 써서 `cont`(연속 재생)까지 끈다
- `reset()` 은 맨 먼저 열린 `.edit` 를 취소 — 작업 중 새 파일을 끌어다 놓을 때 입력창이 남아 새 파일의 같은 번호를 바꾸는 것 방지
- `zipBlob` 은 캐시 → 이름 바꾸기·삭제·되살리기 때 반드시 `zipBlob=null` 로 무효화
- `setStatus` 는 `#status1`(첫 화면)과 `#status2`(도구 막대)에 같이 쓴다
- `claude.use('downloads')` 가 있으면(Claude 아티팩트 환경) 그걸로 저장, 없으면 `<a download>`

## 테스트 절차
실제 .pin 이 없으면 브라우저 콘솔에서 가짜 파일을 만들어 넣는다:
```js
const d=new Uint8Array(4096);
for(const o of [1024,2048,3072]){ d.set([0x49,0x44,0x33,3,0,0,0,0,0,0],o); for(let i=10;i<300;i++) d[o+i]=1; }
const dt=new DataTransfer(); dt.items.add(new File([d],'test_bk.pin'));
const inp=document.getElementById('file'); inp.files=dt.files; inp.dispatchEvent(new Event('change'));
```
라이트·다크 둘 다 확인: `document.documentElement.dataset.theme='dark'`

## 함정
- 더블클릭은 click 이벤트 2번을 먼저 발생시키므로 이름 바꾸기 시 해당 음원이 재생 시작됨(의도된 허용).
  입력창 안의 click/dblclick/mousedown/keydown 은 stopPropagation 으로 재생·단축키와 분리.
- 이름 저장(`finish`)은 `applyView()` 를 부르므로 '이름 없음' 보기에서 이름을 붙이면 그 행이 즉시 사라진다(의도).
- 구조 분석은 세계지도 세이맵 파일 1개 기준. 다른 .pin 은 추출 안 될 수 있음.
- 테이블 영역은 암호화되어 해석하지 않음 → 스티커 ↔ 음원 매칭 정보 없음.
- `index.html` 을 file:// 로 열고 받은 ZIP은 `Zone.Identifier` 가 `ZoneId=4`(제한된 사이트)로 붙어
  탐색기가 압축 해제를 막는다. 해결: `Unblock-File <zip>` 또는 속성 → 차단 해제.
  https(GitHub Pages)로 열고 받으면 이 문제가 없도록 Pages 주소 사용을 권장.
- 저장소는 Pages 때문에 공개(public) 상태 — 음원·.pin 같은 저작물은 절대 커밋하지 않는다.

## 관례
- 텍스트 파일은 BOM 없는 UTF-8, UI 문구·주석은 한국어
- 색은 CSS 변수만 — 새 색을 넣으면 라이트·다크 둘 다 정의
- 커밋 메시지: 한국어 한 줄 요약 (예: `음원 목록 더블클릭으로 파일명 수정 기능 추가`)
- 배포: GitHub Pages(main 브랜치 루트) — https://stepersjmj-hash.github.io/saypen/
