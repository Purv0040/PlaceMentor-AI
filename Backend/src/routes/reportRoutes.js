import express from 'express';
import {
  createReport,
  getReportById,
  getSkillRoadmap,
  downloadReport,
} from '../controllers/reportController.js';
import { optionalAuth } from '../middleware/authMiddleware.js';
import { uploadResume } from '../middleware/uploadMiddleware.js';

const router = express.Router();

router.post('/', optionalAuth, uploadResume.single('resume'), createReport);
router.get('/:id', getReportById);
router.post('/:id/roadmap', getSkillRoadmap);
router.get('/:id/download', downloadReport);

export default router;
