import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  ManyToOne,
  JoinColumn,
} from 'typeorm';
import { Program } from '../../programs/entities/program.entity';

@Entity('macro_targets', { schema: 'nutrition' })
export class MacroTargets {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column()
  program_id: string;

  @Column()
  week: number;

  @Column({ nullable: true })
  day_of_week: number;

  @Column()
  kcal: number;

  @Column()
  protein_g: number;

  @Column()
  carbs_g: number;

  @Column()
  fat_g: number;

  @Column()
  fiber_g: number;

  @Column()
  sodium_mg: number;

  @Column()
  water_ml: number;

  @Column({ default: false })
  refeed: boolean;

  @CreateDateColumn()
  created_at: Date;

  @ManyToOne(() => Program, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'program_id' })
  program: Program;
}
