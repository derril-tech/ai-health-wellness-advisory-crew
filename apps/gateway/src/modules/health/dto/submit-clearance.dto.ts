import { IsBoolean } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class SubmitClearanceDto {
  @ApiProperty({
    description: 'Whether the user acknowledges the safety warnings',
    example: true,
  })
  @IsBoolean()
  acknowledged: boolean;
}
