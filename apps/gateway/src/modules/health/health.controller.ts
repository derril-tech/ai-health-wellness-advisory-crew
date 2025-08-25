import {
  Controller,
  Post,
  Get,
  Body,
  UseGuards,
  Request,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiBearerAuth } from '@nestjs/swagger';

import { HealthService } from './health.service';
import { SubmitIntakeDto } from './dto/submit-intake.dto';
import { SubmitClearanceDto } from './dto/submit-clearance.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';

@ApiTags('Health & Intake')
@Controller('health')
@UseGuards(JwtAuthGuard)
@ApiBearerAuth()
export class HealthController {
  constructor(private readonly healthService: HealthService) {}

  @Post('intake')
  @ApiOperation({ summary: 'Submit intake questionnaire' })
  @ApiResponse({ status: 201, description: 'Intake submitted successfully' })
  async submitIntake(@Request() req, @Body() submitIntakeDto: SubmitIntakeDto) {
    return this.healthService.submitIntake(req.user.id, submitIntakeDto);
  }

  @Post('clearance')
  @ApiOperation({ summary: 'Submit safety clearance acknowledgment' })
  @ApiResponse({ status: 200, description: 'Clearance status updated' })
  async submitClearance(@Request() req, @Body() submitClearanceDto: SubmitClearanceDto) {
    return this.healthService.submitClearance(req.user.id, submitClearanceDto);
  }

  @Get('profile')
  @ApiOperation({ summary: 'Get health profile' })
  @ApiResponse({ status: 200, description: 'Health profile retrieved' })
  async getProfile(@Request() req) {
    return this.healthService.getProfile(req.user.id);
  }

  @Get('intake/status')
  @ApiOperation({ summary: 'Get intake questionnaire status' })
  @ApiResponse({ status: 200, description: 'Intake status retrieved' })
  async getIntakeStatus(@Request() req) {
    return this.healthService.getIntakeStatus(req.user.id);
  }
}
