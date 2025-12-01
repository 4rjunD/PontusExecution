# Starting the Frontend

## Quick Start

```bash
cd /Users/arjundixit/Downloads/PontusExecution/PontusUserFrontend
npm run dev
```

The frontend will be available at: **http://localhost:3000**

## Access Points

- **Main Dashboard:** http://localhost:3000/dashboard
- **Route & Execute:** http://localhost:3000/dashboard/routing
- **Treasury:** http://localhost:3000/dashboard/treasury
- **Global Payouts:** http://localhost:3000/dashboard/payouts
- **FX Intelligence:** http://localhost:3000/dashboard/fx
- **Compliance:** http://localhost:3000/dashboard/compliance
- **Reconciliation:** http://localhost:3000/dashboard/reconciliation
- **Analytics:** http://localhost:3000/dashboard/analytics
- **Integrations:** http://localhost:3000/dashboard/integrations
- **Developer Platform:** http://localhost:3000/dashboard/developer

## Backend API

Make sure the backend API is running on: **http://localhost:8000**

To start the backend:
```bash
cd /Users/arjundixit/Downloads/PontusExecution/Pontus-Execution-Layer
python -m app.main
```

## Troubleshooting

If the frontend doesn't load:
1. Check if port 3000 is available: `lsof -i :3000`
2. Kill any existing process: `lsof -ti:3000 | xargs kill -9`
3. Restart: `npm run dev`

If API calls fail:
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check `.env.local` has: `NEXT_PUBLIC_API_URL=http://localhost:8000`


