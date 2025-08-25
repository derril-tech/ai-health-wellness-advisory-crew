import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  ManyToOne,
  JoinColumn,
  OneToMany,
} from 'typeorm';
import { Program } from '../../programs/entities/program.entity';
import { WorkoutExercise } from './workout-exercise.entity';

@Entity('workouts', { schema: 'training' })
export class Workout {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column()
  program_id: string;

  @Column()
  name: string;

  @Column()
  day_of_week: number;

  @Column()
  week: number;

  @Column()
  estimated_duration_min: number;

  @Column()
  difficulty: string;

  @Column({ type: 'text', nullable: true })
  notes: string;

  @Column({ default: 'scheduled' })
  status: string; // scheduled, in_progress, completed, skipped

  @CreateDateColumn()
  created_at: Date;

  @UpdateDateColumn()
  updated_at: Date;

  @ManyToOne(() => Program, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'program_id' })
  program: Program;

  @OneToMany(() => WorkoutExercise, (exercise) => exercise.workout)
  exercises: WorkoutExercise[];
}
