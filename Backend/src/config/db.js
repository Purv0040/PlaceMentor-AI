import mongoose from 'mongoose';

export const connectDB = async () => {
  const uri = process.env.MONGODB_URI;

  if (!uri || uri.includes('<username>') || uri.includes('<password>')) {
    console.warn('\n⚠️ [MongoDB Atlas] MONGODB_URI is not configured with real credentials in Backend/.env.');
    console.warn('⚠️ Please add your MongoDB Atlas connection string in Backend/.env.');
    console.warn('⚠️ Server will run, but database queries may fail until Atlas URI is updated.\n');
    return;
  }

  try {
    const conn = await mongoose.connect(uri, {
      serverSelectionTimeoutMS: 5000,
    });
    console.log(`✅ [MongoDB Atlas] Connected successfully to host: ${conn.connection.host}`);
  } catch (error) {
    console.error(`❌ [MongoDB Atlas] Connection error: ${error.message}`);
    console.warn('⚠️ Tip: Verify your IP is whitelisted (0.0.0.0/0) in MongoDB Atlas Network Access.');
  }
};
