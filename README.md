<p align="center">
  <img src="docs/01home.png" alt="DIO Bank" width="100%">
</p>
# DIO Bank

Aplicação Django para solicitar cartões e acompanhar o andamento com segurança.

## Recursos

- Cadastro, login e recuperação de senha.
- Solicitação, filtro, paginação e linha do tempo de status.
- Notificações por e-mail quando o status muda.
- Cartões tokenizados: número e CVV não são persistidos.
- API JSON autenticada e esquema OpenAPI.
- SQLite para desenvolvimento e PostgreSQL via `DATABASE_URL`.
- Testes, cobertura, CI, Docker e cabeçalhos de segurança.

## Desenvolvimento

Requer Python 3.11 e Poetry.

```bash
cp .env.example .env
set -a; source .env; set +a
poetry install --no-root
poetry run python manage.py migrate
poetry run python manage.py createsuperuser
poetry run python manage.py runserver
```

Para testes:

```bash
DEBUG=True poetry run coverage run manage.py test
poetry run coverage report
```

Com Docker e PostgreSQL:

```bash
docker compose up --build
```

## Variáveis de ambiente

Use `.env.example` como referência. Em produção, defina uma `SECRET_KEY` longa, `DEBUG=False`, os hosts permitidos, `DATABASE_URL` e um servidor SMTP. O arquivo `.env` não deve ser versionado.

## API

`GET /cards/api/` retorna apenas os cartões da sessão autenticada, sem token, número completo ou CVV. O esquema OpenAPI está em `GET /api/schema/`.

Exemplo de resposta:

```json
{"results":[{"id":1,"name":"DIO Bank Platinum","last_four":"1234","network":"Visa","status":"P","status_label":"Pendente","created_at":"2026-09-04T12:00:00-03:00"}]}
```

## Segurança

O sistema gera um número temporário válido pelo algoritmo de Luhn, retém somente os quatro últimos dígitos e um token aleatório e descarta o número e o CVV antes da persistência. Para emissão real, substitua o gerador por um provedor PCI DSS; este projeto não processa transações.
