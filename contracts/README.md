# Контракт Agent Runtime

`agent-runtime-api.yaml` — проверенная копия API из релиза
`portable-agent/contracts` версии `2.1.0`.

Обновляй файл только командой:

```powershell
.\scripts\update-contract.ps1 -Version 2.1.0
```

Скрипт проверяет SHA-256 и GitHub attestation релизного архива до замены файла.
Тест `test_contract.py` проверяет реальные запросы и ответы сервиса по этой схеме.
