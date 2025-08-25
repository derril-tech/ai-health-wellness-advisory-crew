import {
  Controller,
  Post,
  Get,
  Body,
  Param,
  UseGuards,
  Request,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiBearerAuth, ApiParam } from '@nestjs/swagger';

import { ProgramsService } from './programs.service';
import { CreateProgramDto } from './dto/create-program.dto';
import { ActivateProgramDto } from './dto/activate-program.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';

@ApiTags('Programs')
@Controller('programs')
@UseGuards(JwtAuthGuard)
@ApiBearerAuth()
export class ProgramsController {
  constructor(private readonly programsService: ProgramsService) {}

  @Post()
  @ApiOperation({ summary: 'Create a new program' })
  @ApiResponse({ status: 201, description: 'Program created successfully' })
  async createProgram(@Request() req, @Body() createProgramDto: CreateProgramDto) {
    return this.programsService.createProgram(req.user.id, createProgramDto);
  }

  @Post(':id/activate')
  @ApiOperation({ summary: 'Activate a program' })
  @ApiParam({ name: 'id', description: 'Program ID' })
  @ApiResponse({ status: 200, description: 'Program activated successfully' })
  async activateProgram(
    @Request() req,
    @Param('id') programId: string,
    @Body() activateProgramDto: ActivateProgramDto,
  ) {
    return this.programsService.activateProgram(req.user.id, programId, activateProgramDto);
  }

  @Get()
  @ApiOperation({ summary: 'Get user programs' })
  @ApiResponse({ status: 200, description: 'Programs retrieved successfully' })
  async getUserPrograms(@Request() req) {
    return this.programsService.getUserPrograms(req.user.id);
  }

  @Get(':id')
  @ApiOperation({ summary: 'Get program details' })
  @ApiParam({ name: 'id', description: 'Program ID' })
  @ApiResponse({ status: 200, description: 'Program details retrieved' })
  async getProgram(@Request() req, @Param('id') programId: string) {
    return this.programsService.getProgram(req.user.id, programId);
  }

  @Get(':id/adjustments')
  @ApiOperation({ summary: 'Get program adjustments' })
  @ApiParam({ name: 'id', description: 'Program ID' })
  @ApiResponse({ status: 200, description: 'Adjustments retrieved successfully' })
  async getAdjustments(@Request() req, @Param('id') programId: string) {
    return this.programsService.getAdjustments(req.user.id, programId);
  }

  @Get(':id/current-week')
  @ApiOperation({ summary: 'Get current week of program' })
  @ApiParam({ name: 'id', description: 'Program ID' })
  @ApiResponse({ status: 200, description: 'Current week calculated' })
  async getCurrentWeek(@Param('id') programId: string) {
    return this.programsService.getCurrentWeek(programId);
  }
}
