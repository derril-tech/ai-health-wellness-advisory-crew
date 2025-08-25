import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  ManyToOne,
  JoinColumn,
} from 'typeorm';
import { User } from '../../auth/entities/user.entity';
import { HealthProfile } from './health-profile.entity';

@Entity('intake_questionnaires', { schema: 'health' })
export class IntakeQuestionnaire {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column()
  user_id: string;

  @Column({ type: 'jsonb' })
  responses: Record<string, any>;

  @Column({ nullable: true })
  normalized_profile_id: string;

  @Column({ default: 'pending' })
  status: string;

  @CreateDateColumn()
  created_at: Date;

  @Column({ nullable: true })
  completed_at: Date;

  @ManyToOne(() => User, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'user_id' })
  user: User;

  @ManyToOne(() => HealthProfile, { nullable: true })
  @JoinColumn({ name: 'normalized_profile_id' })
  normalized_profile: HealthProfile;
}
