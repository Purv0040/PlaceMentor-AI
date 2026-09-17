import mongoose from 'mongoose';

const reportSchema = new mongoose.Schema(
  {
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: false,
    },
    domain: {
      type: String,
      required: true,
    },
    domainName: {
      type: String,
    },
    readinessScore: {
      type: Number,
      required: true,
      min: 0,
      max: 100,
    },
    grade: {
      type: String,
      required: true,
    },
    studentName: String,
    collegeName: String,
    branch: String,
    matchedSkills: [
      {
        skill: { type: String, required: true },
        foundIn: { type: String, required: true },
      },
    ],
    missingSkills: [
      {
        skill: { type: String, required: true },
        reason: { type: String, required: true },
      },
    ],
    comparisonSummary: [String],
    recommendations: [
      {
        title: { type: String, required: true },
        desc: { type: String, required: true },
        priority: { type: String, enum: ['High', 'Medium', 'Low'], default: 'Medium' },
      },
    ],
    projectSuggestions: [String],
    profileAnalysis: {
      github: {
        repoCount: Number,
        reposCount: Number,
        topLanguages: [String],
        summary: String,
        details: mongoose.Schema.Types.Mixed,
      },
      leetcode: {
        solved: {
          easy: Number,
          medium: Number,
          hard: Number,
        },
        solvedCount: Number,
        topTags: [String],
        details: mongoose.Schema.Types.Mixed,
      },
      hackerrank: {
        badgesCount: Number,
        stars: Number,
        domains: [String],
        details: mongoose.Schema.Types.Mixed,
      },
      resume: {
        atsScore: Number,
        extractedSkills: [String],
        missingSections: [String],
        details: mongoose.Schema.Types.Mixed,
      },
    },
    generatedAt: {
      type: String,
    },
  },
  {
    timestamps: true,
  }
);

export const Report = mongoose.model('Report', reportSchema);
