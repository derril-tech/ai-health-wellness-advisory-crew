import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';

import { NutritionController } from './nutrition.controller';
import { NutritionService } from './nutrition.service';
import { MacroTargets } from './entities/macro-targets.entity';
import { MealPlan } from './entities/meal-plan.entity';
import { Food } from './entities/food.entity';

@Module({
  imports: [TypeOrmModule.forFeature([MacroTargets, MealPlan, Food])],
  controllers: [NutritionController],
  providers: [NutritionService],
  exports: [NutritionService],
})
export class NutritionModule {}
