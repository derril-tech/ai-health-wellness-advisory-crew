import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  ManyToOne,
  JoinColumn,
  OneToMany,
} from 'typeorm';
import { Workout } from './workout.entity';
import { Exercise } from './exercise.entity';
import { SetLog } from './set-log.entity';

@Entity('workout_exercises', { schema: 'training' })
export class WorkoutExercise {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column()
  workout_id: string;

  @Column()
  exercise_id: string;

  @Column()
  order: number;

  @Column()
  sets: number;

  @Column()
  reps: number;

  @Column({ type: 'decimal', precision: 5, scale: 2, nullable: true })
  weight_kg: number;

  @Column({ nullable: true })
  rpe: number; // Rate of Perceived Exertion (1-10)

  @Column()
  rest_seconds: number;

  @Column({ type: 'text', nullable: true })
  notes: string;

  @CreateDateColumn()
  created_at: Date;

  @ManyToOne(() => Workout, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'workout_id' })
  workout: Workout;

  @ManyToOne(() => Exercise, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'exercise_id' })
  exercise: Exercise;

  @OneToMany(() => SetLog, (setLog) => setLog.workout_exercise)
  set_logs: SetLog[];
}
