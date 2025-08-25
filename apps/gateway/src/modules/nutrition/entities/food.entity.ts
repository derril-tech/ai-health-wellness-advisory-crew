import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
} from 'typeorm';

@Entity('foods', { schema: 'nutrition' })
export class Food {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column()
  name: string;

  @Column({ nullable: true })
  brand: string;

  @Column({ type: 'decimal', precision: 8, scale: 2, nullable: true })
  serving_size_g: number;

  @Column()
  kcal_per_100g: number;

  @Column({ type: 'decimal', precision: 5, scale: 2 })
  protein_g_per_100g: number;

  @Column({ type: 'decimal', precision: 5, scale: 2 })
  carbs_g_per_100g: number;

  @Column({ type: 'decimal', precision: 5, scale: 2 })
  fat_g_per_100g: number;

  @Column({ type: 'decimal', precision: 5, scale: 2, nullable: true })
  fiber_g_per_100g: number;

  @Column({ nullable: true })
  sodium_mg_per_100g: number;

  @Column({ type: 'text', array: true, default: [] })
  allergens: string[];

  @Column({ type: 'vector', dimension: 1536, nullable: true })
  embedding: number[];

  @CreateDateColumn()
  created_at: Date;
}
