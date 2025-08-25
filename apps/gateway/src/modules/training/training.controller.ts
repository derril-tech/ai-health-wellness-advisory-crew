import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Body,
  Param,
  Query,
  UseGuards,
  Request,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiBearerAuth } from '@nestjs/swagger';
import { TrainingService } from './training.service';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';

@ApiTags('training')
@Controller('training')
@UseGuards(JwtAuthGuard)
@ApiBearerAuth()
export class TrainingController {
  constructor(private readonly trainingService: TrainingService) {}

  // Exercise endpoints
  @Get('exercises')
  @ApiOperation({ summary: 'Get all exercises' })
  @ApiResponse({ status: 200, description: 'List of all exercises' })
  async getAllExercises() {
    return this.trainingService.findAllExercises();
  }

  @Get('exercises/:id')
  @ApiOperation({ summary: 'Get exercise by ID' })
  @ApiResponse({ status: 200, description: 'Exercise details' })
  @ApiResponse({ status: 404, description: 'Exercise not found' })
  async getExerciseById(@Param('id') id: string) {
    return this.trainingService.findExerciseById(id);
  }

  @Get('exercises/search')
  @ApiOperation({ summary: 'Search exercises' })
  @ApiResponse({ status: 200, description: 'Search results' })
  async searchExercises(@Query('q') query: string) {
    return this.trainingService.searchExercises(query);
  }

  @Get('exercises/muscle-group/:muscleGroup')
  @ApiOperation({ summary: 'Get exercises by muscle group' })
  @ApiResponse({ status: 200, description: 'Exercises for muscle group' })
  async getExercisesByMuscleGroup(@Param('muscleGroup') muscleGroup: string) {
    return this.trainingService.findExercisesByMuscleGroup(muscleGroup);
  }

  @Get('exercises/difficulty/:difficulty')
  @ApiOperation({ summary: 'Get exercises by difficulty level' })
  @ApiResponse({ status: 200, description: 'Exercises by difficulty' })
  async getExercisesByDifficulty(@Param('difficulty') difficulty: string) {
    return this.trainingService.findExercisesByDifficulty(difficulty);
  }

  @Get('exercises/equipment/:equipment')
  @ApiOperation({ summary: 'Get exercises by equipment' })
  @ApiResponse({ status: 200, description: 'Exercises by equipment' })
  async getExercisesByEquipment(@Param('equipment') equipment: string) {
    return this.trainingService.findExercisesByEquipment(equipment);
  }

  // Workout endpoints
  @Get('workouts/program/:programId')
  @ApiOperation({ summary: 'Get workouts by program' })
  @ApiResponse({ status: 200, description: 'Program workouts' })
  async getWorkoutsByProgram(
    @Param('programId') programId: string,
    @Query('week') week?: number,
  ) {
    return this.trainingService.findWorkoutsByProgram(programId, week);
  }

  @Get('workouts/:id')
  @ApiOperation({ summary: 'Get workout by ID' })
  @ApiResponse({ status: 200, description: 'Workout details' })
  @ApiResponse({ status: 404, description: 'Workout not found' })
  async getWorkoutById(@Param('id') id: string) {
    return this.trainingService.findWorkoutById(id);
  }

  @Get('workouts/program/:programId/week/:week')
  @ApiOperation({ summary: 'Get workouts by program and week' })
  @ApiResponse({ status: 200, description: 'Weekly workouts' })
  async getWorkoutsByWeek(
    @Param('programId') programId: string,
    @Param('week') week: number,
  ) {
    return this.trainingService.findWorkoutsByWeek(programId, week);
  }

  // Workout log endpoints
  @Post('workout-logs')
  @ApiOperation({ summary: 'Create workout log' })
  @ApiResponse({ status: 201, description: 'Workout log created' })
  async createWorkoutLog(
    @Request() req,
    @Body() data: {
      workout_id: string;
      started_at: Date;
      completed_at: Date;
      duration_minutes: number;
      rating?: number;
      notes?: string;
      set_logs?: Record<string, any[]>;
    },
  ) {
    return this.trainingService.createWorkoutLog(req.user.id, data.workout_id, data);
  }

  @Get('workout-logs')
  @ApiOperation({ summary: 'Get user workout logs' })
  @ApiResponse({ status: 200, description: 'User workout logs' })
  async getUserWorkoutLogs(
    @Request() req,
    @Query('limit') limit?: number,
  ) {
    return this.trainingService.findWorkoutLogsByUser(req.user.id, limit);
  }

  @Get('workout-logs/:id')
  @ApiOperation({ summary: 'Get workout log by ID' })
  @ApiResponse({ status: 200, description: 'Workout log details' })
  @ApiResponse({ status: 404, description: 'Workout log not found' })
  async getWorkoutLogById(@Param('id') id: string) {
    return this.trainingService.findWorkoutLogById(id);
  }

  @Put('workout-logs/:id')
  @ApiOperation({ summary: 'Update workout log' })
  @ApiResponse({ status: 200, description: 'Workout log updated' })
  @ApiResponse({ status: 404, description: 'Workout log not found' })
  async updateWorkoutLog(
    @Param('id') id: string,
    @Body() data: {
      completed_at?: Date;
      duration_minutes?: number;
      rating?: number;
      notes?: string;
    },
  ) {
    return this.trainingService.updateWorkoutLog(id, data);
  }

  // Exercise substitution endpoints
  @Get('exercises/:id/substitutions')
  @ApiOperation({ summary: 'Get exercise substitutions' })
  @ApiResponse({ status: 200, description: 'Exercise substitution suggestions' })
  async getExerciseSubstitutions(
    @Request() req,
    @Param('id') exerciseId: string,
    @Query('reason') reason?: string,
  ) {
    return this.trainingService.findExerciseSubstitutions(
      exerciseId,
      req.user.id,
      reason,
    );
  }

  // Progress tracking endpoints
  @Get('progress/:programId')
  @ApiOperation({ summary: 'Get user progress for program' })
  @ApiResponse({ status: 200, description: 'User progress data' })
  async getUserProgress(
    @Request() req,
    @Param('programId') programId: string,
  ) {
    return this.trainingService.getUserProgress(req.user.id, programId);
  }
}
