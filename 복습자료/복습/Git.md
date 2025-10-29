## ✅ Git 기본 흐름 (로컬 작업)

| 명령어 | 하는 일 |
|--------|----------|
| `git init` | 현재 폴더를 Git 저장소로 초기화 |
| `git status` | 변경된 파일 상태 확인 |
| `git add .` | 모든 변경 파일을 스테이징(커밋 후보로 등록) |
| `git commit -m "msg"` | 변경사항을 기록(스냅샷 생성) |
| `git log --oneline` | 커밋 이력 간단히 보기 |

---

## ✅ 원격 저장소 연결 & 확인

| 명령어 | 하는 일 |
|--------|----------|
| `git remote -v` | 연결된 원격 저장소 주소 확인 |
| `git remote add origin URL` | 원격 저장소 추가 |
| `git remote set-url origin URL` | 원격 저장소 주소 변경 |

---

## ✅ 원격과 동기화

| 명령어 | 의미 |
|--------|------|
| `git push -u origin main` | 원격 main으로 최초 푸시 & 추적 설정 |
| `git push` | 이후에는 단독 push 가능 |
| `git pull` | 원격 변경사항 가져와 병합 |
| `git fetch` | 가져오기만 하고 병합은 안함 |
| `git pull --rebase` | 이력 깔끔하게 가져온 뒤 내 커밋 위로 재배치 |

---

## ✅ 브랜치

| 명령어 | 설명 |
|--------|------|
| `git branch` | 브랜치 목록 보기 |
| `git branch 새이름` | 새 브랜치 생성 |
| `git checkout 새이름` | 브랜치 이동 |
| `git checkout -b 새이름` | 생성 + 이동 한 번에 |
| `git merge 브랜치명` | 현재 브랜치에 다른 브랜치 병합 |
| `git branch -d 브랜치명` | merge된 브랜치 삭제 |
| `git branch -D 브랜치명` | 강제 삭제 |

---

## ✅ 롤백 / 실수 처리

| 명령어 | 설명 |
|--------|------|
| `git restore 파일명` | 스테이징 전 변경 취소(파일 되돌림) |
| `git reset --hard origin/main` | 원격 상태로 강제 되돌림(조심!) |
| `git stash` | 변경사항 임시 숨김 |
| `git stash pop` | 숨긴 변경 다시 적용 |
| `git revert 커밋ID` | 기록 남기며 특정 커밋 되돌리기 |
