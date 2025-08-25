import { IsDateString } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class ActivateProgramDto {
  @ApiProperty({ description: 'Program start date', example: '2024-01-01' })
  @IsDateString()
  start_date: string;

  @ApiProperty({ description: 'Program end date', example: '2024-03-25' })
  @IsDateString()
  end_date: string;
}
