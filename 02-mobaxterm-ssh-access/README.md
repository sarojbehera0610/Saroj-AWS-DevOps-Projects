# 🟢 02 MobaXterm Production SSH Access

**GUI terminal + SFTP → Ubuntu EC2 13.203.156.167** [file:246]

## Dual Terminal Strategy (Production Ops)
| Terminal | Use Case | Status |
|----------|----------|--------|
| MobaXterm | Interactive ops, file transfer, tabs | ⏳ Testing |
| CMD SSH | Automation, CI/CD pipelines | ✅ Live |
| AWS Console | Emergency rescue | ✅ Available |

## Target Infrastructure

Ubuntu EC2: 13.203.156.167 (Public IP)
User: ubuntu
Key: saroj-ubuntu-prod-2026.pem

