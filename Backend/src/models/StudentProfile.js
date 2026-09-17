import mongoose from 'mongoose';

const studentProfileSchema = new mongoose.Schema(
  {
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: false,
    },
    targetDomain: {
      type: String,
      required: [true, 'Target domain is required'],
    },
    academicDetails: {
      studentName: { type: String, required: true },
      email: { type: String, required: true },
      collegeName: { type: String, default: '' },
      branch: { type: String, default: '' },
      graduationYear: { type: String, default: '' },
    },
    profileLinks: {
      githubUrl: { type: String, default: '' },
      leetcodeUrl: { type: String, default: '' },
      hackerRankUrl: { type: String, default: '' },
      linkedinUrl: { type: String, default: '' },
      resumeFileName: { type: String, default: '' },
      resumeFilePath: { type: String, default: '' },
      resumeMode: { type: String, enum: ['file', 'text'], default: 'file' },
    },
  },
  {
    timestamps: true,
  }
);

export const StudentProfile = mongoose.model('StudentProfile', studentProfileSchema);
