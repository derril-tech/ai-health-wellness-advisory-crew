import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  ManyToOne,
  JoinColumn,
} from 'typeorm';
import { User } from '../../auth/entities/user.entity';

@Entity('profiles', { schema: 'health' })
export class HealthProfile {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column()
  user_id: string;

  @Column({ nullable: true })
  height_cm: number;

  @Column({ type: 'decimal', precision: 5, scale: 2, nullable: true })
  weight_kg: number;

  @Column({ nullable: true })
  age: number;

  @Column({ nullable: true })
  sex_at_birth: string;

  @Column({ nullable: true })
  activity_level: string;

  @Column({ nullable: true })
  goal: string;

  @Column({ nullable: true })
  experience_level: string;

  @Column({ type: 'text', array: true, default: [] })
  equipment_access: string[];

  @Column({ type: 'text', array: true, default: [] })
  allergies: string[];

  @Column({ type: 'jsonb', array: true, default: [] })
  injuries: any[];

  @Column({ type: 'jsonb', array: true, default: [] })
  medications: any[];

  @Column({ type: 'text', array: true, default: [] })
  parq_flags: string[];

  @Column({ default: 'low' })
  risk_level: string;

  @Column({ default: false })
  cleared: boolean;

  @CreateDateColumn()
  created_at: Date;

  @UpdateDateColumn()
  updated_at: Date;

  @ManyToOne(() => User, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'user_id' })
  user: User;
}
