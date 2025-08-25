import { Injectable, NotFoundException, BadRequestException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Exercise } from './entities/exercise.entity';
import { Workout } from './entities/workout.entity';
import { WorkoutLog } from './entities/workout-log.entity';
import { WorkoutExercise } from './entities/workout-exercise.entity';
import { SetLog } from './entities/set-log.entity';

@Injectable()
export class TrainingService {
  constructor(
    @InjectRepository(Exercise)
    private exerciseRepository: Repository<Exercise>,
    @InjectRepository(Workout)
    private workoutRepository: Repository<Workout>,
    @InjectRepository(WorkoutLog)
    private workoutLogRepository: Repository<WorkoutLog>,
    @InjectRepository(WorkoutExercise)
    private workoutExerciseRepository: Repository<WorkoutExercise>,
    @InjectRepository(SetLog)
    private setLogRepository: Repository<SetLog>,
  ) {}

  // Exercise Management
  async findAllExercises(): Promise<Exercise[]> {
    return this.exerciseRepository.find({
      order: { name: 'ASC' },
    });
  }

  async findExerciseById(id: string): Promise<Exercise> {
    const exercise = await this.exerciseRepository.findOne({ where: { id } });
    if (!exercise) {
      throw new NotFoundException(`Exercise with ID ${id} not found`);
    }
    return exercise;
  }

  async findExercisesByMuscleGroup(muscleGroup: string): Promise<Exercise[]> {
    return this.exerciseRepository
      .createQueryBuilder('exercise')
      .where(':muscleGroup = ANY(exercise.muscle_groups)', { muscleGroup })
      .orderBy('exercise.name', 'ASC')
      .getMany();
  }

  async findExercisesByDifficulty(difficulty: string): Promise<Exercise[]> {
    return this.exerciseRepository.find({
      where: { difficulty },
      order: { name: 'ASC' },
    });
  }

  async findExercisesByEquipment(equipment: string): Promise<Exercise[]> {
    return this.exerciseRepository
      .createQueryBuilder('exercise')
      .where(':equipment = ANY(exercise.equipment)', { equipment })
      .orderBy('exercise.name', 'ASC')
      .getMany();
  }

  async searchExercises(query: string): Promise<Exercise[]> {
    return this.exerciseRepository
      .createQueryBuilder('exercise')
      .where('exercise.name ILIKE :query', { query: `%${query}%` })
      .orWhere('exercise.description ILIKE :query', { query: `%${query}%` })
      .orderBy('exercise.name', 'ASC')
      .getMany();
  }

  // Workout Management
  async findWorkoutsByProgram(programId: string, week?: number): Promise<Workout[]> {
    const query = this.workoutRepository
      .createQueryBuilder('workout')
      .leftJoinAndSelect('workout.exercises', 'workoutExercise')
      .leftJoinAndSelect('workoutExercise.exercise', 'exercise')
      .where('workout.program_id = :programId', { programId })
      .orderBy('workout.week', 'ASC')
      .addOrderBy('workout.day_of_week', 'ASC')
      .addOrderBy('workoutExercise.order', 'ASC');

    if (week) {
      query.andWhere('workout.week = :week', { week });
    }

    return query.getMany();
  }

  async findWorkoutById(id: string): Promise<Workout> {
    const workout = await this.workoutRepository
      .createQueryBuilder('workout')
      .leftJoinAndSelect('workout.exercises', 'workoutExercise')
      .leftJoinAndSelect('workoutExercise.exercise', 'exercise')
      .where('workout.id = :id', { id })
      .orderBy('workoutExercise.order', 'ASC')
      .getOne();

    if (!workout) {
      throw new NotFoundException(`Workout with ID ${id} not found`);
    }

    return workout;
  }

  async findWorkoutsByWeek(programId: string, week: number): Promise<Workout[]> {
    return this.workoutRepository
      .createQueryBuilder('workout')
      .leftJoinAndSelect('workout.exercises', 'workoutExercise')
      .leftJoinAndSelect('workoutExercise.exercise', 'exercise')
      .where('workout.program_id = :programId', { programId })
      .andWhere('workout.week = :week', { week })
      .orderBy('workout.day_of_week', 'ASC')
      .addOrderBy('workoutExercise.order', 'ASC')
      .getMany();
  }

  // Workout Log Management
  async createWorkoutLog(userId: string, workoutId: string, data: any): Promise<WorkoutLog> {
    const workout = await this.findWorkoutById(workoutId);
    
    const workoutLog = this.workoutLogRepository.create({
      user_id: userId,
      workout_id: workoutId,
      started_at: data.started_at,
      completed_at: data.completed_at,
      duration_minutes: data.duration_minutes,
      rating: data.rating,
      notes: data.notes,
    });

    const savedLog = await this.workoutLogRepository.save(workoutLog);

    // Save set logs if provided
    if (data.set_logs) {
      for (const [exerciseId, sets] of Object.entries(data.set_logs)) {
        for (const setData of sets as any[]) {
          const setLog = this.setLogRepository.create({
            workout_log_id: savedLog.id,
            workout_exercise_id: exerciseId,
            set_number: setData.set_number,
            reps: setData.reps,
            weight_kg: setData.weight_kg,
            rpe: setData.rpe,
            completed: setData.completed,
            notes: setData.notes,
          });
          await this.setLogRepository.save(setLog);
        }
      }
    }

    return savedLog;
  }

  async findWorkoutLogsByUser(userId: string, limit = 10): Promise<WorkoutLog[]> {
    return this.workoutLogRepository
      .createQueryBuilder('workoutLog')
      .leftJoinAndSelect('workoutLog.workout', 'workout')
      .leftJoinAndSelect('workoutLog.setLogs', 'setLogs')
      .leftJoinAndSelect('setLogs.workoutExercise', 'workoutExercise')
      .leftJoinAndSelect('workoutExercise.exercise', 'exercise')
      .where('workoutLog.user_id = :userId', { userId })
      .orderBy('workoutLog.started_at', 'DESC')
      .limit(limit)
      .getMany();
  }

  async findWorkoutLogById(id: string): Promise<WorkoutLog> {
    const workoutLog = await this.workoutLogRepository
      .createQueryBuilder('workoutLog')
      .leftJoinAndSelect('workoutLog.workout', 'workout')
      .leftJoinAndSelect('workoutLog.setLogs', 'setLogs')
      .leftJoinAndSelect('setLogs.workoutExercise', 'workoutExercise')
      .leftJoinAndSelect('workoutExercise.exercise', 'exercise')
      .where('workoutLog.id = :id', { id })
      .getOne();

    if (!workoutLog) {
      throw new NotFoundException(`Workout log with ID ${id} not found`);
    }

    return workoutLog;
  }

  async updateWorkoutLog(id: string, data: any): Promise<WorkoutLog> {
    const workoutLog = await this.findWorkoutLogById(id);
    
    Object.assign(workoutLog, {
      completed_at: data.completed_at,
      duration_minutes: data.duration_minutes,
      rating: data.rating,
      notes: data.notes,
    });

    return this.workoutLogRepository.save(workoutLog);
  }

  // Exercise Substitution
  async findExerciseSubstitutions(
    exerciseId: string,
    userId: string,
    reason: string = 'injury'
  ): Promise<Exercise[]> {
    const originalExercise = await this.findExerciseById(exerciseId);
    
    // Get user profile to check contraindications and equipment
    // This would typically come from a user service
    const userProfile = await this.getUserProfile(userId);
    
    const query = this.exerciseRepository
      .createQueryBuilder('exercise')
      .where('exercise.id != :exerciseId', { exerciseId })
      .andWhere('exercise.category = :category', { category: originalExercise.category });

    // Filter by muscle groups (at least one match)
    const muscleGroupConditions = originalExercise.muscle_groups.map(
      (group, index) => `:muscleGroup${index} = ANY(exercise.muscle_groups)`
    );
    query.andWhere(`(${muscleGroupConditions.join(' OR ')})`);
    
    originalExercise.muscle_groups.forEach((group, index) => {
      query.setParameter(`muscleGroup${index}`, group);
    });

    // Filter by available equipment
    if (userProfile.equipment_access && userProfile.equipment_access.length > 0) {
      const equipmentConditions = userProfile.equipment_access.map(
        (eq, index) => `:equipment${index} = ANY(exercise.equipment)`
      );
      query.andWhere(`(${equipmentConditions.join(' OR ')})`);
      
      userProfile.equipment_access.forEach((eq, index) => {
        query.setParameter(`equipment${index}`, eq);
      });
    }

    // Filter by experience level
    if (userProfile.experience_level === 'beginner') {
      query.andWhere('exercise.difficulty != :advanced', { advanced: 'advanced' });
    }

    // Filter out contraindicated exercises
    if (userProfile.injuries && userProfile.injuries.length > 0) {
      const contraindicationConditions = userProfile.injuries.map(
        (injury, index) => `:contraindication${index} != ANY(exercise.contraindications)`
      );
      query.andWhere(`(${contraindicationConditions.join(' AND ')})`);
      
      userProfile.injuries.forEach((injury, index) => {
        query.setParameter(`contraindication${index}`, injury.type);
      });
    }

    return query
      .orderBy('exercise.difficulty', 'ASC')
      .addOrderBy('exercise.name', 'ASC')
      .limit(5)
      .getMany();
  }

  // Progress Tracking
  async getUserProgress(userId: string, programId: string): Promise<any> {
    const workoutLogs = await this.workoutLogRepository
      .createQueryBuilder('workoutLog')
      .leftJoinAndSelect('workoutLog.workout', 'workout')
      .leftJoinAndSelect('workoutLog.setLogs', 'setLogs')
      .where('workoutLog.user_id = :userId', { userId })
      .andWhere('workout.program_id = :programId', { programId })
      .orderBy('workoutLog.started_at', 'ASC')
      .getMany();

    const progress = {
      total_workouts: workoutLogs.length,
      completion_rate: 0,
      average_rating: 0,
      total_duration: 0,
      weekly_progress: [],
      exercise_progress: {},
    };

    if (workoutLogs.length > 0) {
      progress.total_duration = workoutLogs.reduce((sum, log) => sum + log.duration_minutes, 0);
      progress.average_rating = workoutLogs
        .filter(log => log.rating)
        .reduce((sum, log) => sum + log.rating, 0) / workoutLogs.filter(log => log.rating).length;

      // Calculate weekly progress
      const weeklyData = {};
      workoutLogs.forEach(log => {
        const week = log.workout.week;
        if (!weeklyData[week]) {
          weeklyData[week] = { workouts: 0, duration: 0, rating: 0 };
        }
        weeklyData[week].workouts++;
        weeklyData[week].duration += log.duration_minutes;
        if (log.rating) {
          weeklyData[week].rating += log.rating;
        }
      });

      progress.weekly_progress = Object.entries(weeklyData).map(([week, data]: [string, any]) => ({
        week: parseInt(week),
        workouts: data.workouts,
        duration: data.duration,
        average_rating: data.rating / data.workouts,
      }));

      // Calculate exercise progress
      const exerciseData = {};
      workoutLogs.forEach(log => {
        log.setLogs.forEach(setLog => {
          const exerciseId = setLog.workoutExercise.exercise.id;
          if (!exerciseData[exerciseId]) {
            exerciseData[exerciseId] = {
              name: setLog.workoutExercise.exercise.name,
              sets: 0,
              total_reps: 0,
              total_weight: 0,
              max_weight: 0,
            };
          }
          exerciseData[exerciseId].sets++;
          exerciseData[exerciseId].total_reps += setLog.reps;
          if (setLog.weight_kg) {
            exerciseData[exerciseId].total_weight += setLog.weight_kg;
            exerciseData[exerciseId].max_weight = Math.max(
              exerciseData[exerciseId].max_weight,
              setLog.weight_kg
            );
          }
        });
      });

      progress.exercise_progress = exerciseData;
    }

    return progress;
  }

  // Helper method to get user profile (would be injected from user service)
  private async getUserProfile(userId: string): Promise<any> {
    // This would typically come from a user service
    // For now, return a mock profile
    return {
      experience_level: 'intermediate',
      equipment_access: ['barbell', 'dumbbells', 'bench', 'pull_up_bar'],
      injuries: [],
    };
  }
}
