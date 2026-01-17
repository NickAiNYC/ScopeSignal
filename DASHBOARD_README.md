# COMMAND CENTER 2026

## Overview

COMMAND CENTER 2026 is an enterprise-grade, animated dashboard system that integrates four projects into one unified intelligence platform:

1. **ViolationSentinel** - Compliance Enforcement Dashboard
2. **Regula** - Healthcare Revenue Recovery Dashboard  
3. **AI-PulsePoint** - AI Model Intelligence Dashboard
4. **ScopeSignal** - Construction Opportunity Radar

## Features

### Advanced Architecture
- **Next.js 14** with App Router for optimal performance
- **TypeScript** for type-safe development
- **Tailwind CSS** for modern, responsive styling
- Modular component architecture for easy maintenance

### Visual & Interactive Features
- **Framer Motion** animations for smooth transitions and interactions
- **Three.js** 3D visualizations for geographic data mapping
- **Recharts** for interactive data charts
- **Real-time WebSocket** integration for live data updates
- **Voice Control** using browser Speech Recognition API

### Dashboard Modules

#### ScopeSignal Module
- Construction opportunity tracking and classification
- Real-time project updates feed
- 3D geographic visualization of opportunities
- Confidence-based filtering (CONTESTABLE, SOFT_OPEN, CLOSED)
- Integration with Python classification backend

#### ViolationSentinel Module
- Compliance violation monitoring
- Critical alerts with pulse animations
- Weekly trend analysis
- Severity-based categorization

#### Regula Module
- Healthcare revenue recovery tracking
- Revenue leak source analysis
- Monthly recovery trend visualization
- Currency-formatted metrics

#### AI-PulsePoint Module
- AI model performance monitoring
- Anomaly detection alerts
- Model health status tracking
- Radar chart performance metrics

### Voice Commands

The system supports natural language voice commands:
- "Show me healthcare violations" → Navigate to Regula
- "Open ScopeSignal" → Navigate to ScopeSignal
- "Show compliance" → Navigate to ViolationSentinel
- "AI intelligence" → Navigate to AI-PulsePoint
- "Go home" → Return to dashboard

## Installation

### Prerequisites
- Node.js 18 or higher
- Python 3.8+ (for ScopeSignal backend)
- npm or yarn

### Setup

1. **Install Node.js dependencies:**
```bash
npm install
```

2. **Install Python dependencies** (for ScopeSignal backend):
```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

4. **Run the development server:**
```bash
npm run dev
```

5. **Open your browser:**
Navigate to [http://localhost:3000](http://localhost:3000)

## Development

### Project Structure

```
├── app/                          # Next.js app directory
│   ├── api/                      # API routes
│   │   └── scopesignal/         # ScopeSignal Python backend integration
│   ├── violation-sentinel/       # ViolationSentinel module page
│   ├── regula/                   # Regula module page
│   ├── ai-pulsepoint/           # AI-PulsePoint module page
│   ├── scopesignal/             # ScopeSignal module page
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Home page
│   └── globals.css              # Global styles
├── components/                   # React components
│   ├── layout/                  # Layout components
│   ├── modules/                 # Dashboard modules
│   ├── ui/                      # UI components
│   ├── voice/                   # Voice control components
│   └── visualizations/          # 3D visualizations
├── lib/                         # Utilities and services
│   ├── hooks/                   # Custom React hooks
│   ├── websocket/              # WebSocket service
│   └── utils/                   # Utility functions
├── classifier/                  # Python ScopeSignal classifier
├── data/                        # Python data utilities
└── evaluation/                  # Python evaluation tools
```

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Check TypeScript types

### Python Backend Integration

The ScopeSignal module integrates with the existing Python classifier:

**Classify single update:**
```typescript
const response = await fetch('/api/scopesignal/classify', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    update_text: 'RFP issued for electrical work',
    trade: 'Electrical'
  })
})
const result = await response.json()
```

**Batch processing:**
```typescript
const response = await fetch('/api/scopesignal/batch', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    updates: [
      { text: 'Amendment 2 issued', trade: 'Electrical' },
      { text: 'RFP posted for HVAC work', trade: 'HVAC' }
    ]
  })
})
const results = await response.json()
```

## Technologies

### Frontend
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Framer Motion
- Three.js / React Three Fiber
- Recharts
- Lucide React Icons

### Backend Integration
- Python 3.8+
- OpenAI API (via DeepSeek)
- Next.js API Routes
- WebSocket for real-time data

## Browser Support

- Chrome/Edge (recommended for voice control)
- Firefox
- Safari (limited voice control support)

Voice control requires browser support for the Web Speech API.

## Contributing

This project follows the existing ScopeSignal philosophy:
- Conservative design over complexity
- Explicit over implicit
- Documentation that earns trust

## License

MIT

## Acknowledgments

Built on top of the ScopeSignal project, demonstrating:
- Full-stack AI integration
- Real-time data visualization
- Voice-controlled interfaces
- Modern web architecture

---

**COMMAND CENTER 2026** - Where intelligence meets action.
