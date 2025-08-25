import { IsString, IsObject, IsDateString, IsOptional } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class CreateProgramDto {
  @ApiProperty({ description: 'Health profile ID' })
  @IsString()
  profile_id: string;

  @ApiProperty({ description: 'Program start date', example: '2024-01-01' })
  @IsDateString()
  start_date: string;

  @ApiProperty({ description: 'Program end date', example: '2024-03-25' })
  @IsDateString()
  end_date: string;

  @ApiProperty({
    description: 'Program goal',
    example: {
      type: 'weight_loss',
      target_weight: 65,
      timeline_weeks: 12,
    },
  })
  @IsObject()
  goal: Record<string, any>;

  @ApiProperty({
    description: 'Program strategy (optional)',
    example: {
      nutrition_approach: 'flexible_dieting',
      training_split: 'upper_lower',
      cardio_frequency: 3,
    },
    required: false,
  })
  @IsOptional()
  @IsObject()
  strategy?: Record<string, any>;
}
