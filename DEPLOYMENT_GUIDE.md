# COMMAND CENTER 2026 - Deployment Guide

## Quick Start

### 1. Development Mode

```bash
# Install dependencies
npm install

# Set up Python environment (for ScopeSignal backend)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys

# Start development server
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000)

### 2. Production Build

```bash
# Build the application
npm run build

# Start production server
npm run start
```

## Environment Variables

Create a `.env` file in the root directory:

```env
# DeepSeek API (for ScopeSignal classification)
DEEPSEEK_API_KEY=your_api_key_here

# Optional: WebSocket server URL
NEXT_PUBLIC_WS_URL=ws://localhost:8080

# Optional: API base URL
NEXT_PUBLIC_API_URL=http://localhost:3000
```

## Deployment Options

### Vercel (Recommended for Next.js)

1. Push your code to GitHub
2. Import project in Vercel
3. Add environment variables in Vercel dashboard
4. Deploy!

**Note:** Python backend integration requires:
- Vercel Pro (for Python runtime support), OR
- Deploy Python backend separately (see below)

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/public ./public

EXPOSE 3000
CMD ["npm", "start"]
```

Build and run:
```bash
docker build -t command-center-2026 .
docker run -p 3000:3000 command-center-2026
```

### Python Backend Deployment

The ScopeSignal Python backend can be deployed separately:

#### Option 1: FastAPI Wrapper
```python
# api_server.py
from fastapi import FastAPI
from classifier import classify_update
import uvicorn

app = FastAPI()

@app.post("/classify")
async def classify(update_text: str, trade: str):
    return classify_update(update_text, trade)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Run with:
```bash
pip install fastapi uvicorn
python api_server.py
```

#### Option 2: Deploy to Cloud Functions
- AWS Lambda
- Google Cloud Functions
- Azure Functions

Update the Next.js API routes to point to your cloud function URL.

### WebSocket Server (Optional)

For real-time updates, deploy a WebSocket server:

```javascript
// websocket-server.js
const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', (ws) => {
  console.log('Client connected');
  
  // Simulate real-time updates
  const interval = setInterval(() => {
    ws.send(JSON.stringify({
      type: 'update',
      data: {
        message: 'New opportunity detected',
        timestamp: new Date().toISOString()
      }
    }));
  }, 5000);

  ws.on('close', () => {
    clearInterval(interval);
    console.log('Client disconnected');
  });
});

console.log('WebSocket server running on port 8080');
```

Run with:
```bash
node websocket-server.js
```

## Production Considerations

### Performance Optimization

1. **Enable caching for Python classifier:**
   - Already implemented in the ScopeSignal classifier
   - Cache is stored in `.scopesignal_cache/`

2. **Enable Next.js caching:**
   ```bash
   # In production, Next.js automatically enables caching
   npm run build
   ```

3. **CDN Integration:**
   - Deploy static assets to a CDN
   - Configure in `next.config.js`:
   ```javascript
   module.exports = {
     assetPrefix: 'https://cdn.example.com',
   }
   ```

### Security

1. **API Rate Limiting:**
   ```typescript
   // middleware.ts
   import { NextResponse } from 'next/server'
   import type { NextRequest } from 'next/server'
   
   const rateLimit = new Map()
   
   export function middleware(request: NextRequest) {
     const ip = request.ip ?? '127.0.0.1'
     const limit = rateLimit.get(ip) ?? { count: 0, resetTime: Date.now() + 60000 }
     
     if (Date.now() > limit.resetTime) {
       limit.count = 0
       limit.resetTime = Date.now() + 60000
     }
     
     if (limit.count > 100) {
       return NextResponse.json({ error: 'Rate limit exceeded' }, { status: 429 })
     }
     
     limit.count++
     rateLimit.set(ip, limit)
     
     return NextResponse.next()
   }
   ```

2. **Environment Variable Protection:**
   - Never commit `.env` files
   - Use secret management services in production
   - Rotate API keys regularly

3. **CORS Configuration:**
   ```javascript
   // next.config.js
   module.exports = {
     async headers() {
       return [
         {
           source: '/api/:path*',
           headers: [
             { key: 'Access-Control-Allow-Origin', value: 'https://yourdomain.com' },
             { key: 'Access-Control-Allow-Methods', value: 'GET,POST,OPTIONS' },
           ],
         },
       ]
     },
   }
   ```

### Monitoring

1. **Error Tracking:**
   - Integrate Sentry or similar service
   - Monitor API failures
   - Track Python classifier errors

2. **Performance Monitoring:**
   - Use Vercel Analytics
   - Monitor API response times
   - Track WebSocket connection health

3. **Logging:**
   ```typescript
   // lib/logger.ts
   export const logger = {
     info: (message: string, data?: any) => {
       console.log(`[INFO] ${message}`, data)
     },
     error: (message: string, error: any) => {
       console.error(`[ERROR] ${message}`, error)
     },
   }
   ```

## Troubleshooting

### Common Issues

1. **Python classifier not found:**
   - Ensure Python is in PATH
   - Activate virtual environment
   - Install dependencies: `pip install -r requirements.txt`

2. **WebSocket connection fails:**
   - Check WebSocket server is running
   - Verify NEXT_PUBLIC_WS_URL is correct
   - Check firewall settings

3. **Build fails:**
   - Clear `.next` cache: `rm -rf .next`
   - Delete node_modules: `rm -rf node_modules`
   - Reinstall: `npm install`
   - Rebuild: `npm run build`

4. **Voice control not working:**
   - Only works in HTTPS (or localhost)
   - Requires Chrome/Edge for best support
   - Check microphone permissions

## Scaling Considerations

### Horizontal Scaling

- Deploy multiple Next.js instances behind a load balancer
- Use shared cache for Python classifier (Redis)
- Implement distributed WebSocket connections

### Database Integration

For persistent data storage:

```typescript
// lib/db/prisma.ts
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

export default prisma
```

### Queue System

For heavy processing:

```typescript
// lib/queue/classifier-queue.ts
import Bull from 'bull'

const classifierQueue = new Bull('classifier', {
  redis: {
    host: process.env.REDIS_HOST,
    port: parseInt(process.env.REDIS_PORT || '6379'),
  },
})

classifierQueue.process(async (job) => {
  const { update_text, trade } = job.data
  // Process classification
})
```

## Support

For issues related to:
- **Dashboard/Frontend:** Check DASHBOARD_README.md
- **ScopeSignal Classifier:** Check README.md
- **Deployment:** This document

## License

MIT - See LICENSE file for details
