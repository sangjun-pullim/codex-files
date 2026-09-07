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

## Claude에서 선택적으로 가져오기

Claude 설정이 있는 기기에서는 필요한 경우 다음 명령으로 전역 지침·에이전트 등
기존 동기화 항목을 갱신합니다. 기본 실행은 Codex 스킬을 보존합니다.

```bash
~/.codex/bin/sync-from-claude
```

Claude 스킬과 명령도 가져오려면 `--skills`를 명시합니다.
이 옵션은 같은 이름의 Codex 스킬 수정을 덮어쓸 수 있으므로 먼저 미리보기를 확인합니다.

```bash
~/.codex/bin/sync-from-claude --skills --dry-run
~/.codex/bin/sync-from-claude --skills
git -C ~/.codex diff -- agent-skills/
```

동기화 스크립트는 Python 3.11 이상을 사용하며, 비밀 파일 차단 훅은 `jq`를 사용합니다.

## 버전 관리 범위

- Codex 기본 설정과 전역 지침
- planner/reviewer 에이전트 설정
- 사용자 훅과 동기화 스크립트
- 공통 규칙
- `agent-skills/`의 개인 스킬과 지원 파일
- Claude 설정 마이그레이션 스킬

인증 정보, 대화 기록, 세션, 로그, 임시 파일, 백업, 캐시는 버전 관리하지 않습니다.
