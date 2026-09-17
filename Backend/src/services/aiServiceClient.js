import axios from 'axios';
import FormData from 'form-data';
import fs from 'fs';

const RESUME_SERVICE_URL = process.env.AI_RESUME_URL || 'http://localhost:8001';
const GITHUB_SERVICE_URL = process.env.AI_GITHUB_URL || 'http://localhost:8002';
const LEETCODE_SERVICE_URL = process.env.AI_LEETCODE_URL || 'http://localhost:8003';

/**
 * Extracts a username from a full URL or returns trimmed string
 */
export const extractUsername = (urlOrHandle) => {
  if (!urlOrHandle) return '';
  const trimmed = urlOrHandle.trim().replace(/\/+$/, '');
  const parts = trimmed.split('/');
  return parts[parts.length - 1].replace(/^@/, '');
};

/**
 * Call Teammate's Resume Analyzer FastAPI microservice
 */
export const analyzeResumePDF = async (filePath) => {
  if (!filePath || !fs.existsSync(filePath)) {
    return null;
  }

  try {
    const form = new FormData();
    form.append('file', fs.createReadStream(filePath));

    const response = await axios.post(`${RESUME_SERVICE_URL}/api/v1/resume/analyze`, form, {
      headers: form.getHeaders(),
      timeout: 15000,
    });
    return response.data;
  } catch (err) {
    console.warn(`[AI Service] Resume service unreachable at ${RESUME_SERVICE_URL}:`, err.message);
    return null;
  }
};

/**
 * Call Teammate's GitHub Analyzer FastAPI microservice
 */
export const analyzeGitHubProfile = async (githubUrl) => {
  const username = extractUsername(githubUrl);
  if (!username) return null;

  try {
    const response = await axios.post(
      `${GITHUB_SERVICE_URL}/api/v1/github/analyze`,
      { username },
      { timeout: 15000 }
    );
    return response.data;
  } catch (err) {
    console.warn(`[AI Service] GitHub service unreachable at ${GITHUB_SERVICE_URL}:`, err.message);
    return null;
  }
};

/**
 * Call Teammate's LeetCode Analyzer FastAPI microservice
 */
export const analyzeLeetCodeProfile = async (leetcodeUrl) => {
  const username = extractUsername(leetcodeUrl);
  if (!username) return null;

  try {
    const response = await axios.post(
      `${LEETCODE_SERVICE_URL}/api/v1/leetcode/analyze`,
      { username },
      { timeout: 15000 }
    );
    return response.data;
  } catch (err) {
    console.warn(`[AI Service] LeetCode service unreachable at ${LEETCODE_SERVICE_URL}:`, err.message);
    return null;
  }
};
