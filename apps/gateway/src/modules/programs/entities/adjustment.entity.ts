import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  ManyToOne,
  JoinColumn,
} from 'typeorm';
import { Program } from './program.entity';

@Entity('adjustments', { schema: 'programs' })
export class Adjustment {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column()
  program_id: string;

  @Column()
  week: number;

  @Column({ default: 0 })
  kcal_delta: number;

  @Column({ type: 'decimal', precision: 5, scale: 2, default: 0 })
  volume_delta: number;

  @Column({ default: false })
  deload: boolean;

  @Column({ type: 'jsonb', nullable: true })
  habit_changes: Record<string, any>;

  @Column({ nullable: true })
  rationale: string;

  @CreateDateColumn()
  created_at: Date;

  @ManyToOne(() => Program, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'program_id' })
  program: Program;
}
