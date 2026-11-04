# saypen — 세이펜 PIN 음원 추출기

세이펜 북 파일(.pin)에서 MP3 음원을 잘라내 미리 듣고, 이름을 바꿔 ZIP으로 저장하는
단일 HTML 웹앱. 빌드·서버·외부 라이브러리 없음. 모든 처리는 브라우저 안에서만.

## 구성
- `index.html` — 화면·스타일·스크립트 전부 (IIFE 하나)
- `README.md` — 사용자용 안내

## 동작 구조 (index.html 스크립트)
- `handle(file)` — .pin 을 읽어 ID3 헤더(`"ID3"`+버전2~4) 위치를 찾음. 512바이트 정렬된
  헤더가 있으면 그것만 쓰고, 없으면 전체 매치를 씀. 각 구간 끝의 0 패딩 제거 → `segs[]`
- `names[]` — 각 음원의 파일명(확장자 제외). 기본값 `0001` 형식. 목록 `.num` 더블클릭 →
  `startRename(i)` 인라인 입력 (Enter/포커스 이탈 = 저장, Esc = 취소, 빈칸 = 번호로 복귀)
- `cleanName` — `\ / : * ? " < > |`·제어문자 제거, 끝 `.mp3`·점·공백 제거
- `zipNames()` — ZIP 안 이름 중복 시 ` (2)` 붙임 (대소문자 무시)
- `buildZip` — 무압축(STORE) ZIP 직접 생성, UTF-8 파일명 플래그(0x0800)
- `zipBlob` 은 캐시 → 이름을 바꾸면 반드시 `zipBlob=null` 로 무효화
- `claude.use('downloads')` 가 있으면(Claude 아티팩트 환경) 그걸로 저장, 없으면 `<a download>`

## 테스트 절차
실제 .pin 이 없으면 브라우저 콘솔에서 가짜 파일을 만들어 넣는다:
```js
const d=new Uint8Array(4096);
for(const o of [1024,2048,3072]){ d.set([0x49,0x44,0x33,3,0,0,0,0,0,0],o); for(let i=10;i<300;i++) d[o+i]=1; }
const dt=new DataTransfer(); dt.items.add(new File([d],'test_bk.pin'));
const inp=document.getElementById('file'); inp.files=dt.files; inp.dispatchEvent(new Event('change'));
```

## 함정
- 더블클릭은 click 이벤트 2번을 먼저 발생시키므로 이름 바꾸기 시 해당 음원이 재생 시작됨(의도된 허용).
  입력창 안의 click/dblclick/mousedown/keydown 은 stopPropagation 으로 재생·단축키와 분리.
- 구조 분석은 세계지도 세이맵 파일 1개 기준. 다른 .pin 은 추출 안 될 수 있음.
- 테이블 영역은 암호화되어 해석하지 않음 → 스티커 ↔ 음원 매칭 정보 없음.

## 관례
- 텍스트 파일은 BOM 없는 UTF-8, UI 문구·주석은 한국어
- 커밋 메시지: 한국어 한 줄 요약 (예: `음원 목록 더블클릭으로 파일명 수정 기능 추가`)
- 배포: GitHub Pages(main 브랜치 루트) — https://stepersjmj-hash.github.io/saypen/
