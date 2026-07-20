# codex-files

개인 Codex 전역 설정을 여러 기기에서 동일하게 사용하기 위한 저장소입니다.

## 새 기기 설정

Codex를 처음 실행하기 전에 저장소를 기본 설정 경로로 복제합니다.

```bash
git clone https://github.com/sangjun-pullim/codex-files.git ~/.codex
codex login
```

Claude 설정을 함께 사용하는 기기에서는 `~/.claude`를 먼저 구성한 뒤 필요할 때 동기화합니다.

```bash
~/.codex/bin/sync-from-claude
```

동기화 스크립트는 Python 3.11 이상을 사용하며, 비밀 파일 차단 훅은 `jq`를 사용합니다.

## 버전 관리 범위

- Codex 기본 설정과 전역 지침
- planner/reviewer 에이전트 설정
- 사용자 훅과 동기화 스크립트
- 공통 규칙
- Claude 설정 마이그레이션 스킬

인증 정보, 대화 기록, 세션, 로그, 임시 파일, 백업, 캐시는 버전 관리하지 않습니다.
