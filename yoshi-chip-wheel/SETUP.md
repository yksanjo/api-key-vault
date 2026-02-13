# Quick Setup Guide 🚀

## Prerequisites
- Node.js (v16+) and npm
- MongoDB
- Stripe account (for payments)

## Quick Start

### 1. Clone and Setup
```bash
git clone <your-repo>
cd yoshi-chip-wheel
```

### 2. Environment Setup
```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env with your keys

# Frontend
cp frontend/.env.example frontend/.env
```

### 3. Install Dependencies
```bash
# Backend
cd backend
npm install

# Frontend
cd ../frontend
npm install
```

### 4. Start MongoDB
```bash
# macOS
brew services start mongodb-community

# Ubuntu
sudo systemctl start mongod

# Or use Docker
docker run -d -p 27017:27017 --name mongodb mongo:6.0
```

### 5. Run the App
```bash
# Option 1: Use the startup script
./start.sh

# Option 2: Run manually
# Terminal 1 (Backend)
cd backend && npm run dev

# Terminal 2 (Frontend)
cd frontend && npm start
```

### 6. Access the App
- Frontend: http://localhost:3000
- Backend: http://localhost:5000

## Docker Alternative
```bash
docker-compose up -d
```

## First Time Setup
1. Register a new account
2. Buy some chips (demo mode available)
3. Join a game round
4. Watch the wheel spin every minute!

## Troubleshooting
- Ensure MongoDB is running
- Check environment variables
- Verify ports 3000 and 5000 are free
- Check browser console for errors

## Support
Check the main README.md for detailed documentation.
