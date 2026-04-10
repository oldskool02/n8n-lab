up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

backup:
	./scripts/backup.sh

recover:
	./scripts/full-recovery.sh
