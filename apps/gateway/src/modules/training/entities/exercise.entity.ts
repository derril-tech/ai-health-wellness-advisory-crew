import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
} from 'typeorm';

@Entity('exercises', { schema: 'training' })
export class Exercise {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column()
  name: string;

  @Column()
  category: string; // compound, isolation, cardio

  @Column({ type: 'text', array: true })
  muscle_groups: string[];

  @Column({ type: 'text', array: true })
  equipment: string[];

  @Column()
  difficulty: string; // beginner, intermediate, advanced

  @Column({ type: 'text', array: true, default: [] })
  contraindications: string[];

  @Column({ type: 'text', array: true, default: [] })
  progressions: string[];

  @Column({ type: 'text', array: true, default: [] })
  regressions: string[];

  @Column({ nullable: true })
  video_url: string;

  @Column({ type: 'text', nullable: true })
  description: string;

  @Column({ type: 'text', nullable: true })
  instructions: string;

  @Column({ type: 'text', nullable: true })
  tips: string;

  @CreateDateColumn()
  created_at: Date;

  @UpdateDateColumn()
  updated_at: Date;
}
