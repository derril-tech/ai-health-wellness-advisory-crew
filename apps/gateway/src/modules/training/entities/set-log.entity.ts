import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  ManyToOne,
  JoinColumn,
} from 'typeorm';
import { WorkoutLog } from './workout-log.entity';
import { WorkoutExercise } from './workout-exercise.entity';

@Entity('set_logs', { schema: 'training' })
export class SetLog {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column()
  workout_log_id: string;

  @Column()
  workout_exercise_id: string;

  @Column()
  set_number: number;

  @Column()
  reps: number;

  @Column({ type: 'decimal', precision: 5, scale: 2, nullable: true })
  weight_kg: number;

  @Column({ nullable: true })
  rpe: number; // Rate of Perceived Exertion (1-10)

  @Column({ default: false })
  completed: boolean;

  @Column({ type: 'text', nullable: true })
  notes: string;

  @Column({ type: 'timestamp' })
  performed_at: Date;

  @CreateDateColumn()
  created_at: Date;

  @ManyToOne(() => WorkoutLog, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'workout_log_id' })
  workout_log: WorkoutLog;

  @ManyToOne(() => WorkoutExercise, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'workout_exercise_id' })
  workout_exercise: WorkoutExercise;
}
