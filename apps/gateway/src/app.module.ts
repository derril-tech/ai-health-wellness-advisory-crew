import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ThrottlerModule } from '@nestjs/throttler';
import { TerminusModule } from '@nestjs/terminus';

// Auth module
import { AuthModule } from './modules/auth/auth.module';
import { User } from './modules/auth/entities/user.entity';
import { Organization } from './modules/auth/entities/organization.entity';

// Health module
import { HealthModule } from './modules/health/health.module';
import { HealthProfile } from './modules/health/entities/health-profile.entity';
import { IntakeQuestionnaire } from './modules/health/entities/intake-questionnaire.entity';

// Programs module
import { ProgramsModule } from './modules/programs/programs.module';
import { Program } from './modules/programs/entities/program.entity';
import { Adjustment } from './modules/programs/entities/adjustment.entity';

// Nutrition module
import { NutritionModule } from './modules/nutrition/nutrition.module';
import { MacroTargets } from './modules/nutrition/entities/macro-targets.entity';
import { MealPlan } from './modules/nutrition/entities/meal-plan.entity';
import { Food } from './modules/nutrition/entities/food.entity';

// Training module
import { TrainingModule } from './modules/training/training.module';
import { Exercise } from './modules/training/entities/exercise.entity';
import { Workout } from './modules/training/entities/workout.entity';
import { WorkoutLog } from './modules/training/entities/workout-log.entity';
import { WorkoutExercise } from './modules/training/entities/workout-exercise.entity';
import { SetLog } from './modules/training/entities/set-log.entity';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: ['.env.local', '.env'],
    }),
    TypeOrmModule.forRoot({
      type: 'postgres',
      host: process.env.DB_HOST || 'localhost',
      port: parseInt(process.env.DB_PORT) || 5432,
      username: process.env.DB_USERNAME || 'postgres',
      password: process.env.DB_PASSWORD || 'postgres',
      database: process.env.DB_NAME || 'health_crew',
      entities: [
        User,
        Organization,
        HealthProfile,
        IntakeQuestionnaire,
        Program,
        Adjustment,
        MacroTargets,
        MealPlan,
        Food,
        Exercise,
        Workout,
        WorkoutLog,
        WorkoutExercise,
        SetLog,
      ],
      synchronize: process.env.NODE_ENV !== 'production',
      logging: process.env.NODE_ENV === 'development',
      ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
    }),
    ThrottlerModule.forRoot([
      {
        ttl: 60000,
        limit: 100,
      },
    ]),
    TerminusModule,
    
    // Feature modules
    AuthModule,
    HealthModule,
    ProgramsModule,
    NutritionModule,
    TrainingModule,
  ],
  controllers: [],
  providers: [],
})
export class AppModule {}
