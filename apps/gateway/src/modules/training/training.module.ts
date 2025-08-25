import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';

import { TrainingController } from './training.controller';
import { TrainingService } from './training.service';
import { Exercise } from './entities/exercise.entity';
import { Workout } from './entities/workout.entity';
import { WorkoutLog } from './entities/workout-log.entity';
import { WorkoutExercise } from './entities/workout-exercise.entity';
import { SetLog } from './entities/set-log.entity';

@Module({
  imports: [TypeOrmModule.forFeature([Exercise, Workout, WorkoutLog, WorkoutExercise, SetLog])],
  controllers: [TrainingController],
  providers: [TrainingService],
  exports: [TrainingService],
})
export class TrainingModule {}
