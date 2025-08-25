import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';

import { HealthProfile } from './entities/health-profile.entity';
import { IntakeQuestionnaire } from './entities/intake-questionnaire.entity';
import { SubmitIntakeDto } from './dto/submit-intake.dto';
import { SubmitClearanceDto } from './dto/submit-clearance.dto';

@Injectable()
export class HealthService {
  constructor(
    @InjectRepository(HealthProfile)
    private readonly healthProfileRepository: Repository<HealthProfile>,
    @InjectRepository(IntakeQuestionnaire)
    private readonly intakeQuestionnaireRepository: Repository<IntakeQuestionnaire>,
  ) {}

  async submitIntake(userId: string, submitIntakeDto: SubmitIntakeDto) {
    // Create intake questionnaire
    const questionnaire = this.intakeQuestionnaireRepository.create({
      user_id: userId,
      responses: submitIntakeDto.responses,
      status: 'pending',
    });

    const savedQuestionnaire = await this.intakeQuestionnaireRepository.save(questionnaire);

    // TODO: Trigger background task to normalize profile
    // This would call the orchestrator to process the questionnaire

    return {
      questionnaire_id: savedQuestionnaire.id,
      status: 'pending',
      message: 'Intake submitted successfully. Profile will be processed shortly.',
    };
  }

  async submitClearance(userId: string, submitClearanceDto: SubmitClearanceDto) {
    const profile = await this.healthProfileRepository.findOne({
      where: { user_id: userId },
    });

    if (!profile) {
      throw new NotFoundException('Health profile not found');
    }

    profile.cleared = submitClearanceDto.acknowledged;
    await this.healthProfileRepository.save(profile);

    return {
      cleared: profile.cleared,
      message: profile.cleared 
        ? 'You have been cleared to proceed with your program.'
        : 'You have not been cleared. Please consult with a healthcare provider.',
    };
  }

  async getProfile(userId: string) {
    const profile = await this.healthProfileRepository.findOne({
      where: { user_id: userId },
    });

    if (!profile) {
      throw new NotFoundException('Health profile not found');
    }

    return profile;
  }

  async getIntakeStatus(userId: string) {
    const questionnaire = await this.intakeQuestionnaireRepository.findOne({
      where: { user_id: userId },
      order: { created_at: 'DESC' },
      relations: ['normalized_profile'],
    });

    if (!questionnaire) {
      return { status: 'not_started' };
    }

    return {
      questionnaire_id: questionnaire.id,
      status: questionnaire.status,
      created_at: questionnaire.created_at,
      completed_at: questionnaire.completed_at,
      profile: questionnaire.normalized_profile,
    };
  }
}
