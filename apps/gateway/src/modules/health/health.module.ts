import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';

import { HealthController } from './health.controller';
import { HealthService } from './health.service';
import { HealthProfile } from './entities/health-profile.entity';
import { IntakeQuestionnaire } from './entities/intake-questionnaire.entity';

@Module({
  imports: [TypeOrmModule.forFeature([HealthProfile, IntakeQuestionnaire])],
  controllers: [HealthController],
  providers: [HealthService],
  exports: [HealthService],
})
export class HealthModule {}
