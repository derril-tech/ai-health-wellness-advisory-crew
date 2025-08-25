import { IsObject, IsNotEmpty } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class SubmitIntakeDto {
  @ApiProperty({
    description: 'Questionnaire responses',
    example: {
      height_cm: 175,
      weight_kg: 70,
      age: 30,
      sex_at_birth: 'male',
      activity_level: 'moderate',
      goal: 'lose_weight',
      experience_level: 'intermediate',
      equipment_access: ['dumbbells', 'resistance_bands'],
      allergies: ['nuts'],
      injuries: [],
      medications: [],
    },
  })
  @IsObject()
  @IsNotEmpty()
  responses: Record<string, any>;
}
