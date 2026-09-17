import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

import { connectDB } from './config/db.js';
import authRoutes from './routes/authRoutes.js';
import domainRoutes from './routes/domainRoutes.js';
import reportRoutes from './routes/reportRoutes.js';
import { notFoundHandler, errorHandler } from './middleware/errorHandler.js';

// Load environment variables
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 8000;

// Connect to MongoDB Atlas
connectDB();

// Global Middleware
app.use(
  cors({
    origin: true, // Allow frontend on localhost:5173 or other ports
    credentials: true,
  })
);

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Serve uploaded resumes statically if needed
app.use('/uploads', express.static(path.join(__dirname, '../uploads')));

// Root Route Welcome
app.get('/', (req, res) => {
  res.status(200).json({
    success: true,
    message: '🚀 PlaceMentor AI Backend API is running successfully!',
    frontendUrl: 'http://localhost:3000',
    healthCheck: 'http://localhost:8000/health',
    endpoints: {
      auth: {
        register: 'POST /api/auth/register',
        login: 'POST /api/auth/login',
        me: 'GET /api/auth/me',
      },
      domains: 'GET /api/domains',
      reports: {
        create: 'POST /api/reports',
        getById: 'GET /api/reports/:id',
        roadmap: 'POST /api/reports/:id/roadmap',
        download: 'GET /api/reports/:id/download',
      },
    },
  });
});

// Health Check Endpoints
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'ok',
    service: 'PlaceMentor AI Backend',
    timestamp: new Date().toISOString(),
  });
});

app.get('/api/health', (req, res) => {
  res.status(200).json({
    status: 'ok',
    service: 'PlaceMentor AI Backend API',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
  });
});

// API Routes
app.use('/api/auth', authRoutes);
app.use('/api', authRoutes); // Fallback for /api/login and /api/register
app.use('/api/domains', domainRoutes);
app.use('/api/reports', reportRoutes);

// Error Handling Middlewares
app.use(notFoundHandler);
app.use(errorHandler);

// Start Express Server
const server = app.listen(PORT, () => {
  console.log(`
==================================================
🚀 PlaceMentor AI Backend Server is Running!
📡 Port:           http://localhost:${PORT}
🩺 Health Check:   http://localhost:${PORT}/health
📚 API Base:       http://localhost:${PORT}/api
🌐 Frontend URL:   http://localhost:5173
==================================================
  `);
});

// Graceful shutdown handling
process.on('SIGTERM', () => {
  console.log('SIGTERM signal received: closing HTTP server');
  server.close(() => {
    console.log('HTTP server closed');
  });
});
