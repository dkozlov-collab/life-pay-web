# LIFE PAY Web v7 — New Events + Admin Access Cleanup

Добавлено:
- Новые отгрузки, перемещения и замены поднимаются вверх.
- На дашборде появился верхний блок “Новые отгрузки, перемещения и замены”.
- В карточке организации статус “Полный доступ” показывается только администратору.
- У обычных пользователей убран статус доступа из карточки.
- Из остатков убраны ответственные лица.
- Сохранены: PIN login, Google Sheets CSV, Excel export, отгрузки, перемещения, долги/замены, статистика M–AB, новости, админ аналитика, темы, звуки и мобильная адаптация.

## Deploy
Backend Render: root `backend`, start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
Frontend Vercel: root `frontend`, env `NEXT_PUBLIC_API_URL=https://life-pay-web.onrender.com`

## Vercel dependency install fix
The frontend package lock generated in the previous archive referenced a private build registry.
This package removes that lock file and forces npm to use https://registry.npmjs.org/.
Vercel root directory: frontend
Environment variable: NEXT_PUBLIC_API_URL=https://life-pay-web.onrender.com
