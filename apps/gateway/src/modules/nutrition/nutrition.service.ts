import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';

import { MacroTargets } from './entities/macro-targets.entity';
import { MealPlan } from './entities/meal-plan.entity';
import { Food } from './entities/food.entity';
import { Program } from '../programs/entities/program.entity';

@Injectable()
export class NutritionService {
  constructor(
    @InjectRepository(MacroTargets)
    private readonly macroTargetsRepository: Repository<MacroTargets>,
    @InjectRepository(MealPlan)
    private readonly mealPlanRepository: Repository<MealPlan>,
    @InjectRepository(Food)
    private readonly foodRepository: Repository<Food>,
    @InjectRepository(Program)
    private readonly programRepository: Repository<Program>,
  ) {}

  async getMacros(userId: string, programId: string, week: number) {
    // Verify program belongs to user
    const program = await this.programRepository.findOne({
      where: { id: programId, user_id: userId },
    });

    if (!program) {
      throw new NotFoundException('Program not found');
    }

    const macros = await this.macroTargetsRepository.findOne({
      where: { program_id: programId, week },
    });

    if (!macros) {
      throw new NotFoundException('Macro targets not found for this week');
    }

    return macros;
  }

  async getMealPlans(userId: string, programId: string, week: number, day?: number) {
    // Verify program belongs to user
    const program = await this.programRepository.findOne({
      where: { id: programId, user_id: userId },
    });

    if (!program) {
      throw new NotFoundException('Program not found');
    }

    const query = this.mealPlanRepository.createQueryBuilder('meal_plan')
      .where('meal_plan.program_id = :programId', { programId })
      .andWhere('meal_plan.week = :week', { week });

    if (day !== undefined) {
      query.andWhere('meal_plan.day_of_week = :day', { day });
    }

    return await query.getMany();
  }

  async searchFoods(query: string, limit: number = 10) {
    return await this.foodRepository
      .createQueryBuilder('food')
      .where('food.name ILIKE :query', { query: `%${query}%` })
      .limit(limit)
      .getMany();
  }

  async getFoodById(foodId: string) {
    const food = await this.foodRepository.findOne({
      where: { id: foodId },
    });

    if (!food) {
      throw new NotFoundException('Food not found');
    }

    return food;
  }

  async findSimilarFoods(foodId: string, limit: number = 5) {
    const food = await this.getFoodById(foodId);

    if (!food.embedding) {
      return [];
    }

    // Use vector similarity search
    return await this.foodRepository
      .createQueryBuilder('food')
      .where('food.id != :foodId', { foodId })
      .andWhere('food.embedding IS NOT NULL')
      .orderBy(`food.embedding <-> :embedding`, 'ASC')
      .setParameter('embedding', food.embedding)
      .limit(limit)
      .getMany();
  }

  async calculateMacroDeltas(food1Id: string, food2Id: string, servingSize: number) {
    const food1 = await this.getFoodById(food1Id);
    const food2 = await this.getFoodById(food2Id);

    const calculateMacros = (food: Food, serving: number) => ({
      kcal: (food.kcal_per_100g * serving) / 100,
      protein_g: (food.protein_g_per_100g * serving) / 100,
      carbs_g: (food.carbs_g_per_100g * serving) / 100,
      fat_g: (food.fat_g_per_100g * serving) / 100,
    });

    const macros1 = calculateMacros(food1, servingSize);
    const macros2 = calculateMacros(food2, servingSize);

    return {
      kcal_delta: macros2.kcal - macros1.kcal,
      protein_g_delta: macros2.protein_g - macros1.protein_g,
      carbs_g_delta: macros2.carbs_g - macros1.carbs_g,
      fat_g_delta: macros2.fat_g - macros1.fat_g,
    };
  }
}
