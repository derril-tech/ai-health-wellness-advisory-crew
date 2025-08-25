import {
  Controller,
  Get,
  Query,
  Param,
  UseGuards,
  Request,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiBearerAuth, ApiParam, ApiQuery } from '@nestjs/swagger';

import { NutritionService } from './nutrition.service';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';

@ApiTags('Nutrition')
@Controller('nutrition')
@UseGuards(JwtAuthGuard)
@ApiBearerAuth()
export class NutritionController {
  constructor(private readonly nutritionService: NutritionService) {}

  @Get('programs/:programId/macros')
  @ApiOperation({ summary: 'Get macro targets for a program week' })
  @ApiParam({ name: 'programId', description: 'Program ID' })
  @ApiQuery({ name: 'week', description: 'Week number', type: Number })
  @ApiResponse({ status: 200, description: 'Macro targets retrieved' })
  async getMacros(
    @Request() req,
    @Param('programId') programId: string,
    @Query('week') week: number,
  ) {
    return this.nutritionService.getMacros(req.user.id, programId, week);
  }

  @Get('programs/:programId/meal-plans')
  @ApiOperation({ summary: 'Get meal plans for a program week' })
  @ApiParam({ name: 'programId', description: 'Program ID' })
  @ApiQuery({ name: 'week', description: 'Week number', type: Number })
  @ApiQuery({ name: 'day', description: 'Day of week (optional)', type: Number, required: false })
  @ApiResponse({ status: 200, description: 'Meal plans retrieved' })
  async getMealPlans(
    @Request() req,
    @Param('programId') programId: string,
    @Query('week') week: number,
    @Query('day') day?: number,
  ) {
    return this.nutritionService.getMealPlans(req.user.id, programId, week, day);
  }

  @Get('foods/search')
  @ApiOperation({ summary: 'Search foods by name' })
  @ApiQuery({ name: 'q', description: 'Search query' })
  @ApiQuery({ name: 'limit', description: 'Maximum results', type: Number, required: false })
  @ApiResponse({ status: 200, description: 'Food search results' })
  async searchFoods(
    @Query('q') query: string,
    @Query('limit') limit: number = 10,
  ) {
    return this.nutritionService.searchFoods(query, limit);
  }

  @Get('foods/:foodId')
  @ApiOperation({ summary: 'Get food details by ID' })
  @ApiParam({ name: 'foodId', description: 'Food ID' })
  @ApiResponse({ status: 200, description: 'Food details retrieved' })
  async getFoodById(@Param('foodId') foodId: string) {
    return this.nutritionService.getFoodById(foodId);
  }

  @Get('foods/:foodId/similar')
  @ApiOperation({ summary: 'Find similar foods using vector embeddings' })
  @ApiParam({ name: 'foodId', description: 'Food ID' })
  @ApiQuery({ name: 'limit', description: 'Maximum results', type: Number, required: false })
  @ApiResponse({ status: 200, description: 'Similar foods found' })
  async findSimilarFoods(
    @Param('foodId') foodId: string,
    @Query('limit') limit: number = 5,
  ) {
    return this.nutritionService.findSimilarFoods(foodId, limit);
  }

  @Get('foods/compare')
  @ApiOperation({ summary: 'Calculate macro differences between two foods' })
  @ApiQuery({ name: 'food1', description: 'First food ID' })
  @ApiQuery({ name: 'food2', description: 'Second food ID' })
  @ApiQuery({ name: 'serving', description: 'Serving size in grams', type: Number })
  @ApiResponse({ status: 200, description: 'Macro differences calculated' })
  async calculateMacroDeltas(
    @Query('food1') food1Id: string,
    @Query('food2') food2Id: string,
    @Query('serving') servingSize: number,
  ) {
    return this.nutritionService.calculateMacroDeltas(food1Id, food2Id, servingSize);
  }
}
