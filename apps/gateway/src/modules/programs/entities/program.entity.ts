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
import { User } from '../../auth/entities/user.entity';
import { HealthProfile } from '../../health/entities/health-profile.entity';
import { Adjustment } from './adjustment.entity';

@Entity('programs', { schema: 'programs' })
export class Program {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column()
  user_id: string;

  @Column()
  profile_id: string;

  @Column({ type: 'date' })
  start_date: Date;

  @Column({ type: 'date' })
  end_date: Date;

  @Column({ default: 'draft' })
  status: string;

  @Column({ type: 'jsonb' })
  goal: Record<string, any>;

  @Column({ type: 'jsonb', nullable: true })
  strategy: Record<string, any>;

  @CreateDateColumn()
  created_at: Date;

  @UpdateDateColumn()
  updated_at: Date;

  @ManyToOne(() => User, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'user_id' })
  user: User;

  @ManyToOne(() => HealthProfile, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'profile_id' })
  profile: HealthProfile;

  @OneToMany(() => Adjustment, (adjustment) => adjustment.program)
  adjustments: Adjustment[];
}
