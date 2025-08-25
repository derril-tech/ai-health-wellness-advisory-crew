import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  ManyToOne,
  JoinColumn,
} from 'typeorm';
import { Program } from '../../programs/entities/program.entity';

@Entity('meal_plans', { schema: 'nutrition' })
export class MealPlan {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column()
  program_id: string;

  @Column()
  week: number;

  @Column()
  day_of_week: number;

  @Column()
  meal_type: string;

  @Column({ type: 'jsonb' })
  meals: Record<string, any>;

  @Column()
  total_kcal: number;

  @Column()
  total_protein_g: number;

  @Column()
  total_carbs_g: number;

  @Column()
  total_fat_g: number;

  @CreateDateColumn()
  created_at: Date;

  @ManyToOne(() => Program, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'program_id' })
  program: Program;
}
