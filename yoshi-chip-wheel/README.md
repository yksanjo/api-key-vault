# Yoshi Chip Wheel 🎯

A fun and interactive web game where players compete on a spinning wheel to win Yoshi Chips!

## Features

- **Spinning Wheel Game**: Join rounds every minute and spin to win
- **Chip System**: Buy chips with real money, compete for bragging rights
- **Real-time Updates**: WebSocket integration for live game updates
- **Leaderboard**: Track top players and their achievements
- **Authentication**: Secure user accounts with JWT
- **Stripe Integration**: Safe payment processing for chip purchases

## Tech Stack

### Backend
- Node.js + Express
- MongoDB with Mongoose
- Socket.IO for real-time communication
- JWT authentication
- Stripe payment processing
- Node-cron for automated game rounds

### Frontend
- React 18
- Tailwind CSS for styling
- Framer Motion for animations
- Socket.IO client for real-time updates
- React Router for navigation

## Game Rules

1. **Joining**: Each round costs 100 Yoshi Chips
2. **Spinning**: Wheel spins automatically every minute
3. **Winning**: Winner gets the total pot (players × 100 chips)
4. **Chips**: Can only be used in-game, no cashing out
5. **Pricing**: 5,000 chips = $5 USD

## Installation

### Prerequisites
- Node.js (v16 or higher)
- MongoDB
- Stripe account

### Backend Setup
```bash
cd backend
npm install
cp .env.example .env
# Edit .env with your configuration
npm run dev
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Environment Variables

### Backend (.env)
```
MONGODB_URI=mongodb://localhost:27017/yoshi-chip-wheel
JWT_SECRET=your-super-secret-jwt-key-here
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key_here
FRONTEND_URL=http://localhost:3000
PORT=5000
```

### Frontend (.env)
```
REACT_APP_BACKEND_URL=http://localhost:5000
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login

### Game
- `GET /api/game/state` - Get current game state
- `POST /api/game/join` - Join current game round

### Payments
- `POST /api/payments/create-payment-intent` - Create Stripe payment
- `POST /api/payments/confirm-payment` - Confirm payment and add chips

### Leaderboard
- `GET /api/leaderboard` - Get top players

## Game Flow

1. Users register/login and buy chips
2. Players join the next round (cost: 100 chips)
3. Every minute, the wheel spins automatically
4. Random winner is selected
5. Winner receives total pot
6. New round begins

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

ISC License

---

**Note**: This is a demo application. In production, ensure proper security measures, error handling, and testing are implemented.
