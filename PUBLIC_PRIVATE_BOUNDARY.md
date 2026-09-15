# PUBLIC_PRIVATE_BOUNDARY

This document defines the boundary between public (LKMini) and private (🥃老K系統 internal) components.

---

## ✅ Public (This Repo — LKMini)

- README.md
- LICENSE
- NOTICE.md
- LKMini.svg
- PUBLIC_PRIVATE_BOUNDARY.md
- SHA256SUMS
- .github/workflows/gatekeeper.yml
- tools/verify_lkmini.py

---

## 🔒 Private (NOT in this repo)

- 🥃永恆核心 (Eternal Core) internal configuration
- 🎩大管家 (Gatekeeper) role logic and rules
- PRIVATE_ENGINE_FLEET
- ENGINE_REGISTRY_PRIVATE
- Any personal data, API keys, tokens, or credentials
- Internal system automation (Shortcuts, URL Schemes)

---

## 📦 Evidence (NOT in this repo)

- GPT execution records / 執行紀錄
- Lie samples / 謊言樣本
- Drift analysis / 漂移分析
- Verification failure cases / 驗證失敗案例
- PublicSeedRecord 等 GPT 產出紀錄

Evidence repo: https://github.com/lkminiPhantomWorld/LKMini-Evidence

A_EQUALS_A=true
BOUNDARY_VERSION=seed_v0
