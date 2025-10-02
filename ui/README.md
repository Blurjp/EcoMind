# Ecomind UI (Next.js)

Dashboard and admin interface for Ecomind platform.

## Features

- **Dashboard**: Today's usage overview with charts
- **Trends**: 7-day usage charts by provider
- **Dark mode** support
- **Responsive** design with Tailwind CSS

## Development

```bash
npm install
npm run dev
```

Open http://localhost:3000

## Environment Variables

- `NEXT_PUBLIC_API_URL` (default: http://localhost:8000)

## Build

```bash
npm run build
npm start
```

## Docker

```bash
docker build -t ecomind-ui .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://api:8000 ecomind-ui
```

## Pages (Planned)

- `/` - Dashboard (implemented)
- `/trends` - Historical trends
- `/alerts` - Alert management
- `/factors` - Environmental factors config
- `/reports` - ESG report generation
- `/settings` - Org/users/teams management
- `/audits` - Audit log viewer
