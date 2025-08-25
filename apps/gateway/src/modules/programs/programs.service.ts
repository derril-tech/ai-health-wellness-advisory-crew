import { Injectable, NotFoundException, BadRequestException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';

import { Program } from './entities/program.entity';
import { Adjustment } from './entities/adjustment.entity';
import { CreateProgramDto } from './dto/create-program.dto';
import { ActivateProgramDto } from './dto/activate-program.dto';

@Injectable()
export class ProgramsService {
  constructor(
    @InjectRepository(Program)
    private readonly programRepository: Repository<Program>,
    @InjectRepository(Adjustment)
    private readonly adjustmentRepository: Repository<Adjustment>,
  ) {}

  async createProgram(userId: string, createProgramDto: CreateProgramDto) {
    const program = this.programRepository.create({
      user_id: userId,
      profile_id: createProgramDto.profile_id,
      start_date: createProgramDto.start_date,
      end_date: createProgramDto.end_date,
      goal: createProgramDto.goal,
      strategy: createProgramDto.strategy,
      status: 'draft',
    });

    return await this.programRepository.save(program);
  }

  async activateProgram(userId: string, programId: string, activateProgramDto: ActivateProgramDto) {
    const program = await this.programRepository.findOne({
      where: { id: programId, user_id: userId },
    });

    if (!program) {
      throw new NotFoundException('Program not found');
    }

    if (program.status !== 'draft') {
      throw new BadRequestException('Program is not in draft status');
    }

    program.status = 'active';
    program.start_date = activateProgramDto.start_date;
    program.end_date = activateProgramDto.end_date;

    return await this.programRepository.save(program);
  }

  async getProgram(userId: string, programId: string) {
    const program = await this.programRepository.findOne({
      where: { id: programId, user_id: userId },
      relations: ['profile', 'adjustments'],
    });

    if (!program) {
      throw new NotFoundException('Program not found');
    }

    return program;
  }

  async getUserPrograms(userId: string) {
    return await this.programRepository.find({
      where: { user_id: userId },
      relations: ['profile'],
      order: { created_at: 'DESC' },
    });
  }

  async getAdjustments(userId: string, programId: string) {
    // Verify program belongs to user
    const program = await this.programRepository.findOne({
      where: { id: programId, user_id: userId },
    });

    if (!program) {
      throw new NotFoundException('Program not found');
    }

    return await this.adjustmentRepository.find({
      where: { program_id: programId },
      order: { week: 'ASC' },
    });
  }

  async getCurrentWeek(programId: string) {
    const program = await this.programRepository.findOne({
      where: { id: programId },
    });

    if (!program) {
      throw new NotFoundException('Program not found');
    }

    const startDate = new Date(program.start_date);
    const currentDate = new Date();
    const diffTime = currentDate.getTime() - startDate.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    const currentWeek = Math.floor(diffDays / 7) + 1;

    return {
      current_week: currentWeek,
      days_elapsed: diffDays,
      start_date: program.start_date,
      end_date: program.end_date,
    };
  }
}
