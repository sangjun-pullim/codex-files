# codex-files

개인 Codex 전역 설정을 여러 기기에서 동일하게 사용하기 위한 저장소입니다.

## 새 기기 설정

Codex를 처음 실행하기 전에 저장소를 기본 설정 경로로 복제합니다.

```bash
git clone https://github.com/sangjun-pullim/codex-files.git ~/.codex
python3 ~/.codex/bin/link-agent-skills.py
codex login
```

스킬은 이 저장소의 `agent-skills/`에서 관리하고, Codex의 탐색 경로인
`~/.agents/skills`를 해당 디렉터리에 심볼릭 링크로 연결합니다.
설정과 스킬 변경을 이 저장소에서 함께 커밋합니다.

## 기존 환경에서 스킬 연결

저장소를 업데이트한 뒤 다음 명령을 실행합니다.

```bash
python3 ~/.codex/bin/link-agent-skills.py
```

이미 올바른 링크가 있으면 그대로 유지합니다. 기존 `~/.agents/skills`가 실제 폴더라면
저장소의 스킬과 내용·파일 권한이 일치하는지 확인하고,
`~/.agents/skills-backup-*/skills`에 원본을 보존한 뒤 연결합니다.
서로 다르거나 다른 곳을 가리키는 링크가 있으면 중단하므로, 필요한 로컬 변경을
`agent-skills/`에 반영한 뒤 다시 실행합니다. 설치 스크립트는 Claude 파일을 수정하지 않습니다.

## Codex 독립 설정

`AGENTS.md`, `rules/`, `agents/`, `agent-skills/`, `hooks/`는 Codex 원본입니다.
Claude 설정에서 동기화하지 않습니다. `bin/sync-from-claude`는 어떤 옵션으로 실행해도
파일을 변경하지 않고 종료합니다. 전역 지침과 스킬은 이 저장소에서 직접 수정합니다.

`config.toml`의 추가 지침은 실행 지속성과 승인 경계 해석만 다룹니다.
개인 규칙은 `AGENTS.md`, 작업별 절차는 스킬과 필요할 때 읽는 참조 파일에 둡니다.
프로젝트별 규칙은 `AGENTS.md`를 사용하며 `CLAUDE.md` 자동 fallback은 사용하지 않습니다.

Orca는 별도 `CODEX_HOME`을 사용합니다. 현재 계정의 `AGENTS.md`, `rules`, 에이전트 파일은
이 저장소를 참조하고, 계정 config의 개인 지침과 fallback 설정은 같은 값으로 유지합니다.
계정별 인증·MCP·모델·훅 승인 상태는 전체 config 복사로 덮어쓰지 않습니다.
훅 경로 변경에 필요한 신뢰 승인은 Codex UI에서 처리하고 승인 해시를 직접 만들지 않습니다.

`skills/migrate-to-codex/`는 명시적으로 요청된 별도 마이그레이션용 도구로만 보관합니다.
개인 설정을 다시 Claude 기반으로 바꾸는 용도로 실행하지 않습니다.
비밀 파일 차단 훅은 `jq`를 사용합니다.

검증:

```bash
python3 -m unittest discover -s skills/migrate-to-codex/tests
```

## 버전 관리 범위

- Codex 기본 설정과 전역 지침
- planner/reviewer 에이전트 설정
- 사용자 훅과 동기화 스크립트
- 공통 규칙
- `agent-skills/`의 개인 스킬과 지원 파일
- Claude 설정 마이그레이션 스킬

인증 정보, 대화 기록, 세션, 로그, 임시 파일, 백업, 캐시는 버전 관리하지 않습니다.
